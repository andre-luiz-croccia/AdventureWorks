FROM hashicorp/terraform:1.8

# Instalando dependências para CLI do Databricks
RUN apk add --no-cache bash curl unzip python3 py3-pip && \
    pip install --break-system-packages databricks-cli

