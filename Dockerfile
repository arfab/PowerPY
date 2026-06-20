FROM python:3.10-slim

# Instalar dependencias del sistema requeridas para compilar unixodbc y descargar los repositorios de MS
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar el Microsoft ODBC Driver para SQL Server (msodbcsql17)
# Se descarga la clave GPG de MS, se guarda en keyrings, y se crea la lista apt indicando que la firme microsoft-prod.gpg
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY app.py .
COPY config.json.example ./config.json.example
COPY src/ ./src/

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Definir variables de entorno de red recomendadas para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para iniciar la aplicación
CMD ["streamlit", "run", "app.py"]
