variable "databricks_host" {
  description = "URL da instância do Databricks"
  type        = string
}

variable "databricks_token" {
  description = "Token de autenticação do Databricks (uso pessoal ou de serviço)"
  type        = string
  sensitive   = true
}

variable "user_email" {
  description = "E-mail do usuário Databricks onde os notebooks serão criados"
  type        = string
}


