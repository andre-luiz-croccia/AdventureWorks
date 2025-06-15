FROM hashicorp/terraform:1.8

# Configura ambiente Python sem conflitos
RUN apk add --no-cache bash curl unzip python3 && \
    python3 -m ensurepip --upgrade && \
    rm -rf /var/cache/apk/*

# Instala a CLI do Databricks em um virtualenv
RUN python3 -m venv /opt/databricks-cli && \
    /opt/databricks-cli/bin/pip install --no-cache-dir databricks-cli && \
    ln -s /opt/databricks-cli/bin/databricks /usr/local/bin/databricks && \
    ln -sf /bin/bash /bin/sh

# Define o shell como entrypoint padrão
ENTRYPOINT ["/bin/bash"]
