import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
if MODO_MANTENIMIENTO:
    st.set_page_config(page_title="En mantenimiento", page_icon="🛠️")
    st.markdown(
        """
        <div style="
            text-align: center;
            margin-top: 100px;
            padding: 40px;
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
            color: #000000;
        ">
            <h1 style="color:#000000;">🛠️ Sitio en mantenimiento</h1>
            <p style="font-size:18px; color:#000000;">
                Lo sentimos, la aplicación está siendo actualizada.
            </p>
            <p style="font-size:16px; color:#000000;">
                Modificaciones en curso por <b>Antonio</b> 👨‍💻
            </p>
            <p style="color: #333333;">
                Vuelve en unos minutos 🚀
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()


# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Monitor de Contaminación - México",
    page_icon="🌎",
    layout="wide"
)

st.title("🌫️ Monitor de Contaminación del Aire")
st.write("Datos reales en tiempo casi real obtenidos desde **OpenAQ**")

# ---------------- SELECCIÓN DE REGIÓN ----------------
region = st.selectbox(
    "Selecciona la región:",
    ["Guanajuato", "México (todo el país)"]
)

# ---------------- API ----------------
BASE_URL = "https://api.openaq.org/v2/latest"

params = {
    "country": "MX",
    "limit": 200
}

if region == "Guanajuato":
    params["state"] = "Guanajuato"

headers = {
    "User-Agent": "Monitor-Contaminacion-Mexico",
    "From": "tucorreo@gmail.com"
}

try:
    response = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    data = response.json().get("results", [])
except:
    st.warning("❌ No se pudieron obtener los datos en este momento. Mostrando mapa vacío.")
    data = []

# ---------------- PROCESAMIENTO ----------------
records = []

if not data:
    # Creamos un registro ficticio para mostrar el mapa
    records.append({
        "Ciudad": "CDMX",
        "Estación": "Sin datos",
        "Contaminante": "PM25",
        "Valor": 0,
        "Unidad": "µg/m³",
        "Fecha": "",
        "Latitud": 19.432608,
        "Longitud": -99.133209
    })
else:
    for station in data:
        city = station.get("city", "Desconocido")
        location = station.get("location", "N/A")
        coords = station.get("coordinates", {})

        lat = coords.get("latitude")
        lon = coords.get("longitude")

        if lat is None or lon is None:
            continue

        for m in station["measurements"]:
            records.append({
                "Ciudad": city,
                "Estación": location,
                "Contaminante": m["parameter"].upper(),
                "Valor": m["value"],
                "Unidad": m["unit"],
                "Fecha": m["lastUpdated"],
                "Latitud": lat,
                "Longitud": lon
            })

df = pd.DataFrame(records)

# ---------------- TABLA ----------------
st.subheader("📊 Datos de Contaminación")
st.dataframe(df, use_container_width=True)

# ---------------- SELECCIÓN DE CONTAMINANTE ----------------
st.subheader("🔍 Análisis por contaminante")

contaminante = st.selectbox(
    "Selecciona un contaminante:",
    sorted(df["Contaminante"].unique())
)

df_f = df[df["Contaminante"] == contaminante]

# ---------------- GRÁFICA ----------------
st.subheader("📈 Niveles por ciudad")

fig, ax = plt.subplots()
ax.bar(df_f["Ciudad"], df_f["Valor"])
ax.set_ylabel(f"{df_f['Unidad'].iloc[0]}")
ax.set_xlabel("Ciudad")
ax.set_title(f"Niveles de {contaminante}")
plt.xticks(rotation=45)

st.pyplot(fig)

# ---------------- INTERPRETACIÓN ----------------
st.subheader("🧠 Interpretación automática")

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

df_f = df_f.copy()
df_f["Estado"] = df_f["Valor"].apply(lambda v: interpretar(contaminante, v))

st.dataframe(df_f[["Ciudad", "Valor", "Unidad", "Estado"]])

# ---------------- MAPA ----------------
st.subheader("🗺️ Mapa interactivo de contaminación")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_f,
    get_position="[Longitud, Latitud]",
    get_radius="Valor * 60",
    get_fill_color="[255, 80, 80, 160]",
    pickable=True
)

lat_mean = df_f["Latitud"].mean() if not df_f.empty else 19.432608
lon_mean = df_f["Longitud"].mean() if not df_f.empty else -99.133209

view_state = pdk.ViewState(
    latitude=lat_mean,
    longitude=lon_mean,
    zoom=6 if region == "Guanajuato" else 4
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "text": "Ciudad: {Ciudad}\nContaminante: {Contaminante}\nValor: {Valor} {Unidad}"
    }
)

st.pydeck_chart(deck)

st.success("✅ Aplicación funcionando perfectamente")









