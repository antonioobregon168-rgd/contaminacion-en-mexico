import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ===============================
# MODO MANTENIMIENTO
# ===============================
MODO_MANTENIMIENTO = True # Cambia a True si estás actualizando

if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown(
        """
        <div style="text-align:center;margin-top:120px;">
            <h1 style="color:black;">🛠️ Sitio en mantenimiento</h1>
            <p style="color:black;">Actualizaciones en curso por <b>Antonio</b> 👨‍💻</p>
            <p style="color:gray;">Vuelve en unos minutos 🚀</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Monitor de Contaminación - México",
    page_icon="🌎",
    layout="wide"
)

st.title("🌫️ Monitor de Contaminación del Aire en México")
st.write("Datos ambientales en tiempo casi real (OpenAQ)")

# ===============================
# REGIÓN
# ===============================
region = st.selectbox(
    "📍 Selecciona región:",
    ["México (todo el país)", "Guanajuato"]
)

# ===============================
# OBTENER DATOS (OpenAQ)
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
df = pd.DataFrame(
    [
        ["CDMX", "PM25", 28, "µg/m³", 19.4326, -99.1332],
        ["León", "PM25", 41, "µg/m³", 21.1220, -101.6860],
        ["Guanajuato", "PM25", 35, "µg/m³", 21.0190, -101.2574],
        ["Celaya", "PM25", 38, "µg/m³", 20.5270, -100.8123],
        ["Salamanca", "PM25", 45, "µg/m³", 20.5710, -101.1910],
    ],
    columns=["Ciudad", "Contaminante", "Valor", "Unidad", "Latitud", "Longitud"]
)


# ===============================
# FILTRO GUANAJUATO
# ===============================
if region == "Guanajuato":
    df = df[df["Ciudad"].isin(
        ["León", "Irapuato", "Celaya", "Salamanca", "Guanajuato"]
    )]

# ===============================
# CONTAMINANTE
# ===============================
contaminante = st.selectbox(
    "🔍 Selecciona contaminante:",
    sorted(df["Contaminante"].unique())
)

df_f = df[df["Contaminante"] == contaminante].copy()

# ===============================
# GRÁFICA
# ===============================
st.subheader("📈 Niveles por ciudad")

fig, ax = plt.subplots()
ax.bar(df_f["Ciudad"], df_f["Valor"])
ax.set_ylabel(df_f["Unidad"].iloc[0])
ax.set_title(f"Niveles de {contaminante}")
plt.xticks(rotation=30)
st.pyplot(fig)

# ===============================
# MAPA
# ===============================
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
    view = pdk.ViewState(latitude=21.12, longitude=-101.68, zoom=7.5)
else:
    view = pdk.ViewState(latitude=23.63, longitude=-102.55, zoom=5.3)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip={"text": "Ciudad: {Ciudad}\nValor: {Valor} {Unidad}"}
)

st.pydeck_chart(deck)

st.success("✅ Aplicación cargada correctamente")


























