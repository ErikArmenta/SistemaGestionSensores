# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 21:29:33 2025

@author: acer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --------------------------
# Credenciales desde Streamlit Secrets
# --------------------------
google_creds = st.secrets["google_sheets"]

creds_dict = {
    "type": google_creds["type"],
    "project_id": google_creds["project_id"],
    "private_key_id": google_creds["private_key_id"],
    "private_key": google_creds["private_key"].replace('\\n', '\n'),  # importante
    "client_email": google_creds["client_email"],
    "client_id": google_creds["client_id"],
    "auth_uri": google_creds["auth_uri"],
    "token_uri": google_creds["token_uri"],
    "auth_provider_x509_cert_url": google_creds["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_creds["client_x509_cert_url"]
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# --------------------------
# Conectar hoja de Google Sheets
# --------------------------
SPREADSHEET_ID = "1JLJBRgoHw0Kyl5igDMVRpt_atoe7AOx_gOncbS_4yL0"
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Solicitudes")


# --------------------------
# FUNCIONES CON PERSISTENCIA
# --------------------------
@st.cache_data(ttl=60)
def load_solicitudes_from_sheet():
    """Carga datos desde Google Sheets con cache"""
    try:
        records = worksheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return []

def save_solicitud_to_sheet(solicitud):
    """Guarda en Google Sheets y actualiza session_state"""
    try:
        worksheet.append_row([
            solicitud["Timestamp"],
            solicitud["Nombre"],
            solicitud["Nómina"],
            solicitud["Línea"],
            solicitud["Estación/Máquina"],
            solicitud["Cantidad"],
            solicitud["Turno"],
            solicitud["Motivo"],
            solicitud["NumParte"],
            solicitud["NombreSensor"]
        ])

        # Agregar a session_state
        st.session_state.solicitudes.append(solicitud)

        # Limpiar cache para recargar datos
        st.cache_data.clear()

        return True
    except Exception as e:
        st.error(f"Error al guardar: {str(e)}")
        return False


# Configuración de la página
st.set_page_config(
    page_title="Gestión de Sensores",
    page_icon="📡",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .sensor-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #4338CA;
    }
    .sensor-img {
        width: 100% !important;
        height: 220px !important;
        object-fit: cover !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
#   CATÁLOGO LOCAL
# =========================
CATALOG = [
    {'ID': 1, 'Nombre': 'Sensor Flat Amarillo', 'NumParte': '31 T89 79711', 'Descripción': 'Sensor de 3 PIN de 8mm', 'ImagenURL': 'imagenes/sensor1.jpg'},
    {'ID': 2, 'Nombre': 'Sensor Flat Azul', 'NumParte': '31 C47 39980', 'Descripción': 'Sensor de 3 PIN de 8mm', 'ImagenURL': 'imagenes/sensor2.jpg'},
    {'ID': 3, 'Nombre': 'Sensor Flat Metalico', 'NumParte': '30 A51 21098', 'Descripción': 'Sensor de 3 PIN de 12mm', 'ImagenURL': 'imagenes/sensor3.jpg'},
    {'ID': 4, 'Nombre': 'Sensor Flat Blanco', 'NumParte': '31 I34 003010', 'Descripción': 'Sensor Flat Blanco', 'ImagenURL': 'imagenes/sensor4.jpg'},
    {'ID': 5, 'Nombre': 'Sensor Falt Naranja', 'NumParte': '31 E28 002286', 'Descripción': 'Sensor Flat de 4 PIN de 12mm', 'ImagenURL': 'imagenes/sensor5.jpg'},
    {'ID': 6, 'Nombre': 'Sensor Flat Negro', 'NumParte': '31 A51 24742', 'Descripción': 'Sensor Flat de 3 PIN de 12mm', 'ImagenURL': 'imagenes/sensor6.jpg'},
    {'ID': 7, 'Nombre': 'Sensor Goma Blanca', 'NumParte': '30 I34 67223', 'Descripción': 'Sensor de Goma de 3 PIN de 12mm', 'ImagenURL': 'imagenes/sensor7.jpg'},
    {'ID': 8, 'Nombre': 'Sensor Goma Naranja', 'NumParte': '31 I34 36291', 'Descripción': 'Sensor de Goma de 3 PIN de 12mm', 'ImagenURL': 'imagenes/sensor8.jpg'},
    {'ID': 9, 'Nombre': 'Sensor Flat de Luz', 'NumParte': '31 F21 43655', 'Descripción': 'Sensor Flat de 4 PIN de 12mm', 'ImagenURL': 'imagenes/sensor9.jpg'},
    {'ID': 10, 'Nombre': 'Sensor Flat Azul', 'NumParte': '31 S19 016 018', 'Descripción': 'Sensor Flat de 4 PIN de 12mm', 'ImagenURL': 'imagenes/sensor10.jpg'},
    {'ID': 11, 'Nombre': 'Sensor MARPOSS', 'NumParte': '31 T19 013 009', 'Descripción': 'Sensor para Riel Marposs', 'ImagenURL': 'imagenes/sensor11.jpg'},
    {'ID': 12, 'Nombre': 'Sensor de Flujo', 'NumParte': '31 I34 57555', 'Descripción': 'Sensor de Flujo especial para agua', 'ImagenURL': 'imagenes/sensor12.jpg'},
    {'ID': 13, 'Nombre': 'Sensor Presión de Aire', 'NumParte': '31 I34 110991', 'Descripción': 'Sensor para presión de aire', 'ImagenURL': 'imagenes/sensor13.jpg'},
    {'ID': 14, 'Nombre': 'Sensor Cripper', 'NumParte': '31 R260 13264', 'Descripción': 'Sensor Cripper', 'ImagenURL': 'imagenes/sensor14.jpg'},
    {'ID': 15, 'Nombre': 'Sensor Elevador', 'NumParte': '31 P18 37173', 'Descripción': 'Sensor para elevaodres', 'ImagenURL': 'imagenes/sensor15.jpg'},
    {'ID': 16, 'Nombre': 'Sensor de Pluma', 'NumParte': '31 K05 008014', 'Descripción': 'Sensor de pluma', 'ImagenURL': 'imagenes/sensor16.jpg'},
    {'ID': 17, 'Nombre': 'Sensor Carlo Gavazzi', 'NumParte': '31 C760 15563', 'Descripción': 'Sensor Carlo Gavazzi', 'ImagenURL': 'imagenes/sensor17.jpg'},
    {'ID': 18, 'Nombre': 'Sensor Carlo Gavazzi 8mm', 'NumParte': '31 C760 17270', 'Descripción': 'Sensor Carlo Gavazzi 8mm', 'ImagenURL': 'imagenes/sensor18.jpg'},
    {'ID': 19, 'Nombre': 'Sensor Carlo Gavazzi Laser', 'NumParte': '31 C760 15564', 'Descripción': 'Sensor Carlo Gavazzi Laser', 'ImagenURL': 'imagenes/sensor19.jpg'},
    {'ID': 20, 'Nombre': 'Sensor Carlo Gavazzi Flat', 'NumParte': '31 C760 17269', 'Descripción': 'Sensor Carlo Gavazzi Flat 12mm', 'ImagenURL': 'imagenes/sensor20.jpg'}
]

# =========================
#   SESSION STATE CON CARGA INICIAL
# =========================
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "solicitudes" not in st.session_state:
    st.session_state.solicitudes = []

# Cargar datos solo una vez al iniciar
if not st.session_state.data_loaded:
    st.session_state.solicitudes = load_solicitudes_from_sheet()
    st.session_state.data_loaded = True

if "selected_sensor" not in st.session_state:
    st.session_state.selected_sensor = None

if "show_form" not in st.session_state:
    st.session_state.show_form = False

# =========================
#   HEADER
# =========================
st.title("📡 Sistema de Gestión de Sensores")
st.markdown("---")

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Catálogo de Sensores", "📊 Dashboard", "📋 Solicitudes"]
)

# =========================
#   CATÁLOGO
# =========================
if menu == "🏠 Catálogo de Sensores":

    st.header("Catálogo de Sensores Disponibles")

    # --------------------------
    #   GRID DE CARDS
    # --------------------------
    cols_per_row = 3
    for i in range(0, len(CATALOG), cols_per_row):

        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):

            if i + j < len(CATALOG):

                sensor = CATALOG[i + j]
                with col:
                    # Imagen redimensionada correctamente
                    st.image(sensor['ImagenURL'], width=220)

                    st.subheader(sensor["Nombre"])
                    st.caption(f"**Parte:** {sensor['NumParte']}")
                    st.write(sensor["Descripción"])

                    # Botón solicitar debajo de cada card
                    if st.button("🛒 Solicitar", key=f"sol_{sensor['ID']}"):
                        st.session_state.selected_sensor = sensor
                        st.session_state.show_modal = True  # <-- activar modal

# =========================
#   Formulario Modal
# =========================

if st.session_state.get("show_modal", False):

    @st.dialog("Solicitud de Sensor")
    def modal_form():
        sensor = st.session_state.selected_sensor

        st.markdown(f"### Solicitar: {sensor['Nombre']}")

        nombre = st.text_input("Nombre completo*")
        nomina = st.text_input("Nómina*")
        linea = st.text_input("Línea*")
        estacion = st.text_input("Estación/Máquina*")
        cantidad = st.number_input("Cantidad*", min_value=1, value=1)
        turno = st.selectbox("Turno*", ["", "Matutino", "Vespertino", "Nocturno"])
        motivo = st.text_area("Motivo*")

        col1, col2 = st.columns(2)
        enviar = col1.button("Enviar")
        cancelar = col2.button("Cancelar")

        if enviar:
            if all([nombre, nomina, linea, estacion, turno, motivo]):
                nueva = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nombre": nombre,
                    "Nómina": nomina,
                    "Línea": linea,
                    "Estación/Máquina": estacion,
                    "Cantidad": cantidad,
                    "Turno": turno,
                    "Motivo": motivo,
                    "NumParte": sensor["NumParte"],
                    "NombreSensor": sensor["Nombre"]
                }

                if save_solicitud_to_sheet(nueva):
                    st.success("Solicitud enviada correctamente")
                    st.session_state.show_modal = False
                    st.rerun()
            else:
                st.error("Completa todos los campos obligatorios")

        if cancelar:
            st.session_state.show_modal = False
            st.rerun()

    modal_form()



