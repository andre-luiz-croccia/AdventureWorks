services:
  terraform-databricks:
    build:
      context: .
    image: terraform-databricks
    entrypoint: sh
    environment:
    volumes:
      - ./terraform:/workspace/terraform
    working_dir: /workspace/terraform