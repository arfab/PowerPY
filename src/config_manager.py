import os
import json

CONFIG_FILE = "config.json"

def get_config_path():
    """Retorna la ruta absoluta al archivo config.json."""
    return os.path.abspath(CONFIG_FILE)

def load_config():
    """
    Carga la configuracion de base de datos desde config.json.
    Si no existe, retorna un diccionario vacio.
    Posteriormente, sobreescribe con variables de entorno (DB_SERVER, etc.) si estan presentes.
    """
    config = {}
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error al leer config.json: {e}")
            config = {}
            
    # Sobreescribir con variables de entorno (Opción A)
    env_mapping = {
        "DB_TYPE": "DB_TYPE",
        "SERVER": "DB_SERVER",
        "DATABASE": "DB_DATABASE",
        "USERNAME": "DB_USERNAME",
        "PASSWORD": "DB_PASSWORD",
        "TRUSTED_CONNECTION": "DB_TRUSTED_CONNECTION",
        "DRIVER": "DB_DRIVER",
        "PORT": "DB_PORT"
    }
    
    for key, env_var in env_mapping.items():
        val = os.environ.get(env_var)
        if val is not None:
            config[key] = val
            
    return config

def save_config(config_data):
    """
    Guarda la configuracion en config.json.
    """
    path = get_config_path()
    try:
        # Nos aseguramos de guardar solo claves limpias
        clean_config = {
            "DB_TYPE": config_data.get("DB_TYPE", "sqlserver"),
            "SERVER": config_data.get("SERVER", ""),
            "DATABASE": config_data.get("DATABASE", ""),
            "USERNAME": config_data.get("USERNAME", ""),
            "PASSWORD": config_data.get("PASSWORD", ""),
            "TRUSTED_CONNECTION": config_data.get("TRUSTED_CONNECTION", "no"),
            "DRIVER": config_data.get("DRIVER", "ODBC Driver 17 for SQL Server"),
            "PORT": config_data.get("PORT", "1433")
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar config.json: {e}")
        return False

def is_configured():
    """
    Verifica si la configuracion tiene valores basicos cargados para SQL Server.
    """
    config = load_config()
    if not config:
        return False
    
    # Si requiere autenticacion de Windows
    if config.get("TRUSTED_CONNECTION", "no").lower() == "yes":
        return bool(config.get("SERVER") and config.get("DATABASE"))
    
    # Autenticacion SQL Server
    return bool(config.get("SERVER") and config.get("DATABASE") and config.get("USERNAME"))
