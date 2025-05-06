import streamlit as st
import pandas as pd
import os
from src.geolocation import get_coordinates
from src.places_search import get_cached_or_query_places

CSV_PATH = "data/nearby_competitors.csv"

st.set_page_config(page_title="Comparador de alojamientos", layout="wide")
st.title("🏡 Comparador de alojamientos rurales")

# Inicializar estado
if "coords" not in st.session_state:
    st.session_state.coords = None
if "selected" not in st.session_state:
    st.session_state.selected = []

# Paso 1: Formulario
with st.form("search_form"):
    user_input = st.text_input("Introduce el nombre de tu alojamiento o zona:", "Lagunas de Ruidera")
    search_radius = st.slider("Selecciona el radio de búsqueda (km):", 1, 50, 15)
    submitted = st.form_submit_button("🔍 Buscar competencia")

# Paso 2: Procesar búsqueda
if submitted:
    coords = get_coordinates(user_input)
    if coords:
        st.session_state.coords = coords
        st.success(f"📍 Coordenadas encontradas: {coords}")

        # Llamada real a Google Places
        results = get_cached_or_query_places(coords[0], coords[1], radius_m=search_radius * 1000)
        df_results = pd.DataFrame(results)

        # Actualizar CSV general
        if os.path.exists(CSV_PATH):
            df_old = pd.read_csv(CSV_PATH)
            df_combined = pd.concat([df_old, df_results], ignore_index=True).drop_duplicates(subset="place_id")
        else:
            df_combined = df_results
        df_combined.to_csv(CSV_PATH, index=False)

        st.session_state.selected = df_results["name"].tolist()[:3]
    else:
        st.error("❌ No se encontraron coordenadas para ese lugar.")
        st.session_state.coords = None
        st.session_state.selected = []

# Paso 3: Mostrar resultados si hay seleccionados
if os.path.exists(CSV_PATH):
    df_all = pd.read_csv(CSV_PATH)

    if not df_all.empty:
        st.write("### ✅ Alojamientos encontrados:")
        options = df_all["name"].dropna().unique().tolist()

        selected_hotels = st.multiselect(
            "Selecciona los alojamientos con los que deseas comparar tu establecimiento:",
            options=options,
            default=st.session_state.selected,
            key="selection_multiselect"
        )
        st.session_state.selected = selected_hotels

        if selected_hotels:
            st.write("### 🔍 Alojamientos seleccionados:")
            df_selected = df_all[df_all["name"].isin(selected_hotels)]

            for _, row in df_selected.iterrows():
                st.markdown(f"- **{row['name']}** – {row.get('address', 'Sin dirección')}")

            if {"lat", "lon"}.issubset(df_selected.columns):
                map_df = df_selected.rename(columns={"lat": "latitude", "lon": "longitude"})
            elif {"latitude", "longitude"}.issubset(df_selected.columns):
                map_df = df_selected
            else:
                st.warning("No se pueden mostrar las ubicaciones en el mapa. Faltan columnas de coordenadas.")
                map_df = pd.DataFrame(columns=["latitude", "longitude"])

            if not map_df.empty:
                st.write("### 🗺️ Mapa de alojamientos seleccionados")
                st.map(map_df[["latitude", "longitude"]])
        else:
            st.warning("Selecciona al menos un alojamiento para continuar.")

st.markdown("---")
st.caption("Versión estable · Streamlit · 2025")
st.markdown("Desarrollado por Germán Bermúdez Rodríguez - [GitHub](https://github.com/GermanBermudezRod) · [LinkedIn](https://www.linkedin.com/in/german-bermudez-rodriguez/)")
