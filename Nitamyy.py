import streamlit as st
import pandas as pd
import googlemaps

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Logística Iztapalapa", layout="wide")
st.title("🚚 Optimizador de Rutas y Flota")

# --- CARGA SEGURA DE API ---
try:
    API_KEY = st.secrets["MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ Error: Configura 'MAPS_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- DATOS DE LA FLOTA ---
flota_data = [
    {"nombre": "ISUZU 2", "capacidad": 6500, "costo_km": 3.42},
    {"nombre": "RAM 4000", "capacidad": 3500, "costo_km": 6.31},
    {"nombre": "ISUZU 1", "capacidad": 4000, "costo_km": 3.68},
    {"nombre": "VW CRAFTER", "capacidad": 1000, "costo_km": 1.76},
    {"nombre": "URVAN PANEL", "capacidad": 1350, "costo_km": 1.90},
    {"nombre": "CHEVROLET TORNADO", "capacidad": 650, "costo_km": 1.70}
]

# --- INTERFAZ ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📋 Datos del Envío")
    origen = st.text_input("Salida (Dirección o Coordenadas)", "20 de Noviembre, Santa María Aztahuacán, Iztapalapa")
    destinos_input = st.text_area("Destinos (Uno por línea. Acepta coordenadas lat, long)", "Central de Abasto, Iztapalapa\n19.2842, -99.1358")
    peso = st.number_input("Carga total (kg)", min_value=1, value=500)
    boton = st.button("🚀 Calcular Mejor Ruta")

with col2:
    st.subheader("🏁 Resultados y Mapa")
    if boton:
        # 1. Lógica de selección de vehículo (Tu código de Colab)
        opciones = [v for v in flota_data if v['capacidad'] >= peso]
        
        if not opciones:
            st.error("❌ Carga demasiado pesada para un solo vehículo.")
        else:
            # Seleccionar el de menor costo_km (Rendimiento)
            recomendado = min(opciones, key=lambda x: x['costo_km'])
            
            # 2. Procesar destinos
            lista_destinos = [d.strip() for d in destinos_input.split('\n') if d.strip()]
            
            try:
                # 3. Obtener Ruta de Google
                res = gmaps.directions(
                    origen, 
                    lista_destinos[-1], 
                    waypoints=lista_destinos[:-1] if len(lista_destinos) > 1 else None,
                    optimize_waypoints=True,
                    mode="driving",
                    language="es"
                )

                if res:
                    # MOSTRAR RESULTADOS
                    st.success(f"✅ VEHÍCULO ÓPTIMO: **{recomendado['nombre']}**")
                    
                    # Calcular KM totales
                    total_km = sum(leg['distance']['value'] for leg in res[0]['legs']) / 1000
                    costo_total = total_km * recomendado['costo_km']

                    st.metric("Distancia Total", f"{round(total_km, 2)} KM")
                    st.metric("Costo Estimado", f"${round(costo_total, 2)} MXN")

                    # BOTÓN DE MAPA REAL
                    # Generar link para Google Maps App
                    url_mapa = f"https://www.google.com/maps/dir/?api=1&origin={origen}&destination={lista_destinos[-1]}"
                    if len(lista_destinos) > 1:
                        url_mapa += f"&waypoints={'|'.join(lista_destinos[:-1])}"
                    
                    st.link_button("🗺️ Abrir Navegación Paso a Paso", url_mapa)
                    
                    # Detalle de tramos
                    with
