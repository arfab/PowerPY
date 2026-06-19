import streamlit as st
import pandas as pd
import plotly.express as px
from src.config_manager import load_config, save_config
from src.db_engine import execute_query, get_connection_status, init_engine
from src.query_builder import build_rolap_query, get_available_dimensions, get_dimension_values, METRICS_MAP, DIMENSIONS_MAP

# 1. CONFIGURACION DE LA PAGINA DE STREAMLIT
st.set_page_config(
    page_title="PowerPY - Informix MetaCube ROLAP Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para darle un toque premium y profesional (Estilo Dark Glassmorphism)
st.markdown("""
<style>
    /* Estilo para las tarjetas de KPI */
    .kpi-container {
        background-color: #1E232A;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2A303C;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-title {
        color: #8A99AD;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .kpi-subtitle {
        color: #38BDF8;
        font-size: 0.75rem;
        margin-top: 4px;
    }
    /* Indicator LED style */
    .led-green {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #10B981;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 8px #10B981;
    }
    .led-orange {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #F59E0B;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 8px #F59E0B;
    }
    /* Estilo del Área de Definición de Consulta */
    .query-definition-card {
        background-color: #161B22;
        border: 2px solid #30363D;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .box-title {
        color: #58A6FF;
        font-size: 0.95rem;
        font-weight: bold;
        margin-bottom: 8px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

def update_page_index_callback(page_dim, page_codes):
    key_widget = f"widget_{page_dim}"
    key_idx = f"index_{page_dim}"
    if key_widget in st.session_state:
        selected_val = st.session_state[key_widget]
        if selected_val in page_codes:
            st.session_state[key_idx] = page_codes.index(selected_val)

def render_page_navigator(selected_pages):
    if not selected_pages:
        return {}
    
    active_filters = {}
    with st.container(border=True):
        st.markdown(f"##### 📄 Navegación de Páginas ({selected_pages[0].upper() if len(selected_pages) == 1 else 'MetaCube Pages'})")
        st.caption("Usa las flechas ( ◀ / ▶ ) para avanzar/retroceder secuencialmente, o selecciona un valor específico.")
        
        # Renderizamos un selector horizontal para cada dimension
        for page_dim in selected_pages:
            page_vals = get_dimension_values(page_dim)
            if page_vals:
                page_codes = [d["val"] for d in page_vals]
                page_labels = {d["val"]: d["desc"] for d in page_vals}
                
                key_widget = f"widget_{page_dim}"
                key_idx = f"index_{page_dim}"
                
                if key_idx not in st.session_state:
                    st.session_state[key_idx] = 0
                
                idx_val = st.session_state[key_idx]
                if idx_val < 0 or idx_val >= len(page_codes):
                    idx_val = 0
                    st.session_state[key_idx] = 0
                
                if key_widget not in st.session_state or st.session_state[key_widget] not in page_codes:
                    st.session_state[key_widget] = page_codes[idx_val]
                
                col_prev, col_select, col_next = st.columns([1, 10, 1])
                
                with col_prev:
                    st.write("")
                    st.write("")
                    if st.button("◀", key=f"prev_{page_dim}", help=f"Ver {page_dim} anterior"):
                        new_idx = (idx_val - 1) % len(page_codes)
                        st.session_state[key_idx] = new_idx
                        st.session_state[key_widget] = page_codes[new_idx]
                        st.rerun()
                        
                with col_next:
                    st.write("")
                    st.write("")
                    if st.button("▶", key=f"next_{page_dim}", help=f"Ver {page_dim} siguiente"):
                        new_idx = (idx_val + 1) % len(page_codes)
                        st.session_state[key_idx] = new_idx
                        st.session_state[key_widget] = page_codes[new_idx]
                        st.rerun()
                        
                with col_select:
                    selected_val = st.selectbox(
                        label=f"Página ROLAP: {page_dim}",
                        options=page_codes,
                        index=st.session_state[key_idx],
                        format_func=lambda x: page_labels.get(x, str(x)),
                        key=key_widget,
                        on_change=update_page_index_callback,
                        args=(page_dim, page_codes)
                    )
                    active_filters[page_dim] = [selected_val]
    return active_filters

# 2. INICIALIZAR EL MOTOR DE BASE DE DATOS
init_engine()
db_status = get_connection_status()

# 3. PANEL LATERAL (SIDEBAR) - Carpeta de Filtros Generales y Estado
with st.sidebar:
    st.image("https://img.icons8.com/color/96/cubes.png", width=64)
    st.title("MetaCube ROLAP")
    st.write("Explorador DSS de Montagne")
    
    # Indicador de estado de base de datos
    st.markdown("---")
    st.subheader("Conexión del Sistema")
    if db_status["mode"] == "live":
        st.markdown(
            f'<div style="display: flex; align-items: center;"><span class="led-green"></span><b>Servidor Real Activo</b></div>', 
            unsafe_allow_html=True
        )
        st.caption(f"Base: `{db_status['details']}`")
    else:
        st.markdown(
            f'<div style="display: flex; align-items: center;"><span class="led-orange"></span><b>Modo Demostración</b></div>', 
            unsafe_allow_html=True
        )
        st.caption("Usando simulación local.")
        
    st.markdown("---")
    st.subheader("Filtros Globales (Slicers)")

    # Dropdowns de filtros poblados dinámicamente de forma robusta
    anios_list = [d["val"] for d in get_dimension_values("Año")]
    meses_dict = {d["val"]: d["desc"] for d in get_dimension_values("Mes")}
    regiones_list = [d["val"] for d in get_dimension_values("Región")]
    locales_dict = {d["val"]: d["desc"] for d in get_dimension_values("Local")}
    rubros_list = [d["val"] for d in get_dimension_values("Rubro")]
    
    filtered_years = st.multiselect("Año Fiscal", options=anios_list, default=[])
    selected_months_codes = st.multiselect(
        "Mes del Año", 
        options=list(meses_dict.keys()), 
        format_func=lambda x: meses_dict[x], 
        default=[]
    )
    filtered_regions = st.multiselect("Región Geográfica", options=regiones_list, default=[])
    selected_locales_codes = st.multiselect(
        "Local Comercial", 
        options=list(locales_dict.keys()), 
        format_func=lambda x: locales_dict[x], 
        default=[]
    )
    filtered_rubros = st.multiselect("Rubro Comercial", options=rubros_list, default=[])

    # Compilar los filtros de barra lateral activos
    active_filters = {}
    if filtered_years:
        active_filters["Año"] = filtered_years
    if selected_months_codes:
        active_filters["Mes"] = selected_months_codes
    if filtered_regions:
        active_filters["Región"] = filtered_regions
    if selected_locales_codes:
        active_filters["Local"] = selected_locales_codes
    if filtered_rubros:
        active_filters["Rubro"] = filtered_rubros

    st.markdown("---")
    if st.button("🔄 Forzar Recarga BD"):
        st.cache_data.clear()
        init_engine(force_reload=True)
        st.rerun()

# 4. CUERPO PRINCIPAL
st.title("📊 MetaCube: Explorador de Consulta ROLAP")
st.markdown("Diseña tu reporte dinámico seleccionando y ubicando medidas y dimensiones en las cajas del Constructor de Consulta.")

# 4.1. CONSTRUCTOR DE CONSULTA MAESTRO (Query Definition Area - Metacube Style)
with st.container(border=True):
    st.subheader("🛠️ Área de Definición de Consulta (Query Definition Area)")
    st.caption("Organiza los atributos de las dimensiones en filas, columnas o páginas, tal como en la interfaz clásica de Informix MetaCube.")
    
    col_box1, col_box2 = st.columns(2)
    
    with col_box1:
        # Selector de Medidas (Measures Drop Box)
        metric_options = list(METRICS_MAP.keys())
        selected_metrics = st.multiselect(
            "📊 Medidas (Measures)",
            options=metric_options,
            default=["Facturación ($)", "Unidades Vendidas"],
            help="Las columnas numéricas agregadas que deseas calcular en el reporte."
        )
        if not selected_metrics:
            selected_metrics = ["Facturación ($)"]
    
        # Validar las dimensiones que se pueden utilizar para el conjunto de métricas elegido
        available_dims = get_available_dimensions(selected_metrics)
        
        # Selector de Páginas (Pages Drop Box)
        selected_pages = st.multiselect(
            "📄 Páginas (Page Dimensions)",
            options=available_dims,
            default=[],
            help="Dimensiones que paginarán el reporte completo. Útil para filtrar todo por un valor específico en la cabecera."
        )
    
    with col_box2:
        # Selector de Filas (Rows Drop Box)
        remaining_for_rows = [d for d in available_dims if d not in selected_pages]
        row_dimensions = st.multiselect(
            "⬇️ Filas (Row Dimensions)",
            options=remaining_for_rows,
            default=["Región"] if "Región" in remaining_for_rows else [remaining_for_rows[0]],
            help="Dimensiones que formarán las filas de la tabla. Elige más de una para crear subordinaciones jerárquicas (Break Reports)."
        )
        if not row_dimensions:
            row_dimensions = ["Región"]
    
        # Selector de Columnas (Columns Drop Box)
        remaining_for_cols = [d for d in remaining_for_rows if d not in row_dimensions]
        col_dimensions = st.multiselect(
            "➡️ Columnas (Column Dimensions)",
            options=remaining_for_cols,
            default=["Año"] if "Año" in remaining_for_cols else [],
            help="Dimensiones que formarán los encabezados de las columnas."
        )

# 4.2. RESOLUCIÓN Y RENDERIZACIÓN DE NAVEGADORES DE PÁGINAS OLAP
# Renderizar el navegador de páginas OLAP arriba (fuera de las pestañas) y obtener los filtros activos
active_page_filters = render_page_navigator(selected_pages)

# Combinar filtros generales de barra lateral con los filtros de página OLAP activos
combined_filters = {**active_filters, **active_page_filters}

# Log de depuración temporal
try:
    with open("debug_run.log", "w", encoding="utf-8") as f_dbg:
        f_dbg.write(f"selected_pages: {selected_pages}\n")
        f_dbg.write(f"active_page_filters: {active_page_filters}\n")
        f_dbg.write(f"combined_filters: {combined_filters}\n")
except Exception:
    pass

# 4.3. PROCESAR MULTI-FACT TABLE Y BLENDING (ROLAP CUBE ENGINE)
# La unión de todas las dimensiones necesarias en la consulta SQL es: filas + columnas + páginas
total_dimensions = list(set(row_dimensions + col_dimensions + selected_pages))

# Explicar limitación si hay métricas financieras cruzadas por productos
any_financial = any("($)" in m for m in selected_metrics)
any_product_only = any(DIMENSIONS_MAP.get(d, {}).get("product_only", False) for d in total_dimensions)

# Ya no interrumpimos la ejecución (st.stop), sino que el motor enrutará
# de forma segura a factProductos y devolverá 0 en la métrica no conforme.

# 4.4. Realizar consultas individuales y fusión (Data Blending) en Pandas
merged_df = None
query_errors = []

for m_name in selected_metrics:
    try:
        sql, params = build_rolap_query(m_name, total_dimensions, combined_filters)
        df_m = execute_query(sql, params)
        
        if df_m.empty:
            continue
            
        if merged_df is None:
            merged_df = df_m
        else:
            # Fusión mediante Outer Join en Pandas sobre todas las dimensiones de la consulta
            dim_cols = [c for c in df_m.columns if c != m_name]
            merged_df = pd.merge(merged_df, df_m, on=dim_cols, how="outer")
    except Exception as e:
        query_errors.append(f"{m_name}: {str(e)}")

# Limpiar nulos del merge (reemplazar con 0 para métricas no presentes en la intersección)
if merged_df is not None and not merged_df.empty:
    for m_name in selected_metrics:
        if m_name in merged_df.columns:
            merged_df[m_name] = merged_df[m_name].fillna(0)

# 4.5. CALCULO DE TOTALES GENERALES DEL FILTRO DE CABECERA
total_ventas_monto = 0.0
total_productos_cant = 0
total_transacciones = 0

kpi_ventas_sql, kpi_ventas_params = build_rolap_query("Facturación ($)", ["Año"], combined_filters)
kpi_prod_sql, kpi_prod_params = build_rolap_query("Unidades Vendidas", ["Año"], combined_filters)
kpi_op_sql, kpi_op_params = build_rolap_query("Cantidad de Operaciones", ["Año"], combined_filters)

df_kpi_ventas = execute_query(kpi_ventas_sql, kpi_ventas_params)
df_kpi_prod = execute_query(kpi_prod_sql, kpi_prod_params)
df_kpi_op = execute_query(kpi_op_sql, kpi_op_params)

if not df_kpi_ventas.empty:
    total_ventas_monto = df_kpi_ventas["Facturación ($)"].sum()
if not df_kpi_prod.empty:
    total_productos_cant = int(df_kpi_prod["Unidades Vendidas"].sum())
if not df_kpi_op.empty:
    total_transacciones = int(df_kpi_op["Cantidad de Operaciones"].sum())

# Muestra del Grid de KPIs rápidas
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">Facturación Total</div><div class="kpi-value">${total_ventas_monto:,.2f}</div><div class="kpi-subtitle">Ventas Acumuladas</div></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">Unidades Vendidas</div><div class="kpi-value">{total_productos_cant:,} u.</div><div class="kpi-subtitle">Volumen de Artículos</div></div>', unsafe_allow_html=True)
with col_kpi3:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">Operaciones Realizadas</div><div class="kpi-value">{total_transacciones:,}</div><div class="kpi-subtitle">Tickets Emitidos</div></div>', unsafe_allow_html=True)
with col_kpi4:
    ticket_promedio = total_ventas_monto / total_transacciones if total_transacciones > 0 else 0
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">Ticket Promedio</div><div class="kpi-value">${ticket_promedio:,.2f}</div><div class="kpi-subtitle">Facturación por Ticket</div></div>', unsafe_allow_html=True)

# 5. SECCION DE TABS (Resultados de Consulta)
tab_pivot, tab_visual, tab_sql, tab_config = st.tabs([
    "📋 Tabla Dinámica (Pivot)", 
    "📈 Gráfico Dinámico", 
    "🔍 Consultas SQL Generadas",
    "⚙️ Conexión Base de Datos"
])

# --- TAB 1: TABLA DINAMICA PIVOT ---
with tab_pivot:
    if merged_df is None or merged_df.empty:
        st.warning("⚠️ No se encontraron datos para la combinación seleccionada. Intenta remover filtros o simplificar el cubo.")
        if query_errors:
            st.error("Errores del motor de base de datos:\n" + "\n".join(query_errors))
    else:
        st.subheader("Matriz ROLAP: Tabla Dinámica")
        st.caption("Vista del reporte analítico resultante. Incluye subtotales y Totales Generales en filas y columnas.")
        
        pivot_rows = row_dimensions
        pivot_cols = col_dimensions if col_dimensions else None
        
        # Eliminar las dimensiones que están en Páginas del desglose físico de filas/columnas,
        # puesto que su valor ya está fijo en la cabecera y no aporta granularidad.
        # Filtramos merged_df localmente en base a las páginas por seguridad
        clean_df = merged_df.copy()
        
        try:
            # Generar la Pivot Table con Totales Generales (margins=True)
            # Replicando los reportes clásicos de MetaCube
            pivot_table = pd.pivot_table(
                clean_df,
                index=pivot_rows,
                columns=pivot_cols,
                values=selected_metrics,
                aggfunc="sum",
                fill_value=0,
                margins=True,
                margins_name="Total General"
            )
            
            # Formatear visualmente los números de la Pivot Table en Streamlit
            # Si hay valores flotantes, les damos formato de dos decimales
            styled_pivot = pivot_table.style.format(lambda x: f"${x:,.2f}" if isinstance(x, float) and x > 1000 else f"{x:,}" if isinstance(x, (int, float)) else str(x))
            
            # Mostrar la tabla formateada y estilizada de manera premium con soporte completo de scroll
            st.dataframe(styled_pivot, use_container_width=True)
            
            # Nota explicativa si hay dimensiones de producto cruzadas con finanzas
            if any_financial and any_product_only:
                st.info("💡 **Nota de Desagregación ROLAP (Safe Routing):** Has seleccionado dimensiones exclusivas de producto (ej: Género, Rubro) junto con métricas financieras (ej: Facturación $). Como la tabla `factVentas` no posee desglose por productos, la aplicación completó la facturación como `0.00` para que puedas analizar el resto de las variables (ej: Unidades Vendidas por producto) en este mismo reporte sin bloqueos.")
            
            # Exportar datos
            st.markdown("---")
            csv_data = pivot_table.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Exportar Matriz Pivot a CSV",
                data=csv_data,
                file_name="metacube_report_matrix.csv",
                mime="text/csv"
            )
        except Exception as e:
            # En raras combinaciones (ej. vacíos absolutos), margins de pandas puede fallar.
            # En ese caso, mostramos la tabla sin totales de margen para asegurar robustez absoluta.
            try:
                pivot_table_fallback = pd.pivot_table(
                    clean_df,
                    index=pivot_rows,
                    columns=pivot_cols,
                    values=selected_metrics,
                    aggfunc="sum",
                    fill_value=0
                )
                st.dataframe(pivot_table_fallback, use_container_width=True)
                
                st.markdown("---")
                csv_data = pivot_table_fallback.to_csv().encode('utf-8')
                st.download_button(
                    label="📥 Exportar Matriz a CSV",
                    data=csv_data,
                    file_name="metacube_report_matrix.csv",
                    mime="text/csv"
                )
            except Exception as e_inner:
                st.error(f"Error al estructurar la tabla pivot: {e_inner}")
                st.info("Sugerencia: Intenta cambiar de caja los atributos en las filas y columnas.")

# --- TAB 2: GRAFICO DINAMICO ---
with tab_visual:
    if merged_df is None or merged_df.empty:
        st.warning("⚠️ No hay datos para graficar.")
    else:
        st.subheader("Representación Gráfica del Cubo")
        st.caption("Visualiza las variables agregadas del cubo de datos de manera interactiva.")
        
        col_g1, col_g2 = st.columns([1, 3])
        
        # Obtener dimensiones disponibles para el gráfico (excluyendo páginas que tienen valor único fijo)
        chart_dims = [d for d in total_dimensions if d not in selected_pages]
        if not chart_dims:
            chart_dims = total_dimensions
            
        with col_g1:
            st.markdown("##### Configuración del Eje")
            chart_x = st.selectbox("Eje X (Dimensión)", options=chart_dims, index=0)
            
            color_candidates = ["Ninguno"] + [d for d in chart_dims if d != chart_x]
            chart_color = st.selectbox(
                "Desglosar por / Leyenda (Color)", 
                options=color_candidates, 
                index=1 if len(color_candidates) > 1 else 0
            )
            color_val = None if chart_color == "Ninguno" else chart_color
            
            chart_y = st.selectbox(
                "Métrica en Eje Y", 
                options=selected_metrics, 
                index=0
            )
            
            chart_style = st.radio(
                "Tipo de Visualización",
                options=["Barras Agrupadas", "Barras Apiladas", "Líneas de Tendencia", "Área Temporal", "Torta (Composición)"],
                key="chart_style_selector"
            )
            
        with col_g2:
            colors_palette = px.colors.qualitative.Prism
            fig = None
            
            try:
                groupby_cols = [chart_x]
                if color_val:
                    groupby_cols.append(color_val)
                    
                plot_df = merged_df.groupby(groupby_cols)[chart_y].sum().reset_index()
                
                if chart_style == "Barras Agrupadas":
                    fig = px.bar(
                        plot_df, 
                        x=chart_x, 
                        y=chart_y, 
                        color=color_val, 
                        barmode="group",
                        color_discrete_sequence=colors_palette
                    )
                elif chart_style == "Barras Apiladas":
                    fig = px.bar(
                        plot_df, 
                        x=chart_x, 
                        y=chart_y, 
                        color=color_val, 
                        barmode="relative",
                        color_discrete_sequence=colors_palette
                    )
                elif chart_style == "Líneas de Tendencia":
                    fig = px.line(
                        plot_df, 
                        x=chart_x, 
                        y=chart_y, 
                        color=color_val, 
                        markers=True,
                        color_discrete_sequence=colors_palette
                    )
                elif chart_style == "Área Temporal":
                    fig = px.area(
                        plot_df, 
                        x=chart_x, 
                        y=chart_y, 
                        color=color_val,
                        color_discrete_sequence=colors_palette
                    )
                elif chart_style == "Torta (Composición)":
                    pie_names = color_val if color_val else chart_x
                    fig = px.pie(
                        plot_df, 
                        names=pie_names, 
                        values=chart_y,
                        color_discrete_sequence=colors_palette,
                        hole=0.4
                    )
                    
                # Estilizar el gráfico para que combine perfectamente
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E2E8F0", size=12),
                    xaxis=dict(showgrid=True, gridcolor="#2A303C", title_text=chart_x),
                    yaxis=dict(showgrid=True, gridcolor="#2A303C", title_text=chart_y),
                    legend=dict(
                        bgcolor="rgba(30, 35, 42, 0.8)",
                        bordercolor="#2A303C",
                        borderwidth=1
                    ),
                    margin=dict(t=15, b=15, l=15, r=15),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error generando el gráfico interactivo: {e}")

# --- TAB 3: CONSULTAS SQL GENERADAS ---
with tab_sql:
    st.subheader("Motor ROLAP: Código SQL Generado")
    st.markdown("""
    Para alimentar el cubo dinámico, el motor de PowerPY compila tus selecciones en consultas SQL unificadas.
    Si seleccionaste múltiples métricas, estas se ejecutan por separado y se fusionan en memoria con Pandas para mantener el rendimiento y evitar duplicaciones de montos.
    """)
    
    for m_name in selected_metrics:
        st.markdown(f"#### SQL para Medida: `{m_name}`")
        try:
            sql, _ = build_rolap_query(m_name, total_dimensions, combined_filters)
            st.code(sql, language="sql")
        except Exception as e:
            st.error(f"No se pudo compilar SQL para {m_name}: {e}")

# --- TAB 4: CONFIGURACION DE BASE DE DATOS ---
with tab_config:
    st.subheader("Configuración de la Base de Datos")
    st.markdown("""
    Configura aquí las credenciales para conectarte a tu base de datos de producción **Microsoft SQL Server**.
    Si la conexión falla o los campos están vacíos, la herramienta utilizará automáticamente el **Modo Demostración** con base local SQLite.
    """)
    
    current_config = load_config()
    
    with st.form("db_credentials_form"):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            server_input = st.text_input(
                "Servidor SQL Server (SERVER)", 
                value=current_config.get("SERVER", ""),
                placeholder="ej: sqlserver.montagne.com o localhost\\SQLEXPRESS"
            )
            database_input = st.text_input(
                "Base de Datos (DATABASE)", 
                value=current_config.get("DATABASE", "MontagneAdministracionTest")
            )
            driver_input = st.text_input(
                "Controlador ODBC (DRIVER)", 
                value=current_config.get("DRIVER", "ODBC Driver 17 for SQL Server"),
                help="Debe estar instalado en tu sistema de Windows."
            )
            port_input = st.text_input(
                "Puerto SQL Server", 
                value=current_config.get("PORT", "1433")
            )
            
        with col_form2:
            trusted_conn = st.selectbox(
                "Autenticación de Windows (Trusted Connection)",
                options=["no", "yes"],
                index=0 if current_config.get("TRUSTED_CONNECTION", "no") == "no" else 1,
                help="Elige 'yes' si tu base de datos utiliza tus credenciales locales de Windows. En 'no' debes proveer Usuario y Contraseña."
            )
            username_input = st.text_input(
                "Usuario (UID)", 
                value=current_config.get("USERNAME", "")
            )
            password_input = st.text_input(
                "Contraseña (PWD)", 
                type="password", 
                value=current_config.get("PASSWORD", "")
            )
            
        st.markdown("---")
        submit_btn = st.form_submit_button("💾 Guardar y Validar Conexión")
        
        if submit_btn:
            new_config = {
                "DB_TYPE": "sqlserver",
                "SERVER": server_input,
                "DATABASE": database_input,
                "USERNAME": username_input,
                "PASSWORD": password_input,
                "TRUSTED_CONNECTION": trusted_conn,
                "DRIVER": driver_input,
                "PORT": port_input
            }
            
            with st.spinner("Intentando conectar al Servidor de Base de Datos..."):
                from src.db_engine import test_sql_server_connection
                test_engine, err = test_sql_server_connection(new_config)
                
                if test_engine:
                    save_config(new_config)
                    init_engine(force_reload=True)
                    st.success("🟢 ¡Conexión exitosa establecida con SQL Server! La configuración ha sido guardada.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"""
                    🔴 **Fallo en la Conexión.** Las credenciales no se han guardado.
                    
                    **Detalle del Error:**
                    `{err}`
                    
                    *Por favor, verifica que el servidor esté encendido, que el nombre del servidor/instancia y base de datos sean correctos, y que tengas instalado el driver ODBC especificado.*
                    """)
                    
    st.markdown("### Configuración Guardada en Disco")
    st.json(current_config)
