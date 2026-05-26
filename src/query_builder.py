# Mapeo de dimensiones a sus correspondientes columnas de SQL y JOINs requeridos
DIMENSIONS_MAP = {
    "Año": {
        "column": "f.anio",
        "label": "Año",
        "joins": []
    },
    "Mes": {
        "column": "m.descripcion",
        "key_column": "f.mes",
        "label": "Mes",
        "joins": ["LEFT JOIN dimMeses m ON f.mes = m.codigo"],
        "order_by": "f.mes"
    },
    "Región": {
        "column": "f.region",
        "label": "Región",
        "joins": []
    },
    "Local": {
        "column": "l.descripcion",
        "key_column": "f.empresa",
        "label": "Local",
        "joins": ["LEFT JOIN dimLocales l ON f.empresa = l.codigo"]
    },
    "Vendedor": {
        "column": "v.descripcion",
        "key_column": "f.vendedor",
        "label": "Vendedor",
        "joins": ["LEFT JOIN dimVendedores v ON f.vendedor = v.codigo"]
    },
    "Cliente": {
        "column": "f.cliente",
        "label": "Cliente",
        "joins": []
    },
    # Dimensiones exclusivas de factProductos
    "Rubro": {
        "column": "f.rubro",
        "label": "Rubro",
        "joins": [],
        "product_only": True
    },
    "Subrubro": {
        "column": "f.subrubro",
        "label": "Subrubro",
        "joins": [],
        "product_only": True
    },
    "Género": {
        "column": "f.genero",
        "label": "Género",
        "joins": [],
        "product_only": True
    },
    "Temporada": {
        "column": "f.temporada",
        "label": "Temporada",
        "joins": [],
        "product_only": True
    },
    "Producto Genérico": {
        "column": "f.generico",
        "label": "Producto Genérico",
        "joins": [],
        "product_only": True
    },
    "Código Alfa": {
        "column": "f.codalfa",
        "label": "Código Alfanumérico",
        "joins": [],
        "product_only": True
    }
}

METRICS_MAP = {
    "Facturación ($)": {
        "table": "factVentas",
        "agg": "SUM(f.monto)",
        "label": "Venta ($)",
        "product_table_supported": False
    },
    "Ventas en Efectivo ($)": {
        "table": "factVentas",
        "agg": "SUM(f.efectivo)",
        "label": "Efectivo ($)",
        "product_table_supported": False
    },
    "Ventas con Tarjeta ($)": {
        "table": "factVentas",
        "agg": "SUM(f.tarjeta)",
        "label": "Tarjeta ($)",
        "product_table_supported": False
    },
    "Unidades Vendidas": {
        "table": "factProductos",
        "agg": "SUM(f.cantidad)",
        "label": "Unidades",
        "product_table_supported": True
    },
    "Cantidad de Operaciones": {
        "table": "factProductos",
        "agg": "SUM(f.numero_ventas)",
        "label": "Operaciones",
        "product_table_supported": True
    }
}

