# Guía de Uso de Docker para PowerPY

Esta guía describe cómo compilar, configurar y ejecutar la aplicación **PowerPY** dentro de un contenedor Docker conectándose a la base de datos externa de SQL Server (Opción A).

## Requisitos Previos

*   Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/) en tu máquina (Windows, macOS o Linux).

## Configuración de Base de Datos

La aplicación ha sido modificada para soportar configuración por variables de entorno en tiempo de ejecución. 

Puedes configurar el archivo [docker-compose.yml](file:///c:/Users/arfab/source/py-repos/PowerPY/docker-compose.yml) completando la sección `environment`:

```yaml
    environment:
      - DB_TYPE=sqlserver
      - DB_SERVER=tu-servidor-sql.com
      - DB_DATABASE=NombreDeTuBD
      - DB_USERNAME=tu_usuario
      - DB_PASSWORD=tu_contraseña
      - DB_TRUSTED_CONNECTION=no
      - DB_DRIVER=ODBC Driver 17 for SQL Server
      - DB_PORT=1433
```

> [!NOTE]
> Si no se definen las variables de entorno de base de datos (`DB_SERVER` y `DB_DATABASE`), la aplicación cargará automáticamente el **Modo Demostración** utilizando la base local SQLite autogenerada.

---

## Comandos para Ejecutar la Aplicación

### Opción 1: Usando Docker Compose (Recomendado)

1.  **Construir e iniciar el contenedor:**
    ```bash
    docker compose up --build -d
    ```
2.  **Ver los logs en tiempo real:**
    ```bash
    docker compose logs -f
    ```
3.  **Detener y remover el contenedor:**
    ```bash
    docker compose down
    ```

### Opción 2: Usando comandos de Docker clásicos

1.  **Construir la imagen:**
    ```bash
    docker build -t powerpy-app .
    ```
2.  **Iniciar el contenedor pasando variables por línea de comandos:**
    ```bash
    docker run -d -p 8501:8501 \
      -e DB_SERVER="186.122.177.252" \
      -e DB_DATABASE="MontagneAdministracionTest" \
      -e DB_USERNAME="programadormtg2" \
      -e DB_PASSWORD="tu_password_aqui" \
      --name powerpy-instance \
      powerpy-app
    ```

---

## Acceso a la Aplicación

Una vez levantado el contenedor, abre tu navegador web favorito y accede a:
👉 **[http://localhost:8501](http://localhost:8501)**