# ============= PÁGINA: DASHBOARD =============
elif menu == "📊 Dashboard":
    st.header("Dashboard de Análisis")

    if len(st.session_state.solicitudes) == 0:
        st.info("📊 No hay solicitudes registradas aún. Ve al catálogo y solicita algunos sensores.")
    else:
        df = pd.DataFrame(st.session_state.solicitudes)

        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Solicitudes", len(df))
        with col2:
            st.metric("Sensores Únicos", df['NombreSensor'].nunique())
        with col3:
            st.metric("Líneas Activas", df['Línea'].nunique())
        with col4:
            st.metric("Cantidad Total", df['Cantidad'].sum())

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            # Solicitudes por Línea
            fig_linea = px.bar(
                df.groupby('Línea').size().reset_index(name='Solicitudes'),
                x='Línea',
                y='Solicitudes',
                title='Solicitudes por Línea',
                color='Solicitudes',
                color_continuous_scale='Blues'
            )
            fig_linea.update_layout(showlegend=False)
            st.plotly_chart(fig_linea, use_container_width=True)

        with col2:
            # Solicitudes por Persona
            fig_persona = px.pie(
                df,
                names='Nombre',
                title='Solicitudes por Persona',
                hole=0.4
            )
            st.plotly_chart(fig_persona, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Solicitudes por Estación/Máquina
            fig_estacion = px.bar(
                df.groupby('Estación/Máquina').size().reset_index(name='Solicitudes'),
                x='Estación/Máquina',
                y='Solicitudes',
                title='Solicitudes por Estación/Máquina',
                color='Solicitudes',
                color_continuous_scale='Purples'
            )
            fig_estacion.update_layout(showlegend=False)
            st.plotly_chart(fig_estacion, use_container_width=True)

        with col4:
            # Frecuencia de Sensores
            fig_sensor = px.bar(
                df.groupby('NombreSensor').size().reset_index(name='Frecuencia'),
                y='NombreSensor',
                x='Frecuencia',
                title='Sensores Más Solicitados',
                orientation='h',
                color='Frecuencia',
                color_continuous_scale='Greens'
            )
            fig_sensor.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_sensor, use_container_width=True)

        # Gráfico de tendencia temporal
        st.subheader("📅 Tendencia Temporal")
        df['Fecha'] = pd.to_datetime(df['Timestamp']).dt.date
        fig_tiempo = px.line(
            df.groupby('Fecha').size().reset_index(name='Solicitudes'),
            x='Fecha',
            y='Solicitudes',
            title='Solicitudes por Día',
            markers=True
        )
        st.plotly_chart(fig_tiempo, use_container_width=True)

