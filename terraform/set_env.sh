#!/bin/bash

# Carrega as variáveis do .env e exporta com prefixo TF_VAR_
set -o allexport
source .env
export TF_VAR_databricks_host="$DATABRICKS_HOST"
export TF_VAR_databricks_token="$DATABRICKS_TOKEN"
export TF_VAR_user_email="$USER_EMAIL"
set +o allexport

# Inicializa e aplica o Terraform
terraform init
terraform apply
