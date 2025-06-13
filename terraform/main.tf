terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.40.0"  # Versão atualizada
    }
  }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

# Cria diretório padrão
resource "databricks_directory" "andre_dir" {
  path = "/Users/${var.user_email}/Adventure_Works"  # Sem espaços no caminho
}

# Notebook de extração via API
resource "databricks_notebook" "raw_api" {
  path           = "${databricks_directory.andre_dir.path}/raw_api_extraction"
  language       = "PYTHON"
  content_base64 = base64encode(file("${path.module}/notebooks/raw_api_extraction.py")) 
  format         = "SOURCE"
  depends_on     = [databricks_directory.andre_dir]  # Garante ordem de criação
}

# Notebook de extração via MySQL
resource "databricks_notebook" "raw_mysql" {
  path           = "${databricks_directory.andre_dir.path}/raw_mysql_extraction"
  language       = "PYTHON"
  content_base64 = base64encode(file("${path.module}/notebooks/raw_mysql_extraction.py"))  
  format         = "SOURCE"
  depends_on     = [databricks_directory.andre_dir]
}





