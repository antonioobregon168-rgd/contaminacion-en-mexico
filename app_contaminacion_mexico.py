import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ===============================
# MODO MANTENIMIENTO
# ===============================
MODO_MANTENIMIENTO = False

if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown(
        """
        <h1 style="text-align:center;color:black;">🛠️ Sitio en mantenimiento</h1>
        <p style="text-align:center;color:black;">
        Modificaciones en curso por <b>Antonio</b> 👨‍💻
        </p>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ===============================
# CONFIGURACIÓN
# ===============================
st.set_page_config(
    page_title="Monitor de Contaminación - México",
    page_icon="🌎",
    layout="wide"
)

st.title("🌫️ Monitor de Contaminación del Aire en México")

# ===============================
# REGIÓN
# ===============================
region = st.selectbox(
    "📍 Selecciona región:",
    ["México (todo el país)", "Guanajuato"]
)

# ===============================
# INTENTO API
# ===============================
url = "https://api.openaq.org/v2/latest"
params = {"country": "MX", "limit": 200}

try:
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json().get("results", [])
except:
    data = []

# ===============================
# PROCESAMIENTO
# ===============================
registros = []

for e in data:
    ciudad = e.get("city", "Desconocido")
    coords = e.get("coordinates", {})
    lat = coords.get("latitude")
    lon = coords.get("longitude")

    if lat is None or lon is None:
        continue

    for m in e.get("measurements", []):
        registros.append({
            "Ciudad": ciudad,
            "Contaminante": m["parameter"].upper(),
            "Valor": m["value"],
            "Unidad": m["unit"],
            "Latitud": lat,
            "Longitud": lon
        })

df = pd.DataFrame(registros)

# ===============================
# DATOS DE RESPALDO (CLAVE)
# ===============================
if df.empty:
    st.warning("⚠️ Usando datos de respaldo (API no disponible)")

    df = pd.DataFrame([

























