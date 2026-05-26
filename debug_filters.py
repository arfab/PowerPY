import sys
from src.db_engine import init_engine, get_connection_status, execute_query
from src.query_builder import get_dimension_values

print("Python version:", sys.version)

# Inicializar motor
init_engine()
status = get_connection_status()
print("Conexion status:", status)

print("\n--- TEST MASTER TABLE QUERY ---")
try:
    df = execute_query("SELECT * FROM dimAnios")
    print("dimAnios contents:\n", df)
except Exception as e:
    print("dimAnios error:", e)

print("\n--- TEST FALLBACK QUERY ---")
try:
    df_fb = execute_query("SELECT DISTINCT anio AS val, CAST(anio AS VARCHAR(10)) AS [desc] FROM factVentas WHERE anio IS NOT NULL ORDER BY anio")
    print("factVentas distinct anios:\n", df_fb)
except Exception as e:
    print("factVentas error:", e)

print("\n--- TEST get_dimension_values('Año') ---")
try:
    res = get_dimension_values("Año")
    print("get_dimension_values('Año') result:\n", res)
except Exception as e:
    print("get_dimension_values('Año') error:", e)
