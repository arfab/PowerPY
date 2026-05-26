import os
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine, text
from src.config_manager import load_config, is_configured
from src.mock_data import create_and_populate_mock_db

# Variables de estado global de la conexion
_engine = None
_mode = "demo"  # "live" o "demo"
_error_message = None
_db_details = "SQLite Demo Mode"

def test_sql_server_connection(config):
    """
    Intenta crear una conexion a SQL Server con los parametros recibidos.
    Retorna (engine, None) si tiene exito, o (None, error_str) si falla.
    """
    try:
        server = config.get("SERVER", "")
        database = config.get("DATABASE", "")
        username = config.get("USERNAME", "")
        password = config.get("PASSWORD", "")
        driver = config.get("DRIVER", "ODBC Driver 17 for SQL Server")
        trusted = config.get("TRUSTED_CONNECTION", "no").lower() == "yes"

        if not server or not database:
            return None, "Servidor o Base de Datos no especificados."

        # Construir los parametros ODBC para SQLAlchemy pyodbc
        if trusted:
            odbc_str = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            odbc_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        params = urllib.parse.quote_plus(odbc_str)
        conn_str = f"mssql+pyodbc:///?odbc_connect={params}"
        
        # Intentar conectar con un timeout bajo para no colgar la UI
        engine = create_engine(conn_str, connect_args={'timeout': 5})
        
        # Validar la conexion de forma efectiva ejecutando un query simple
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        return engine, None
    except Exception as e:
        return None, str(e)

def init_engine(force_reload=False):
    """
    Inicializa el motor de base de datos.
    Intenta primero con SQL Server (si esta configurado).
    Si falla o no esta configurado, utiliza SQLite con datos ficticios realistas.
    """
    global _engine, _mode, _error_message, _db_details
    
    if _engine is not None and not force_reload:
        return _engine

    config = load_config()
    
    if is_configured() or (config.get("SERVER") and config.get("DATABASE")):
        # Intentar conectarse a la BD real
        engine, err = test_sql_server_connection(config)
        if engine:
            _engine = engine
            _mode = "live"
            _error_message = None
            _db_details = f"SQL Server: {config.get('SERVER')} ({config.get('DATABASE')})"
            print(">>> Conexion exitosa con SQL Server.")
            return _engine
        else:
            _error_message = err
            print(f">>> Fallo conexion a SQL Server. Detalle: {err}")
    else:
        _error_message = "No se encontro configuracion valida en config.json."
        print(">>> Base de datos no configurada. Iniciando Modo Demo...")

    # Fallback a SQLite Local
    _mode = "demo"
    _db_details = "SQLite Demo Mode (powerpy_demo.db)"
    
    sqlite_db_path = "powerpy_demo.db"
    # Crear motor SQLite
    engine = create_engine(f"sqlite:///{sqlite_db_path}")
    
    # Poblar la BD con datos simulados si es necesario
    try:
        with engine.connect() as conn:
            create_and_populate_mock_db(conn.connection)
    except Exception as e:
        print(f"Error al poblar la base de datos de simulación: {e}")
        
    _engine = engine
    return _engine

def execute_query(sql_query, params=None):
    """
    Ejecuta una consulta SQL y retorna un Pandas DataFrame.
    """
    engine = init_engine()
    try:
        # Usamos pandas read_sql que maneja internamente la conexion
        with engine.connect() as conn:
            # En SQLAlchemy 2.0+, stmts deben enviarse con text()
            query_obj = text(sql_query)
            df = pd.read_sql_query(query_obj, conn, params=params)
            return df
    except Exception as e:
        print(f"Error ejecutando query: {sql_query}\nError: {e}")
        # Retornamos un dataframe vacio en caso de falla
        return pd.DataFrame()

def get_connection_status():
    """
    Retorna el estado de la conexion actual para mostrarlo en el panel de Streamlit.
    """
    # Forzamos inicializacion si no se ha hecho
    init_engine()
    return {
        "mode": _mode,
        "details": _db_details,
        "error_message": _error_message
    }
