## Importa as bibliotecas necessárias: SparkSession para trabalhar com Spark (extração dos dados) e DBUtils para trabalhar com variáveis sensíveis (variável de ambiente):
from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils

spark = SparkSession.builder.appName("RawExtraction").getOrCreate()
dbutils = DBUtils(spark) #Inicializa o utilitário DBUtils para acessar os secrets armazenados

## Adicionando as credenciais do Secret Scope:
jdbc_hostname = dbutils.secrets.get(scope="sqlserver_scope", key="sql_host")
jdbc_port = dbutils.secrets.get(scope="sqlserver_scope", key="sql_port")
jdbc_user = dbutils.secrets.get(scope="sqlserver_scope", key="sql_user")
jdbc_password = dbutils.secrets.get(scope="sqlserver_scope", key="sql_password")

## Recuperando de forma segura as credenciais de conexão do SQL Server que foram armazenadas no Secret Scope:
jdbc_url = f"jdbc:sqlserver://{jdbc_hostname}:{jdbc_port};databaseName=AdventureWorks;encrypt=false;trustServerCertificate=true"

connection_properties = {
    "user": jdbc_user,
    "password": jdbc_password,
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}
## Lista de tabelas a extrair com Formato (nome_tabela, schema_sql_server):
tabelas_sql_server = [
    ("CreditCard", "Sales"),
    ("Customer", "Sales"),
    ("SalesOrderDetail", "Sales"),
    ("SalesOrderHeader", "Sales"),
    ("SalesOrderHeaderSalesReason", "Sales"),
    ("SalesPerson", "Sales"),
    ("SalesReason", "Sales"),
    ("SalesTerritory", "Sales"),
    ("Address", "Person"),
    ("BusinessEntity", "Person"),
    ("CountryRegion", "Person"),
    ("Person", "Person"),
    ("StateProvince", "Person"),
    ("Employee", "HumanResources"),
    ("Product", "Production"),
    ("ProductCategory", "Production"),
    ("ProductSubcategory", "Production"),
]

## Parâmetros de paginação com tamanho de 1M:
pagina_tamanho = 1_000_000

## monta o nome das tabelas de origem e destino:
for nome_tabela, schema in tabelas_sql_server:
    tabela_fonte = f"{schema}.{nome_tabela}"
    tabela_destino = f"raw_{nome_tabela}"
    print(f"Extraindo: {tabela_fonte}")

    ## Obtem número total de linhas:
    count_query = f"(SELECT COUNT(*) as total FROM {tabela_fonte}) AS count_table"
    total_rows = spark.read.jdbc(
        url=jdbc_url,
        table=count_query,
        properties=connection_properties
    ).collect()[0]["total"]

    if total_rows <= pagina_tamanho:
        print(f"Tabela pequena ({total_rows} linhas) — extraindo de uma vez.")
        df = spark.read.jdbc(
            url=jdbc_url,
            table=tabela_fonte,
            properties=connection_properties
        )
        df.write.mode("overwrite").format("delta").saveAsTable(f"ted_dev.dev_andre_silva.{tabela_destino}")
    else:
        print(f"Tabela grande ({total_rows} linhas) — extraindo em páginas.")
        num_pages = (total_rows // pagina_tamanho) + int(total_rows % pagina_tamanho != 0)

        for i in range(num_pages):
            offset = i * pagina_tamanho
            print(f"   ➤ Página {i+1}/{num_pages} (OFFSET {offset})")
            paged_query = f"(SELECT * FROM {tabela_fonte} ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {pagina_tamanho} ROWS ONLY) AS paged_table"

            df_page = spark.read.jdbc(
                url=jdbc_url,
                table=paged_query,
                properties=connection_properties
            )

            df_page.write.mode("append").format("delta").saveAsTable(f"ted_dev.dev_andre_silva.{tabela_destino}")

print("Extração concluída com sucesso.")
