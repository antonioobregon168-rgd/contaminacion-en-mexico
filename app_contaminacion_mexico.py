import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ==================================================
# 🛠️ MODO MANTENIMIENTO
# ==================================================
MODO_MANTENIMIENTO = False  # ⬅️ pon True cuando estés actualizando

if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:120px;
            padding:40px;
            background-color:#ffffff;
            border-radius:15px;
            box-shadow:0px 10px 30px rgba(0,0,0,0.1);
        ">
            <h1 style="color:black;">🛠️ Sitio en mantenimiento</h1>
            <p style="font-size:18px; color:black;">
                La aplicación está siendo actualizada.
            </p>
            <p style="font-size:16px; color:black;">
                Modificaciones en curso por <b>Antonio</b> 👨‍💻
            </p>
            <p style="color:gray;">
                Regresa en unos minutos 🚀
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# ==================================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==================================================
st.set_page_config(
    page_title="Monitor de Contaminación - México",
    page_icon="🌎",
    layout="wide"
)

st.title("🌫️ Monitor de Contaminación del Aire en México")
st.write("Datos reales (o de demostración) para visualización ambiental")

# ==================================================
# 🔧 OPCIÓN DEMO
# ==================================================
usar_datos_demo = st.checkbox("🔧 Usar datos de ejemplo (demo)", value=True)

# ==================================================
# 🌐 API OpenAQ
# ==================================================
BASE_URL = "https://api.openaq.org/v2/latest"

params = {
    "country": "MX",
    "limit": 200
}

headers = {
    "User-Agent": "Monitor-Contaminacion-Mexico"
}

try:
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    data = response.json().get("results", [])
except:
    data = []

# ==================================================
# 🔄 PROCESAMIENTO
# ==================================================
records = []

if data:
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
                "Contaminante": m.get("parameter", "").upper(),
                "Valor": m.get("value"),
                "Unidad": m.get("unit"),
                "Latitud": lat,
                "Longitud": lon
            })

df = pd.DataFrame(records)

# ==================================================
# 📦 DATOS DEMO SI NO HAY API
# ==================================================
if df.empty and usar_datos_demo:
    df = pd.DataFrame([
        {"Ciudad":"CDMX","Contaminante":"PM25","Valor":55,"Unidad":"µg/m³","Latitud":19.43,"Longitud":-99.13},
        {"Ciudad":"Guadalajara","Contaminante":"PM25","Valor":32,"Unidad":"µg/m³","Latitud":20.67,"Longitud":-103.35},
        {"Ciudad":"Monterrey","Contaminante":"PM25","Valor":41,"Unidad":"µg/m³","Latitud":25.68,"Longitud":-100.31},
        {"Ciudad":"León","Contaminante":"PM25","Valor":28,"Unidad":"µg/m³","Latitud":21.12,"Longitud":-101.68}
    ])

# ==================================================
# ⚠️ SI AÚN NO HAY DATOS
# ==================================================
if df.empty:
    st.warning("⚠️ No hay datos disponibles para mostrar.")
    st.stop()

# ==================================================
# 📊 TABLA GENERAL
# ==================================================
st.subheader("📊 Datos de Contaminación")
st.dataframe(df, use_container_width=True, hide_index=True)

# ==================================================
# 🧠 FUNCIÓN INTERPRETACIÓN
# ==================================================
def interpretar(param, valor):
    if param == "PM25":
        return "⚠️ Malo" if valor > 35 else "✅ Aceptable"
    if param == "PM10":
        return "⚠️ Malo" if valor > 50 else "✅ Aceptable"
    if param == "NO2":
        return "⚠️ Elevado" if valor > 200 else "✅ Normal"
    if param == "O3":
        return "⚠️ Elevado" if valor > 120 else "✅ Normal"
    if param == "CO":
        return "⚠️ Alto" if valor > 9 else "✅ Normal"
    if param == "SO2":
        return "⚠️ Alto" if valor > 75 else "✅ Normal"
    return "ℹ️ Monitoreo"

# ==================================================
# 🔍 SELECCIÓN DE CONTAMINANTE
# ==================================================
st.subheader("🔍 Análisis por contaminante")

contaminante = st.selectbox(
    "Selecciona un contaminante:",
    sorted(df["Contaminante"].unique())
)

df_f = df[df["Contaminante"] == contaminante].copy()
df_f["Estado"] = df_f["Valor"].apply(lambda v: interpretar(contaminante, v))

# ==================================================
# 📈 GRÁFICA
# ==================================================
st.subheader("📈 Niveles por ciudad")

fig, ax = plt.subplots()
ax.bar(df_f["Ciudad"], df_f["Valor"])
ax.set_ylabel(df_f["Unidad"].iloc[0])
ax.set_xlabel("Ciudad")
ax.set_title(f"Niveles de {contaminante}")
plt.xticks(rotation=45)

st.pyplot(fig)

# ==================================================
# 🧠 TABLA INTERPRETADA
# ==================================================
st.subheader("🧠 Interpretación automática")
st.dataframe(
    df_f[["Ciudad", "Valor", "Unidad", "Estado"]],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# 🗺️ MAPA MÉXICO
# ==================================================
st.subheader("🗺️ Mapa de contaminación en México")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_f,
    get_position="[Longitud, Latitud]",
    get_radius=9000,
    radius_min_pixels=6,
    radius_max_pixels=30,
    get_fill_color=[0, 120, 255, 180],
    pickable=True
)

view_state = pdk.ViewState(
    latitude=23.6345,
    longitude=-102.5528,
    zoom=5.3
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "Ciudad: {Ciudad}\nValor: {Valor} {Unidad}"}
)

st.pydeck_chart(deck)

st.success("✅ Aplicación funcionando correctamente")

























