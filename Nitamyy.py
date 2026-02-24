import streamlit as st
import pandas as pd
import googlemaps

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Logística Iztapalapa", layout="wide")
st.title("🚚 Optimizador de Rutas y Flota")

# --- CARGA DE API KEY ---
try:
    API_KEY = st.secrets["MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ Error: Configura 'MAPS_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# --- DATOS DE LA FLOTA (Tu tabla optimizada) ---
flota_data = [
    {"nombre": "ISUZU 2", "capacidad": 6500, "costo_km": 3.42},
    {"nombre": "RAM 4000", "capacidad": 3500, "costo_km": 6.31},
    {"nombre": "ISUZU 1", "capacidad": 4000, "costo_km": 3.68},
    {"nombre": "VW CRAFTER", "capacidad": 1000, "costo_km": 1.76},
    {"nombre": "URVAN PANEL", "capacidad": 1350, "costo_km": 1.90},
    {"nombre": "CHEVROLET TORNADO", "capacidad": 650, "costo_km": 1.70}
]

# --- INTERFAZ DE USUARIO ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📋 Datos del Envío")
    origen = st.text_input("Salida (Dirección o Coordenadas)", "20 de Noviembre, Santa María Aztahuacán, Iztapalapa")
    
    st.info("💡 Puedes ingresar coordenadas como: 19.37, -99.09")
    destinos_input = st.text_area(
        "Destinos (Uno por línea)", 
        "Central de Abasto, Iztapalapa\n19.2842, -99.1358"
    )
    
    peso = st.number_input("Carga total (kg)", min_value=1, value=500)
    boton_calcular = st.button("🚀 Calcular Mejor Ruta")

with col2:
    st.subheader("🏁 Resultados y Mapa")
    
    if boton_calcular:
        # 1. Selección de Vehículo (Lógica de tu Colab)
        opciones = [v for v in flota_data if v['capacidad'] >= peso]
        
        if not opciones:
            st.error("❌ La carga excede la capacidad de nuestras unidades.")
        else:
            # Elegimos el de menor costo por kilómetro
            vehiculo_optimo = min(opciones, key=lambda x: x['costo_km'])
            
            # 2. Procesar lista de destinos
            lista_destinos = [d.strip() for d in destinos_input.split('\n') if d.strip()]
            
            try:
                # 3. Llamada a Google Maps
                # Usamos Directions API para obtener el trazado
                res = gmaps.directions(
                    origen, 
                    lista_destinos[-1], 
                    waypoints=lista_destinos[:-1] if len(lista_destinos) > 1 else None,
                    optimize_waypoints=True,
                    mode="driving",
                    language="es"
                )

                if res:
                    st.success(f"✅ UNIDAD RECOMENDADA: **{vehiculo_optimo['nombre']}**")
                    
                    # Cálculo de distancia y costos
                    total_km = sum(leg['distance']['value'] for leg in res[0]['legs']) / 1000
                    costo_total = total_km * vehiculo_optimo['costo_km']
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Distancia Total", f"{round(total_km, 2)} KM")
                    c2.metric("Costo de Viaje", f"${round(costo_total, 2)} MXN")

                    # 4. BOTÓN DE NAVEGACIÓN REAL
                    # Este link abre Google Maps en el celular con toda la ruta cargada
                    puntos_ruta = "|".join(lista_destinos)
                    url_google = f"https://www.google.com/maps/dir/?api=1&origin={origen}&destination={lista_destinos[-1]}&waypoints={puntos_ruta if len(lista_destinos)>1 else ''}&travelmode=driving"
                    
                    st.link_button("🗺️ Abrir Guía de Navegación (GPS)", url_google)

                    # Detalle del recorrido
                    with st.expander("Ver pasos de la ruta"):
                        for i, leg in enumerate(res[0]['legs']):
                            st.write(f"**Tramo {i+1}:** {leg['distance']['text']}")
                            st.caption(f"De: {leg['start_address']} a {leg['end_address']}")
                else:
                    st.warning("No se pudo calcular la ruta. Revisa las direcciones o coordenadas.")

            except Exception as e:
                st.error(f"Error de conexión con Google Maps: {e}")
    else:
        st.info("Ingresa los datos y presiona el botón para optimizar.")
