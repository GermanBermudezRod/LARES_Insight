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
if "competitors" not in st.session_state:
    st.session_state.competitors = pd.DataFrame()
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
        st.session_state.competitors = df_results

        # Renombrar columnas duplicadas si hace falta
        df_results = df_results.rename(columns={"origin_lat": "query_lat", "origin_lon": "query_lon"})

        # Cargar CSV antiguo y asegurarse de que no haya columnas duplicadas
        if os.path.exists(CSV_PATH):
            df_old = pd.read_csv(CSV_PATH)
            df_old = df_old.loc[:, ~df_old.columns.duplicated()]  # Eliminar columnas duplicadas
        else:
            df_old = pd.DataFrame()

        # Añadir columnas faltantes al nuevo DataFrame
        missing_cols = set(df_old.columns) - set(df_results.columns)
        for col in missing_cols:
            df_results[col] = None

        # Igualar orden de columnas
        df_results = df_results[df_old.columns] if not df_old.empty else df_results

        # Combinar y quitar duplicados
        df_combined = pd.concat([df_old, df_results], ignore_index=True)
        if "place_id" in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset="place_id", keep="first")

        # Guardar actualizado
        df_combined.to_csv(CSV_PATH, index=False)

        # Guardar selección inicial
        st.session_state.selected = df_results["name"].tolist()[:3]

    else:
        st.error("❌ No se encontraron coordenadas para ese lugar.")
        st.session_state.coords = None
        st.session_state.competitors = pd.DataFrame()

# Paso 3: Mostrar resultados
if not st.session_state.competitors.empty:
    st.write("### ✅ Alojamientos encontrados:")

    options = st.session_state.competitors["name"].tolist()
    selected_hotels = st.multiselect(
        "Selecciona los alojamientos con los que deseas comparar tu establecimiento:",
        options=options,
        default=st.session_state.selected
    )
    st.session_state.selected = selected_hotels

    if selected_hotels:
        st.write("### 🔍 Alojamientos seleccionados:")
        for hotel in selected_hotels:
            row = st.session_state.competitors[st.session_state.competitors["name"] == hotel]
            if not row.empty:
                address = row.iloc[0]["address"]
                st.markdown(f"- **{hotel}** – {address}")

        # Mostrar mapa con coordenadas reales
        if "lat" in st.session_state.competitors.columns and "lon" in st.session_state.competitors.columns:
            map_df = st.session_state.competitors[st.session_state.competitors["name"].isin(selected_hotels)][["lat", "lon"]]
            map_df = map_df.rename(columns={"lat": "latitude", "lon": "longitude"})
            st.write("### 🗺️ Mapa de alojamientos seleccionados")
            st.map(map_df)
        else:
            st.warning("No se encontraron coordenadas reales para los alojamientos seleccionados.")
    else:
        st.warning("Selecciona al menos un alojamiento para continuar.")

st.markdown("---")
st.caption("Versión estable · Streamlit · 2025")
st.markdown("Desarrollado por Germán Bermúdez Rodríguez - [GitHub](https://github.com/GermanBermudezRod) · [LinkedIn](https://www.linkedin.com/in/german-bermudez-rodriguez/)")
