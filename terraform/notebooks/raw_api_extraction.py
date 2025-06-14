# 1. EXTRAÇÃO DOS API'S SALES_ORDER_HEADER, PURCHASE_ORDER_DETAIL, PURCHASE_ORDER_HEADER E SALES_ORDER_DETAIL
# ==========================X=======================

import requests
from requests.auth import HTTPBasicAuth
from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Spark otimizado
spark = SparkSession.builder \
    .appName("LargeAPIExtraction") \
    .config("spark.sql.shuffle.partitions", "8") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

dbutils = DBUtils(spark)

# Função de extração recursiva com divisão em blocos menores em caso de falha
def fetch_data_recursive(endpoint, auth, offset, limit, max_retries=3, min_limit=100):
    base_url = "http://18.209.218.63:8080"
    url = f"{base_url}{endpoint}"

    for attempt in range(max_retries):
        try:
            print(f" Offset {offset} | Limit {limit} | Tentativa {attempt + 1}")
            response = requests.get(
                url,
                auth=auth,
                params={"offset": offset, "limit": limit},
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("data"):
                return []
            return data["data"]
        except Exception as e:
            print(f" Erro no offset {offset}, tentativa {attempt + 1}: {str(e)}")
            time.sleep(2 ** attempt)

    # Se falhar, tenta dividir o bloco
    if limit > min_limit:
        print(f" Dividindo bloco de offset {offset} | Limit {limit}")
        mid = limit // 2
        first_half = fetch_data_recursive(endpoint, auth, offset, mid, max_retries, min_limit)
        second_half = fetch_data_recursive(endpoint, auth, offset + mid, limit - mid, max_retries, min_limit)
        return first_half + second_half
    else:
        print(f" Falha crítica em offset {offset} mesmo com limite mínimo ({min_limit}).")
        return []

# Função principal de paginação
def fetch_paginated_data(endpoint, auth, initial_limit=150000):
    offset = 0
    all_data = []

    while True:
        records = fetch_data_recursive(endpoint, auth, offset, initial_limit)
        if not records:
            break
        all_data.extend(records)
        print(f" Offset {offset}: +{len(records)} registros (Total acumulado: {len(all_data)})")
        if len(records) < initial_limit:
            break
        offset += initial_limit

    return all_data

# Processamento e gravação Delta
def process_endpoint(table_suffix, endpoint, auth, schema):
    try:
        print(f"\n🔄 Iniciando extração para {table_suffix}...\n")
        
        data = fetch_paginated_data(endpoint, auth)
        
        if not data:
            print(f"⚠️ Nenhum dado retornado para {table_suffix}")
            return
            
        pdf = pd.DataFrame(data)
        sdf = spark.createDataFrame(pdf)
        
        tabela_destino = f"{schema}.raw_api_{table_suffix}"
        
        sdf.write \
            .mode("overwrite") \
            .format("delta") \
            .option("mergeSchema", "true") \
            .option("overwriteSchema", "true") \
            .option("optimizeWrite", "true") \
            .saveAsTable(tabela_destino)
        
        df_check = spark.read.table(tabela_destino)
        print(f"✅ Concluído: {tabela_destino} com {df_check.count()} registros")
        df_check.printSchema()
        
    except Exception as e:
        print(f"❌ Falha crítica no processamento de {table_suffix}: {str(e)}")
        raise

# Configuração de autenticação
auth = HTTPBasicAuth(
    dbutils.secrets.get(scope="sqlserver_scope", key="api_user"),
    dbutils.secrets.get(scope="sqlserver_scope", key="api_pass")
)

# Endpoint específico
endpoints = {
    "sales_order_detail": "/SalesOrderDetail",
    "sales_order_header": "/SalesOrderHeader",
    "purchase_order_detail": "/PurchaseOrderDetail",
    "purchase_order_header": "/PurchaseOrderHeader"
}

schema = "ted_dev.dev_andre_silva"

# Execução com ThreadPool (mesmo que tenha 1 endpoint, deixa pronto pra escalar)
max_workers = 2

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {
        executor.submit(
            process_endpoint,
            table_suffix,
            endpoint,
            auth,
            schema
        ): table_suffix for table_suffix, endpoint in endpoints.items()
    }
    
    for future in as_completed(futures):
        table_suffix = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f"❗ Erro não tratado em {table_suffix}: {str(e)}")

# COMMAND ----------

# 2. Verificar se o count() bate com o esperado (TESTE DE VALIDAÇÃO)
# ================================X=================================
for table in ["sales_order_detail", "sales_order_header", "purchase_order_detail", "purchase_order_header"]:
    df = spark.table(f"ted_dev.dev_andre_silva.raw_api_{table}")
    print(f"{table}: {df.count():,} registros")