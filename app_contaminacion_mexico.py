import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# ===============================
# MODO MANTENIMIENTO
# ===============================
MODO_MANTENIMIENTO = False  # Cambia a True cuando estés actualizando

if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:120px;
            padding:40px;
            background-color:white;
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
                Vuelve en unos minutos 🚀
            </p>
        </div>
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
st.write("Datos reales en tiempo casi real obtenidos desde **OpenAQ**")

# ===============================
# REGIÓN
# ===============================
region = st.selectbox(
    "📍 Selecciona región:",
    ["México (todo el país)", "Guanajuato"]
)

# ===============================
# API OpenAQ
# ===============================
url = "https://api.openaq.org/v2/latest"

params = {
    "country": "MX",
    "limit": 200
}

headers = {
    "User-Agent": "Monitor-Contaminacion-Mexico"
}

try:
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json().get("results", [])
except:
    data = []

# ===============================
# PROCESAMIENTO
# ===============================
registros = []

for estación in data:
    ciudad = estación.get("city", "Desconocido")
    coords = estación.get("coordinates", {})

    lat = coords.get("latitude")
    lon = coords.get("longitude")

    if lat is None or lon is None:
        continue

    for m in estación.get("measurements", []):
        registros.append({
            "Ciudad": ciudad,
            "Contaminante": m["parameter"].upper(),
            "Valor": m["value"],
            "Unidad": m["unit"],
            "Latitud": lat,
            "Longitud": lon
        })

df = pd.DataFrame(registros)

if df.empty:
    st.error("❌ No se pudieron cargar datos.")
    st.stop()

# ===============================
# FILTRO GUANAJUATO
# ===============================
if region == "Guanajuato":
    ciudades_gto = ["León", "Irapuato", "Celaya", "Salamanca", "Guanajuato"]
    df = df[df["Ciudad"].isin(ciudades_gto)]

# ===============================
# TABLA
# ===============================
st.subheader("📊 Datos de contaminación")
st.dataframe(df, use_container_width=True)

# ===============================
# CONTAMINANTE
# ===============================
contaminante = st.selectbox(
    "🔍 Selecciona contaminante:",
    sorted(df["Contaminante"].unique())
)

df_f = df[df["Contaminante"] == contaminante].copy()

# ===============================
# INTERPRETACIÓN
# ===============================
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

df_f["Estado"] = df_f["Valor"].apply(lambda v: interpretar(contaminante, v))

# ===============================
# GRÁFICA
# ===============================
st.subheader("📈 Niveles por ciudad")

fig, ax = plt.subplots()
ax.bar(df_f["Ciudad"], df_f["Valor"])
ax.set_ylabel(df_f["Unidad"].iloc[0])
ax.set_xlabel("Ciudad")
ax.set_title(f"Niveles de {contaminante}")
plt.xticks(rotation=45)

st.pyplot(fig)

# ===============================
# MAPA
# ===============================
st.subheader("🗺️ Mapa interactivo")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_f,
    get_position="[Longitud, Latitud]",
    get_radius=3000,
    get_fill_color="[0, 120, 255, 180]",
    pickable=True
)

if region == "Guanajuato":
    view_state = pdk.ViewState(
        latitude=21.12,
        longitude=-101.68,
        zoom=7.5
    )
else:
    view_state = pdk.ViewState(
        latitude=23.6345,
        longitude=-102.5528,
        zoom=5.3
    )

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "text": "Ciudad: {Ciudad}\nValor: {Valor} {Unidad}\nEstado: {Estado}"
    }
)

st.pydeck_chart(deck)

st.success("✅ Aplicación funcionando correctamente")



