def build_rolap_query(metric_name, dimensions_list, filters=None):
    """
    Construye una consulta SQL de agregacion ROLAP dinámica para una métrica y una lista de dimensiones.
    Si se solicitan dimensiones exclusivas de producto para una métrica financiera,
    el motor realiza un ruteo seguro a factProductos devolviendo 0, evitando fallos
    y permitiendo cruzar cualquier combinación.
    """
    metric_info = METRICS_MAP.get(metric_name)
    if not metric_info:
        raise ValueError(f"Métrica no soportada: {metric_name}")

    table_name = metric_info["table"]
    
    # Validar si hay dimensiones exclusivas de producto
    has_product_dims = any(DIMENSIONS_MAP.get(d, {}).get("product_only", False) for d in dimensions_list)
    
    # Ruteo seguro para dimensiones no conformes
    is_non_conforming = has_product_dims and not metric_info["product_table_supported"]
    
    if is_non_conforming:
        table_name = "factProductos"
        agg_expr = "CAST(0 AS REAL)"
    else:
        agg_expr = metric_info["agg"]

    select_fields = []
    groupby_fields = []
    joins = set()
    order_by_fields = []

    # Procesar todas las dimensiones solicitadas
    for dim_name in dimensions_list:
        dim_info = DIMENSIONS_MAP.get(dim_name)
        if not dim_info:
            continue
            
        col = dim_info["column"]
        select_fields.append(f"{col} AS [{dim_name}]")
        groupby_fields.append(col)
        for j in dim_info.get("joins", []):
            joins.add(j)
            
        if "order_by" in dim_info:
            order_by_fields.append(dim_info["order_by"])
        else:
            order_by_fields.append(col)

    # Procesar Métrica
    agg_expr = metric_info["agg"]
    select_fields.append(f"{agg_expr} AS [{metric_name}]")

    # Procesar Filtros (WHERE)
    where_clauses = []
    params = {}
    
    if filters:
        for friendly_filter_name, values in filters.items():
            if not values:
                continue
                
            # Convertir valores de filtro a enteros para columnas numéricas de hechos (Año, Mes, Local)
            # Esto evita fallos de tipo (int vs string) en SQLite y SQL Server
            if friendly_filter_name in ["Año", "Mes", "Local"]:
                try:
                    if isinstance(values, list):
                        values = [int(v) for v in values]
                    else:
                        values = int(values)
                except (ValueError, TypeError):
                    pass
                
            # Mapear nombre amigable a columna SQL
            col_filter = None
            if friendly_filter_name == "Año":
                col_filter = "f.anio"
            elif friendly_filter_name == "Mes":
                col_filter = "f.mes"
            elif friendly_filter_name == "Región":
                col_filter = "f.region"
            elif friendly_filter_name == "Rubro" and table_name == "factProductos":
                col_filter = "f.rubro"
            elif friendly_filter_name == "Local":
                col_filter = "f.empresa"
                
            if col_filter:
                if isinstance(values, list):
                    if len(values) == 1:
                        param_name = f"p_{col_filter.replace('.', '_')}"
                        where_clauses.append(f"{col_filter} = :{param_name}")
                        params[param_name] = values[0]
                    else:
                        param_placeholders = []
                        for idx, val in enumerate(values):
                            p_name = f"p_{col_filter.replace('.', '_')}_{idx}"
                            param_placeholders.append(f":{p_name}")
                            params[p_name] = val
                        where_clauses.append(f"{col_filter} IN ({', '.join(param_placeholders)})")
                else:
                    param_name = f"p_{col_filter.replace('.', '_')}"
                    where_clauses.append(f"{col_filter} = :{param_name}")
                    params[param_name] = values

    # Construir SQL
    select_str = ", ".join(select_fields)
    join_str = "\n    ".join(list(joins))
    groupby_str = ", ".join(groupby_fields)
    orderby_str = ", ".join(order_by_fields)
    
    sql = f"SELECT {select_str}\nFROM {table_name} f"
    if join_str:
        sql += f"\n    {join_str}"
    if where_clauses:
        sql += f"\nWHERE {' AND '.join(where_clauses)}"
    if groupby_str:
        sql += f"\nGROUP BY {groupby_str}"
    if orderby_str:
        sql += f"\nORDER BY {orderby_str}"
        
    return sql, params

def get_available_dimensions(metric_name_or_list):
    """
    Retorna la lista de todas las dimensiones disponibles en el sistema.
    Gracias al motor de ruteo seguro (Safe Routing), todas las dimensiones se pueden cruzar
    incluso si se eligen métricas financieras mixtas.
    """
    return list(DIMENSIONS_MAP.keys())

