---

## Estrutura do Projeto

- **terraform/**: Scripts Terraform para provisionamento e upload dos notebooks no Databricks.
- **raw_api_extraction.py**: Notebook Python para extração de dados de uma API.
- **raw_mysql_extraction.py**: Notebook Python para extração de dados de um banco MySQL.
- **.env**: Arquivo com variáveis sensíveis (não versionado).
- **Dockerfile / docker-compose.yml**: Containerização para execução padronizada.
- **set_env.sh**: Script para exportar variáveis do `.env` no formato que o Terraform reconhece.

---
```mermaid
fluxograma TD
    A[Preencher .env] --> B[Executar Docker Compose]
    B --> C[Container inicia set_env.sh]
    C --> D[Exporta variáveis TF_VAR_]
    D --> E[Terraform init/apply]
    E --> F[Upload dos notebooks para Databricks]
    F --> G[Notebooks disponíveis para execução]
    G --> H[Executar os Notebooks no Databricks]
```
## Como Funciona

1. **Configuração das variáveis sensíveis**  
   Preencha o arquivo `.env` com as informações necessárias (host, token, email, etc).
   O arquivo .env.exemplo mostra o exemplo de como as credenciais devem ser preenchidas.

2. **Execução do Script de Ambiente**  
   O script `set_env.sh` carrega as variáveis do `.env` e exporta com prefixo `TF_VAR_`, permitindo que o Terraform as utilize diretamente.

3. **Provisionamento com Terraform**  
   O `main.tf` faz o upload dos notebooks para o Databricks, utilizando as variáveis de ambiente.

4. **Execução via Docker**  
   O Dockerfile e o docker-compose garantem que todo o processo rode de forma idêntica em qualquer máquina.

---

## Explicação dos Notebooks

### `raw_api_extraction.py`

Este notebook realiza a extração de dados de uma API externa. O fluxo típico é:
- Realizar requisições HTTP para uma API.
- Processar os dados recebidos (por exemplo, converter JSON em DataFrame).
- Salvar os dados em um formato adequado (como Parquet ou Delta) para uso posterior no Databricks.
- Arquio irá ser salvo noambiente Catalog ted_dev.(nome).

### `raw_mysql_extraction.py`

Este notebook conecta-se a um banco de dados MySQL para extrair dados. O fluxo típico é:
- Conectar ao banco MySQL usando credenciais seguras.
- Executar queries para buscar os dados desejados.
- Processar e salvar os dados em um formato compatível com o Databricks.
- Arquio irá ser salvo noambiente Catalog ted_dev.(nome).

> Os notebooks em formato `.ipynb` são apenas o resultado da execução desses scripts no Databricks, replicados no VS Code para referência.

---

## Como Rodar

1. Crie e preencha o arquivo `.env` com as variáveis necessárias.
2. Execute o container Docker:
   ```sh
   docker-compose up --build
   ```
3. O processo irá:
   - Carregar as variáveis de ambiente.
   - Inicializar e aplicar o Terraform.
   - Fazer o upload dos notebooks para o Databricks.

---

## Observações

- Não versionar o arquivo `.env` para manter a segurança das credenciais.
- O uso de Docker garante portabilidade e facilidade de execução em qualquer ambiente.

---

## No Databricks

- Executar os dois códigos qiue serão salvo em <catalog>.<schema>.<tabela>
- Notebooks criam tabelas em estágio raw (nomeado em cada tabela)

### Gerenciamento de Segredos (Secret Scope)

Para armazenar credenciais sensíveis (como tokens, senhas e chaves de API) de forma segura no Databricks, foi utilizado o recurso de **Secret Scope**, que permite acessar essas informações diretamente nos notebooks, sem expor dados sensíveis no código.

### Como criar o Secret Scope

1. Acessado o terminal com o **Databricks CLI** configurado.

2. Criado um Secret Scope (substitua `sqlserver_scope` pelo nome que desejar):

```bash
databricks secrets create-scope --scope api_scope

Foi utilizado o scope "sqlserver_scope" para o segredo de todas as credenciais do banco de dados Mysql e da API.

BD:
dbutils.secrets.get(scope="sqlserver_scope", key="sql_host"),
dbutils.secrets.get(scope="sqlserver_scope", key="sql_port"),
dbutils.secrets.get(scope="sqlserver_scope", key="sql_user"),
dbutils.secrets.get(scope="sqlserver_scope", key="sql_password").

API:
dbutils.secrets.get(scope="sqlserver_scope", key="api_user"),
dbutils.secrets.get(scope="sqlserver_scope", key="api_pass").
