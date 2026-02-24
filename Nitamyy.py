import streamlit as st
import pandas as pd
import googlemaps

# Configuración de página
st.set_page_config(page_title="Logística Iztapalapa", layout="wide")
st.title("🚚 Optimizador de Rutas y Flota")

# Conexión Segura a Google Maps (Usando Secrets)
try:
    API_KEY = st.secrets["MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ Error: No se encontró la clave de Google Maps en los 'Secrets'.")
    st.stop()

# Datos de tu flota
flota_data = [
    {"Vehículo": "ISUZU 2 - 6 1/2", "Capacidad": 6500, "Rendimiento": 7.00},
    {"Vehículo": "RAM 4000", "Capacidad": 3500, "Rendimiento": 3.80},
    {"Vehículo": "ISUZU 1- 4 1/2", "Capacidad": 4000, "Rendimiento": 6.52},
    {"Vehículo": "VW CRAFTER", "Capacidad": 1000, "Rendimiento": 13.58},
    {"Vehículo": "URVAN PANEL", "Capacidad": 1350, "Rendimiento": 12.61},
    {"Vehículo": "CHEVROLET TORNADO", "Capacidad": 650, "Rendimiento": 14.10}
]
df_flota = pd.DataFrame(flota_data)

# Interfaz de usuario
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📋 Datos del Envío")
    origen = st.text_input("Salida", "20 de Noviembre, Santa María Aztahuacán, Iztapalapa")
    destinos_input = st.text_area("Destinos (uno por línea)", "Central de Abasto, Iztapalapa\nEcatepec Centro")
    peso = st.number_input("Carga total (kg)", min_value=1, value=500)

with col2:
    st.subheader("🏁 Resultados")
    if st.button("Calcular Mejor Ruta"):
        opciones = df_flota[df_flota["Capacidad"] >= peso]
        if opciones.empty:
            st.error("❌ Carga demasiado pesada.")
        else:
            vehiculo = opciones.sort_values("Rendimiento", ascending=False).iloc[0]
            destinos = [d.strip() for d in destinos_input.split('\n') if d.strip()]
            
            try:
                # Calcular ruta
                ruta = gmaps.directions(origen, destinos[-1], waypoints=destinos[:-1], optimize_waypoints=True, mode="driving", language="es")
                
                if ruta:
                    st.success(f"✅ Unidad asignada: **{vehiculo['Vehículo']}**")
                    total_km = sum(leg['distance']['value'] for leg in ruta[0]['legs']) / 1000
                    st.metric("Distancia Total", f"{round(total_km, 2)} KM")
                    st.metric("Costo Gasolina Estimado", f"${round((total_km/vehiculo['Rendimiento'])*24, 2)} MXN")
            except Exception as e:
                st.error(f"Error de Google Maps: {e}")