def get_dimension_values(dim_name):
    """
    Retorna los valores únicos actuales de una dimensión específica para alimentar los filtros de la UI.
    Incluye una estrategia de fallback automática y robusta: si las tablas de dimensiones
    están vacías o no existen en la base de datos real, busca los valores únicos directamente
    de las tablas de hechos correspondientes.
    """
    dim_info = DIMENSIONS_MAP.get(dim_name)
    if not dim_info:
        return []
        
    from src.db_engine import execute_query
    df = None
    
    # 1. INTENTAR CONSULTA PRINCIPAL A LA TABLA DE DIMENSIÓN
    # Se usa AS [desc] con corchetes porque 'desc' es palabra reservada en SQL Server
    try:
        if dim_name == "Año":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimAnios ORDER BY codigo"
        elif dim_name == "Mes":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimMeses ORDER BY codigo"
        elif dim_name == "Región":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimRegiones ORDER BY codigo"
        elif dim_name == "Local":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimLocales ORDER BY codigo"
        elif dim_name == "Vendedor":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimVendedores ORDER BY descripcion"
        elif dim_name == "Rubro":
            sql = "SELECT codigo AS val, descripcion AS [desc] FROM dimRubros ORDER BY codigo"
        else:
            column = dim_info["column"]
            joins = "\n    ".join(dim_info.get("joins", []))
            h_table = "factProductos" if dim_info.get("product_only") else "factVentas"
            sql = f"SELECT DISTINCT {column} AS val, {column} AS [desc] FROM {h_table} f"
            if joins:
                sql += f"\n {joins}"
            sql += f"\n WHERE {column} IS NOT NULL ORDER BY {column}"
            
        df = execute_query(sql)
    except Exception as e:
        print(f"Error al consultar dimensión '{dim_name}' en su tabla maestra. Usando fallback... Detalle: {e}")
        df = None

    # 2. FALLBACK DINÁMICO A LA TABLA DE HECHOS SI LA TABLA DE DIMENSIÓN ESTÁ VACÍA O DIÓ ERROR
    if df is None or df.empty:
        try:
            h_table = "factProductos" if dim_info.get("product_only") else "factVentas"
            
            # Construimos queries agnósticas (compatibles con SQL Server y SQLite) usando corchetes para desc
            if dim_name == "Año":
                sql_fallback = "SELECT DISTINCT anio AS val, CAST(anio AS VARCHAR(10)) AS [desc] FROM factVentas WHERE anio IS NOT NULL ORDER BY anio"
            elif dim_name == "Mes":
                sql_fallback = "SELECT DISTINCT mes AS val, CAST(mes AS VARCHAR(10)) AS [desc] FROM factVentas WHERE mes IS NOT NULL ORDER BY mes"
            elif dim_name == "Región":
                sql_fallback = "SELECT DISTINCT region AS val, region AS [desc] FROM factVentas WHERE region IS NOT NULL AND region <> '' ORDER BY region"
            elif dim_name == "Local":
                sql_fallback = "SELECT DISTINCT empresa AS val, CAST(empresa AS VARCHAR(10)) AS [desc] FROM factVentas WHERE empresa IS NOT NULL ORDER BY empresa"
            elif dim_name == "Vendedor":
                sql_fallback = "SELECT DISTINCT vendedor AS val, CAST(vendedor AS VARCHAR(10)) AS [desc] FROM factVentas WHERE vendedor IS NOT NULL ORDER BY vendedor"
            elif dim_name == "Rubro":
                sql_fallback = "SELECT DISTINCT rubro AS val, rubro AS [desc] FROM factProductos WHERE rubro IS NOT NULL AND rubro <> '' ORDER BY rubro"
            else:
                column = dim_info["column"]
                sql_fallback = f"SELECT DISTINCT {column} AS val, CAST({column} AS VARCHAR(50)) AS [desc] FROM {h_table} f WHERE {column} IS NOT NULL ORDER BY {column}"
                
            df = execute_query(sql_fallback)
        except Exception as e:
            print(f"Fallo crítico en fallback de dimensión '{dim_name}': {e}")
            return []

    # 3. PROCESAR Y EMBELLECER LOS RESULTADOS EN PYTHON (Database-Agnostic UX)
    if df is not None and not df.empty:
        records = df.to_dict('records')
        
        # Mapeos de nombres estéticos de soporte en Python en caso de que desc sea puramente numérico
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        for r in records:
            val = r["val"]
            
            # Embellecer meses (ej: de "1" a "Enero")
            if dim_name == "Mes":
                try:
                    val_int = int(val)
                    r["desc"] = meses_nombres.get(val_int, f"Mes {val}")
                except (ValueError, TypeError):
                    pass
            
            # Embellecer locales (ej: de "101" a "Local 101")
            elif dim_name == "Local":
                if str(r["desc"]).isdigit() or r["desc"] == val:
                    r["desc"] = f"Local {val}"
                    
            # Embellecer vendedores (ej: de "201" a "Vendedor 201")
            elif dim_name == "Vendedor":
                if str(r["desc"]).isdigit() or r["desc"] == val:
                    r["desc"] = f"Vendedor {val}"
                    
            # Embellecer años (ej: de 2024 a "Año 2024")
            elif dim_name == "Año":
                r["desc"] = f"Año {val}"
                
        return records
        
    return []
