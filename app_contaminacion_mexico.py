import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ======================================
# MODO MANTENIMIENTO
# ======================================
MODO_MANTENIMIENTO = True # Cambia a True si estás actualizando

if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown("""
        <div style="
            background-color:white;
            color:black;
            padding:40px;
            margin-top:100px;
            border-radius:15px;
            text-align:center;
            box-shadow:0px 10px 30px rgba(0,0,0,0.15);
        ">
            <h1>🛠️ Sitio en mantenimiento</h1>
            <p>La aplicación está siendo actualizada</p>
            <p><b>Modificaciones por Antonio</b> 👨‍💻</p>
            <p style="color:gray;">Vuelve en unos minutos 🚀</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ======================================
# CONFIGURACIÓN GENERAL
# ======================================
st.set_page_config(
    page_title="Monitor de Contaminación en México",
    page_icon="🌎",
    layout="wide"
)

st.title("🌫️ Monitor de Contaminación del Aire en México")
st.write("Datos ambientales en tiempo casi real obtenidos desde OpenAQ")

# ======================================
# MODO EDUCATIVO
# ======================================
st.subheader("📘 Modo Educativo")

with st.expander("¿Qué son los contaminantes más comunes?"):
    st.markdown("""
    **PM2.5** – Partículas muy pequeñas, dañan pulmones  
    **PM10** – Irritan ojos y garganta  
    **NO₂** – Proviene de autos e industrias  
    **O₃** – Afecta vías respiratorias  
    **CO** – Gas tóxico invisible
    """)

with st.expander("¿Por qué es importante monitorear el aire?"):
    st.markdown("""
    🌎 Protege la salud  
    👶 Cuida a niños y adultos mayores  
    📊 Ayuda a tomar decisiones ambientales
    """)

# ======================================
# SELECCIÓN DE REGIÓN
# ======================================
region = st.selectbox(
    "Selecciona la región:",
    ["México (todo el país)", "Guanajuato"]
)

# ======================================
# OBTENER DATOS (OpenAQ)
# ======================================
BASE_URL = "https://api.openaq.org/v2/latest"

params = {
    "country": "MX",
    "limit": 200
}

if region == "Guanajuato":
    params["state"] = "Guanajuato"

headers = {
    "User-Agent": "Monitor-Contaminacion-Mexico"
}

try:
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    data = response.json().get("results", [])
except:
    data = []

# ======================================
# PROCESAMIENTO DE DATOS
# ======================================
records = []

for station in data:
    city = station.get("city", "Desconocido")
    coords = station.get("coordinates", {})
    lat = coords.get("latitude")
    lon = coords.get("longitude")

    if lat is None or lon is None:
        continue

    for m in station.get("measurements", []):
        records.append({
            "Ciudad": city,
            "Contaminante": m["parameter"].upper(),
            "Valor": m["value"],
            "Unidad": m["unit"],
            "Latitud": lat,
            "Longitud": lon
        })

df = pd.DataFrame(records)

# ======================================
# DATOS DE EJEMPLO SI NO HAY DATOS
# ======================================
if df.empty:
    st.warning("⚠️ No hay datos en tiempo real. Mostrando datos de ejemplo.")

    df = pd.DataFrame([
        {"Ciudad": "Guanajuato", "Contaminante": "PM25", "Valor": 32, "Unidad": "µg/m³", "Latitud": 21.0186, "Longitud": -101.2591},
        {"Ciudad": "León", "Contaminante": "PM25", "Valor": 40, "Unidad": "µg/m³", "Latitud": 21.122, "Longitud": -101.681},
        {"Ciudad": "CDMX", "Contaminante": "PM25", "Valor": 28, "Unidad": "µg/m³", "Latitud": 19.4326, "Longitud": -99.1332}
    ])

# ======================================
# TABLA
# ======================================
st.subheader("📊 Datos de contaminación")
st.dataframe(df, use_container_width=True)

# ======================================
# SELECCIÓN DE CONTAMINANTE
# ======================================
contaminante = st.selectbox(
    "🔍 Selecciona contaminante:",
    sorted(df["Contaminante"].unique())
)

df_f = df[df["Contaminante"] == contaminante].copy()

# ======================================
# GRÁFICA
# ======================================
st.subheader("📈 Niveles por ciudad")
fig, ax = plt.subplots()
ax.bar(df_f["Ciudad"], df_f["Valor"])
ax.set_ylabel(df_f["Unidad"].iloc[0])
ax.set_title(f"Niveles de {contaminante}")
plt.xticks(rotation=30)
st.pyplot(fig)

# ======================================
# MAPA
# ======================================
st.subheader("🗺️ Mapa interactivo")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_f,
    get_position="[Longitud, Latitud]",
    get_radius=4000,
    get_fill_color="[0, 120, 255, 200]",
    pickable=True
)

if region == "Guanajuato":
    view = pdk.ViewState(latitude=21.02, longitude=-101.26, zoom=7.5)
else:
    view = pdk.ViewState(latitude=23.63, longitude=-102.55, zoom=5.3)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip={"text": "Ciudad: {Ciudad}\nValor: {Valor} {Unidad}"}
)

st.pydeck_chart(deck)

st.success("✅ Aplicación funcionando correctamente")



































