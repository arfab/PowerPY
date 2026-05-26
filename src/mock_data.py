import sqlite3
import random
from datetime import datetime, timedelta

def create_and_populate_mock_db(conn_or_path):
    """
    Crea las tablas de dimensiones y hechos en una base de datos SQLite y las puebla
    con datos realistas e historicos de Montagne.
    conn_or_path puede ser un objeto sqlite3.Connection o una ruta a un archivo.
    """
    if isinstance(conn_or_path, str):
        conn = sqlite3.connect(conn_or_path)
    else:
        conn = conn_or_path

    cursor = conn.cursor()

    # 1. CREAR TABLAS DE DIMENSIONES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimAnios (
        codigo TEXT NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimMeses (
        codigo INTEGER NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimRegiones (
        codigo TEXT NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimLocales (
        codigo INTEGER NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimRubros (
        codigo TEXT NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimSubrubros (
        codigo TEXT NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL,
        rubro TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimGeneros (
        codigo TEXT NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dimVendedores (
        codigo INTEGER NOT NULL PRIMARY KEY,
        descripcion TEXT NOT NULL
    );
    """)

    # 2. CREAR TABLAS DE HECHOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factVentas (
        fecha TEXT NULL,
        anio INTEGER NULL,
        mes INTEGER NULL,
        dia INTEGER NULL,
        franja INTEGER NULL,
        empresa INTEGER NULL,
        tipo_empresa TEXT NULL,
        region TEXT NULL,
        vendedor INTEGER NULL,
        cliente TEXT NULL,
        nrosocio TEXT NULL,
        formulario TEXT NULL,
        monto REAL NULL,
        efectivo REAL NULL,
        tarjeta REAL NULL,
        cheque REAL NULL,
        valores REAL NULL,
        cantidad INTEGER NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factProductos (
        fecha TEXT NULL,
        anio INTEGER NULL,
        mes INTEGER NULL,
        dia INTEGER NULL,
        franja INTEGER NULL,
        empresa INTEGER NULL,
        tipo_empresa TEXT NULL,
        region TEXT NULL,
        vendedor INTEGER NULL,
        cliente TEXT NULL,
        nrosocio TEXT NULL,
        formulario TEXT NULL,
        generico TEXT NULL,
        codalfa TEXT NULL,
        rubro TEXT NULL,
        subrubro TEXT NULL,
        genero TEXT NULL,
        temporada TEXT NULL,
        cantidad INTEGER NULL,
        numero_ventas INTEGER NULL
    );
    """)

    # Verificar si ya hay datos cargados para no duplicar
    cursor.execute("SELECT COUNT(*) FROM dimAnios")
    if cursor.fetchone()[0] > 0:
        # Ya hay datos, salimos de la generacion
        return conn

    # 3. POBLAR TABLAS DE DIMENSIONES
    # Años
    anios_data = [("2024", "Año 2024"), ("2025", "Año 2025"), ("2026", "Año 2026")]
    cursor.executemany("INSERT OR IGNORE INTO dimAnios VALUES (?, ?)", anios_data)

    # Meses
    meses_data = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimMeses VALUES (?, ?)", meses_data)

    # Regiones
    regiones_data = [
        ("Patagonia", "Región Patagonia"),
        ("Cuyo", "Región Cuyo"),
        ("NOA", "Región Noroeste (NOA)"),
        ("Centro", "Región Centro"),
        ("Buenos Aires", "Región Buenos Aires / AMBA")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimRegiones VALUES (?, ?)", regiones_data)

    # Locales
    locales_data = [
        (101, "Montagne Florida (CABA)"),
        (102, "Montagne Unicenter (Martínez)"),
        (103, "Montagne Bariloche (Río Negro)"),
        (104, "Montagne Mendoza (Centro)"),
        (105, "Montagne Salta (Shopping)")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimLocales VALUES (?, ?)", locales_data)

    # Rubros
    rubros_data = [
        ("Indumentaria", "Prendas e Indumentaria"),
        ("Calzado", "Calzado y Zapatillas"),
        ("Camping", "Equipamiento de Camping")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimRubros VALUES (?, ?)", rubros_data)

    # Subrubros
    subrubros_data = [
        ("Camperas", "Camperas e Impermeables", "Indumentaria"),
        ("Pantalones", "Pantalones y Shorts", "Indumentaria"),
        ("Remeras", "Remeras y Chombas", "Indumentaria"),
        ("Zapatillas", "Zapatillas Trekking/Running", "Calzado"),
        ("Botas", "Botas de Nieve/Montaña", "Calzado"),
        ("Mochilas", "Mochilas y Bolsos", "Camping"),
        ("Carpas", "Carpas de Alta Montaña/Familiar", "Camping"),
        ("Bolsas de Dormir", "Bolsas de Dormir y Aislantes", "Camping")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimSubrubros VALUES (?, ?, ?)", subrubros_data)

    # Géneros
    generos_data = [("Hombre", "Masculino"), ("Mujer", "Femenino"), ("Unisex", "Unisex / Accesorios")]
    cursor.executemany("INSERT OR IGNORE INTO dimGeneros VALUES (?, ?)", generos_data)

    # Vendedores
    vendedores_data = [
        (201, "Santiago Almada"), (202, "Valeria Soria"), (203, "Federico Diaz"),
        (204, "Camila Russo"), (205, "Gustavo Benitez"), (206, "Micaela Flores"),
        (207, "Lucas Pereyra"), (208, "Agostina Paz"), (209, "Nicolas Gimenez"),
        (210, "Florencia Costa")
    ]
    cursor.executemany("INSERT OR IGNORE INTO dimVendedores VALUES (?, ?)", vendedores_data)

    # 4. POBLAR TABLAS DE HECHOS (MOCK DE VENTAS REALISTAS)
    # Lista de productos reales simulados de Montagne con precios estimados
    productos_simulados = [
        # Indumentaria
        {"generico": "Campera Softshell Summit", "codalfa": "CAM-01", "rubro": "Indumentaria", "subrubro": "Camperas", "genero": "Hombre", "precio": 85000},
        {"generico": "Campera Pluma Ultra Light", "codalfa": "CAM-02", "rubro": "Indumentaria", "subrubro": "Camperas", "genero": "Mujer", "precio": 120000},
        {"generico": "Campera Impermeable Gore-Tex", "codalfa": "CAM-03", "rubro": "Indumentaria", "subrubro": "Camperas", "genero": "Unisex", "precio": 165000},
        {"generico": "Pantalon Cargo Trekking", "codalfa": "PAN-01", "rubro": "Indumentaria", "subrubro": "Pantalones", "genero": "Hombre", "precio": 45000},
        {"generico": "Pantalon Térmico Fleece", "codalfa": "PAN-02", "rubro": "Indumentaria", "subrubro": "Pantalones", "genero": "Mujer", "precio": 38000},
        {"generico": "Remera Dry-Fit Respirable", "codalfa": "REM-01", "rubro": "Indumentaria", "subrubro": "Remeras", "genero": "Unisex", "precio": 18000},
        
        # Calzado
        {"generico": "Zapatilla Trekking Explorer", "codalfa": "ZAP-01", "rubro": "Calzado", "subrubro": "Zapatillas", "genero": "Hombre", "precio": 68000},
        {"generico": "Zapatilla Trail Running Speed", "codalfa": "ZAP-02", "rubro": "Calzado", "subrubro": "Zapatillas", "genero": "Mujer", "precio": 62000},
        {"generico": "Bota Impermeable Nieve", "codalfa": "BOT-01", "rubro": "Calzado", "subrubro": "Botas", "genero": "Unisex", "precio": 95000},
        
        # Camping
        {"generico": "Carpa Iglu Everest 4 Personas", "codalfa": "CAR-01", "rubro": "Camping", "subrubro": "Carpas", "genero": "Unisex", "precio": 180000},
        {"generico": "Carpa Estructural Canadiense", "codalfa": "CAR-02", "rubro": "Camping", "subrubro": "Carpas", "genero": "Unisex", "precio": 290000},
        {"generico": "Mochila Mochilero 70 Litros", "codalfa": "MOC-01", "rubro": "Camping", "subrubro": "Mochilas", "genero": "Unisex", "precio": 75000},
        {"generico": "Mochila Urbana Deportiva 30L", "codalfa": "MOC-02", "rubro": "Camping", "subrubro": "Mochilas", "genero": "Unisex", "precio": 28000},
        {"generico": "Bolsa Dormir Termica Extreme -10C", "codalfa": "BOL-01", "rubro": "Camping", "subrubro": "Bolsas de Dormir", "genero": "Unisex", "precio": 55000},
    ]

    clientes_nombres = [
        "Andres Lopez", "Maria Rodriguez", "Juan Gonzalez", "Silvia Martinez", 
        "Carlos Gomez", "Patricia Fernandez", "Jorge Diaz", "Ana Alvarez", 
        "Roberto Romero", "Clara Benitez", "Lucas Medina", "Sofia Herrera",
        "Martin Castro", "Julia Gimenez", "Daniel Perez", "Laura Silva"
    ]

    # Generamos registros desde el 1 de Enero de 2024 hasta la fecha actual
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 5, 25)
    delta_days = (end_date - start_date).days

    ventas_rows = []
    productos_rows = []

    # Asignamos locales a regiones
    local_to_region = {
        101: "Buenos Aires",
        102: "Buenos Aires",
        103: "Patagonia",
        104: "Cuyo",
        105: "NOA"
    }

    # Asignamos tipo de empresa (Propio o Franquicia)
    local_type = {
        101: "Propio",
        102: "Propio",
        103: "Franquicia",
        104: "Franquicia",
        105: "Propio"
    }

    ticket_id = 10001

    # Generamos un volumen representativo de transacciones
    # Queremos ~1500 transacciones en total repartidas en los 2.5 años
    for _ in range(1200):
        # 1. Fecha aleatoria
        rand_days = random.randint(0, delta_days)
        sale_date = start_date + timedelta(days=rand_days)
        
        anio = sale_date.year
        mes = sale_date.month
        dia = sale_date.day
        
        # Estacionalidad simple para inflar ventas en invierno (junio-agosto) y verano (diciembre-febrero)
        winter_months = [6, 7, 8]
        summer_months = [12, 1, 2]
        
        # Ajustamos probabilidad de venta
        multiplier = 1.0
        if mes in winter_months:
            multiplier = 1.4  # Mas ventas en temporada de nieve
        elif mes in summer_months:
            multiplier = 1.3  # Mas ventas en temporada de camping

        # Seleccionamos local, region, vendedor
        local_id = random.choice(list(locales_data))[0]
        region = local_to_region[local_id]
        tipo_empresa = local_type[local_id]
        vendedor_id = random.choice(list(vendedores_data))[0]
        
        # Cliente y socio
        cliente = random.choice(clientes_nombres)
        nrosocio = ""
        if random.random() > 0.4:
            nrosocio = f"SOC-{random.randint(10000, 99999)}"
            
        formulario = f"FC-{tipo_empresa[0]}-0001-{ticket_id:08d}"
        ticket_id += 1
        
        # Franja horaria
        franja = random.randint(9, 21)

        # Generar de 1 a 4 items de productos vendidos en este ticket
        num_items = random.randint(1, 4)
        items_in_ticket = []
        
        # Para hacer mas coherente la compra:
        # Si es Patagonia en invierno, empujamos Camperas y Calzado de nieve
        # Si es verano general, empujamos Camping y Remeras
        preferred_rubro = None
        if region == "Patagonia" and mes in winter_months:
            preferred_rubro = "Indumentaria"
        elif mes in summer_months:
            preferred_rubro = "Camping"

        total_ticket_monto = 0.0
        total_ticket_cantidad = 0
        
        for _ in range(num_items):
            # Filtro sesgado por estacionalidad
            if preferred_rubro and random.random() < 0.6:
                candidates = [p for p in productos_simulados if p["rubro"] == preferred_rubro]
            else:
                candidates = productos_simulados
                
            p = random.choice(candidates)
            
            # Cantidad vendida de este producto especifico (1 a 3 unidades)
            cant_item = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
            item_monto = p["precio"] * cant_item
            
            total_ticket_monto += item_monto
            total_ticket_cantidad += cant_item
            
            # Temporada coherente al año y mes de la venta
            temp_season = "Invierno" if mes in [4, 5, 6, 7, 8, 9] else "Verano"
            temporada = f"{temp_season} {anio}"
            
            # Registrar item en factProductos
            productos_rows.append((
                sale_date.strftime("%Y-%m-%d"),
                anio, mes, dia, franja,
                local_id, tipo_empresa, region,
                vendedor_id, cliente, nrosocio, formulario,
                p["generico"], p["codalfa"], p["rubro"], p["subrubro"], p["genero"],
                temporada, cant_item, 1
            ))
            
        # Repartir el monto del ticket en los medios de pago para factVentas
        # Metodos de pago: Efectivo, Tarjeta, Cheque, Valores
        efectivo = 0.0
        tarjeta = 0.0
        cheque = 0.0
        valores = 0.0
        
        pay_method = random.choices(["tarjeta", "efectivo", "mixto"], weights=[70, 20, 10])[0]
        if pay_method == "tarjeta":
            tarjeta = total_ticket_monto
        elif pay_method == "efectivo":
            efectivo = total_ticket_monto
        else:
            tarjeta = round(total_ticket_monto * 0.8, 2)
            efectivo = round(total_ticket_monto * 0.2, 2)
            
        # Eventualmente algun cheque para camping de valores altos
        if total_ticket_monto > 150000 and random.random() < 0.15:
            cheque = total_ticket_monto
            tarjeta = 0.0
            efectivo = 0.0
            
        # Registrar en factVentas
        ventas_rows.append((
            sale_date.strftime("%Y-%m-%d"),
            anio, mes, dia, franja,
            local_id, tipo_empresa, region,
            vendedor_id, cliente, nrosocio, formulario,
            total_ticket_monto, efectivo, tarjeta, cheque, valores,
            total_ticket_cantidad
        ))

    # Insertar registros en lote
    cursor.executemany("""
    INSERT INTO factVentas (
        fecha, anio, mes, dia, franja, empresa, tipo_empresa, region, vendedor,
        cliente, nrosocio, formulario, monto, efectivo, tarjeta, cheque, valores, cantidad
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ventas_rows)

    cursor.executemany("""
    INSERT INTO factProductos (
        fecha, anio, mes, dia, franja, empresa, tipo_empresa, region, vendedor,
        cliente, nrosocio, formulario, generico, codalfa, rubro, subrubro, genero, temporada, cantidad, numero_ventas
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, productos_rows)

    conn.commit()
    return conn
