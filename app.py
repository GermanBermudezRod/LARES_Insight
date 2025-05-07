import streamlit as st
import pandas as pd
import os
import pydeck as pdk
from src.geolocation import get_coordinates
from src.places_search import get_cached_or_query_places

CSV_PATH = "data/nearby_competitors.csv"

st.set_page_config(page_title="Comparador de alojamientos", layout="wide")
st.title("\U0001F3E1 Comparador de alojamientos rurales")

# Inicializar estado
if "coords" not in st.session_state:
    st.session_state.coords = None
if "competitors" not in st.session_state:
    st.session_state.competitors = pd.DataFrame()
if "selected" not in st.session_state:
    st.session_state.selected = []
if "temp_selected" not in st.session_state:
    st.session_state.temp_selected = []

# Paso 1: Formulario
with st.form("search_form"):
    user_input = st.text_input("Introduce el nombre de tu alojamiento o zona:", "A mayor precisión, mejores resultados")
    st.markdown("Ejemplo: `Casa rural X en la Sierra de Guadarrama`")
    search_radius = st.slider("Selecciona el radio de búsqueda (km):", 1, 50, 15)
    submitted = st.form_submit_button("\U0001F50D Buscar competencia")

# Paso 2: Procesar búsqueda
if submitted:
    coords = get_coordinates(user_input)
    if coords:
        st.session_state.coords = coords
        st.success(f"\U0001F4CD Coordenadas encontradas: {coords}")

        results = get_cached_or_query_places(coords[0], coords[1], radius_m=search_radius * 1000)
        df_results = pd.DataFrame(results)
        df_results = df_results[
            ~(
                (df_results["origin_lat"].round(6) == df_results["lat"].round(6)) &
                (df_results["origin_lon"].round(6) == df_results["lon"].round(6))
            )
        ]
        st.session_state.competitors = df_results

        df_results = df_results.rename(columns={"origin_lat": "query_lat", "origin_lon": "query_lon"})

        if os.path.exists(CSV_PATH):
            df_old = pd.read_csv(CSV_PATH)
            df_old = df_old.loc[:, ~df_old.columns.duplicated()]
        else:
            df_old = pd.DataFrame()

        missing_cols = set(df_old.columns) - set(df_results.columns)
        for col in missing_cols:
            df_results[col] = None

        df_results = df_results[df_old.columns] if not df_old.empty else df_results

        df_combined = pd.concat([df_old, df_results], ignore_index=True)
        if "place_id" in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset="place_id", keep="first")

        df_combined.to_csv(CSV_PATH, index=False)
        st.session_state.selected = df_results["name"].tolist()[:3]
        st.session_state.temp_selected = st.session_state.selected.copy()
    else:
        st.error("❌ No se encontraron coordenadas para ese lugar.")
        st.session_state.coords = None
        st.session_state.competitors = pd.DataFrame()

# Paso 3: Mostrar resultados
if not st.session_state.competitors.empty:
    st.write("### \U0001F3D8️ Alojamientos encontrados:")

    cols = st.columns(4)
    new_selection = []

    for idx, (i, row) in enumerate(st.session_state.competitors.iterrows()):
        with cols[idx % 4]:
            checked = row["name"] in st.session_state.temp_selected
            box = st.checkbox(f"**{row['name']}**", value=checked, key=f"hotel_{i}")
            if box:
                new_selection.append(row["name"])

    confirm = st.button("✅ Confirmar selección")
    if confirm:
        st.session_state.selected = new_selection
        st.session_state.temp_selected = new_selection

    if st.session_state.selected:
        st.write("### 🔍 Alojamientos seleccionados:")
        for hotel in st.session_state.selected:
            row = st.session_state.competitors[st.session_state.competitors["name"] == hotel]
            if not row.empty:
                address = row.iloc[0]["address"]
                st.markdown(f"- **{hotel}** – {address}")

        if "lat" in st.session_state.competitors.columns and "lon" in st.session_state.competitors.columns:
            query_marker = {
                "name": "Tu alojamiento",
                "latitude": st.session_state.coords[0],
                "longitude": st.session_state.coords[1],
                "color_r": 0,
                "color_g": 100,
                "color_b": 255,
                "size": 150
            }

            competitor_markers = []
            for _, row in st.session_state.competitors.iterrows():
                if row["name"] in st.session_state.selected and pd.notna(row["lat"]) and pd.notna(row["lon"]):
                    competitor_markers.append({
                        "name": row["name"],
                        "latitude": row["lat"],
                        "longitude": row["lon"],
                        "color_r": 200,
                        "color_g": 30,
                        "color_b": 30,
                        "size": 100
                    })

            map_df = pd.DataFrame([query_marker] + competitor_markers)

            st.write("### 🗺️ Mapa de alojamientos seleccionados")
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/streets-v12",
                initial_view_state=pdk.ViewState(
                    latitude=query_marker["latitude"],
                    longitude=query_marker["longitude"],
                    zoom=11,
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df,
                        get_position='[longitude, latitude]',
                        get_radius="size",
                        get_color='[color_r, color_g, color_b]',
                        pickable=True
                    )
                ],
                tooltip={"text": "{name}"}
            ))
        else:
            st.warning("No se encontraron coordenadas reales para los alojamientos seleccionados.")
    else:
        st.warning("Selecciona al menos un alojamiento y pulsa 'Confirmar selección'.")

st.markdown("---")
st.caption("Versión estable · Streamlit · 2025")
st.markdown("Desarrollado por Germán Bermúdez Rodríguez - [GitHub](https://github.com/GermanBermudezRod) · [LinkedIn](https://www.linkedin.com/in/german-bermudez-rodriguez/)")