# ============= PÁGINA: SOLICITUDES =============
elif menu == "📋 Solicitudes":
    st.header("Historial de Solicitudes")

    if len(st.session_state.solicitudes) == 0:
        st.info("📋 No hay solicitudes registradas.")
    else:
        df = pd.DataFrame(st.session_state.solicitudes)

        # Filtros
        st.subheader("Filtros")
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_linea = st.multiselect("Línea", options=df['Línea'].unique())
        with col2:
            filtro_turno = st.multiselect("Turno", options=df['Turno'].unique())
        with col3:
            filtro_sensor = st.multiselect("Sensor", options=df['NombreSensor'].unique())

        # Aplicar filtros
        df_filtrado = df.copy()
        if filtro_linea:
            df_filtrado = df_filtrado[df_filtrado['Línea'].isin(filtro_linea)]
        if filtro_turno:
            df_filtrado = df_filtrado[df_filtrado['Turno'].isin(filtro_turno)]
        if filtro_sensor:
            df_filtrado = df_filtrado[df_filtrado['NombreSensor'].isin(filtro_sensor)]

        st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df)} solicitudes**")

        # Mostrar tabla
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )

        # Botón de descarga
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"solicitudes_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============= SIDEBAR INFO =============
st.sidebar.markdown("---")
st.sidebar.info(f"📊 **Total de solicitudes:** {len(st.session_state.solicitudes)}")

# Botón para recargar datos desde Google Sheets
if st.sidebar.button("🔄 Recargar datos desde Google Sheets"):
    st.cache_data.clear()
    st.session_state.solicitudes = load_solicitudes_from_sheet()
    st.session_state.data_loaded = True
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("💡 Los datos se guardan automáticamente en Google Sheets")
st.sidebar.caption("🔑 Asegúrate de tener las credenciales configuradas en Streamlit Secrets")