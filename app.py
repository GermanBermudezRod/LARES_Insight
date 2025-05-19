import streamlit as st
import pandas as pd
import os
import pydeck as pdk
import time
from src.geolocation import get_coordinates
from src.places_search import get_cached_or_query_places
from src.scraper_selenium import get_price_from_booking
from src.extract_additional_info import extract_extras_from_html
from src.extract_own_features import extract_own_features_from_booking
from src.price_recommender import recomendar_precio
from src.scraper_selenium import guardar_html_de_booking


CSV_PATH = "data/nearby_competitors.csv"

st.set_page_config(page_title="Comparador de alojamientos", layout="wide")

# Estilos personalizados de Lares Gestión
st.image("data/5.png", width=200)
st.markdown("""
    <style>
    /* ====== CONFIGURACIÓN GENERAL ====== */
    body, .stApp {
        background-color: #F4F6FA;
        color: #1E1E1E;
        font-family: 'Segoe UI', sans-serif;
    }

    .stApp {
        padding-top: 100px !important;
        padding-left: 160px !important;
    }

    /* ====== LOGO FIJO IZQUIERDA ====== */
    .fixed-logo {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        width: 140px !important;
        z-index: 100 !important;
    }

    /* ====== TÍTULOS ====== */
    h1, h2, h3, h4, h5, h6 {
        color: #0076FF !important;
        font-weight: 700;
    }

    /* ====== TEXTOS GENERALES ====== */
    .stMarkdown, .stText, .stCaption, label, .css-1cpxqw2, .css-10trblm {
        color: #1E1E1E !important;
        font-size: 16px !important;
    }

    /* ====== ENTRADAS DE TEXTO Y SELECTS ====== */
    input, textarea {
        background-color: white !important;
        color: #1E1E1E !important;
        border: 1px solid #D0D7DE !important;
        border-radius: 6px !important;
    }

    /* ====== SLIDER ====== */
    .stSlider > div {
        background-color: transparent !important;
        color: #1E1E1E !important;
    }

    /* ====== CHECKBOXES (solución de visibilidad) ====== */
    .stCheckbox > div {
        background-color: #ffffff !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        color: #1E1E1E !important;
    }

    .stCheckbox > div label {
        color: #1E1E1E !important;
        font-weight: 500 !important;
    }

    .stCheckbox > div:hover {
        background-color: #E4F1FF !important;
        border-color: #0076FF !important;
    }

    /* ====== BOTONES ====== */
    button {
        background-color: #0076FF !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.6em 1.2em !important;
        border: none !important;
        transition: background-color 0.3s ease;
    }

    button:hover {
        background-color: #005EDC !important;
        color: white !important;
    }

    /* ====== MENSAJES DE ALERTA ====== */
    .stAlert {
        border-radius: 8px !important;
        font-size: 15px;
        color: #1E1E1E !important;
    }

    /* ====== TABLAS Y DATAFRAMES ====== */
    .css-1d391kg, .css-1v0mbdj {
        background-color: white !important;
        color: #1E1E1E !important;
    }

    /* ====== TOOLTIP DEL MAPA ====== */
    .deck-tooltip {
        font-size: 14px;
        background-color: rgba(0, 118, 255, 0.9);
        color: white;
        padding: 5px;
        border-radius: 5px;
    }
            
    /* Forzar el color del texto dentro de los checkboxes */
    .stCheckbox p,
    .stCheckbox label,
    .stCheckbox div[data-testid="stMarkdownContainer"] {
        color: #0076FF !important;  /* o #1A1A1A si prefieres el azul corporativo */
    }

    .stAlert p,
    .stAlert label,
    .stAlert div[data-testid="stMarkdownContainer"] {
        color: #1A1A1A !important;  /* o #1A1A1A si prefieres el azul corporativo */
    }
    </style>

    <a href="https://www.laresgestion.com" target="_blank">
        <img src="https://imgur.com/gallery/two-day-old-baby-giraffe-5QI5O3B" class="fixed-logo">
    </a>
""", unsafe_allow_html=True)

st.title("🏡 Comparador de alojamientos rurales")

def lanzar_scraper_para_seleccionados(df, seleccionados):
    progress_placeholder = st.empty()
    errores = []
    total = len([r for r in df.iterrows() if r[1]["name"] in seleccionados])
    contador = 0

    for index, row in df.iterrows():
        if row["name"] not in seleccionados:
            continue
        contador += 1

        progress_html = f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 12px 0;">
            <div style="width: 22px; height: 22px; border: 3px solid #0076FF; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <span style="font-weight: 500; color: #0076FF;">Analizando alojamiento {contador} de {total}...</span>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """
        progress_placeholder.markdown(progress_html, unsafe_allow_html=True)

        st.write(f"\U0001F50D Obteniendo precios de: **{row['name']}**")
        try:
            price_min, price_max, price_avg = get_price_from_booking(row["name"])
            df.loc[index, "price_min"] = price_min
            df.loc[index, "price_max"] = price_max
            df.loc[index, "price_avg"] = price_avg

            if price_min is not None:
                st.success(f"✅ {row['name']} ➜ Mín: {price_min} € · Máx: {price_max} € · Media: {price_avg} €")
            else:
                st.warning(f"⚠️ {row['name']} no tiene precios visibles.")
        except Exception as e:
            errores.append((row["name"], str(e)))
            st.error(f"❌ Error con {row['name']}: {e}")

        try:
            extras = extract_extras_from_html(row["name"])
            for key, value in extras.items():
                if key not in df.columns:
                    df[key] = None
                df.at[index, key] = value
        except Exception as e:
            st.warning(f"⚠️ No se pudieron extraer extras de {row['name']}: {e}")

        time.sleep(2.5)

    df.to_csv(CSV_PATH, index=False)
    st.session_state.competitors = df.copy()

    progress_placeholder.markdown(
        "<span style='color: #0076FF; font-weight: 600;'>✅ Análisis completado con éxito.</span>",
        unsafe_allow_html=True
    )
    time.sleep(2)
    progress_placeholder.empty()
    st.session_state.scraping_completado = True
    
# Estado inicial
if "coords" not in st.session_state:
    st.session_state.coords = None
if "competitors" not in st.session_state:
    st.session_state.competitors = pd.DataFrame()
if "selected" not in st.session_state:
    st.session_state.selected = []
if "temp_selected" not in st.session_state:
    st.session_state.temp_selected = []
    if "scraping_completado" not in st.session_state:
        st.session_state.scraping_completado = False

# Paso 1: Formulario
if "buscando_competidores" not in st.session_state:
    st.session_state.buscando_competidores = False

with st.form("search_form"):
    user_input = st.text_input("Introduce el nombre de tu alojamiento o zona:", placeholder="A mayor precisión, mejores resultados")
    st.markdown("Ejemplo: `Casa rural X en la Sierra de Guadarrama`")
    search_radius = st.slider("Selecciona el radio de búsqueda (km):", 1, 50, 15)
    submitted = st.form_submit_button("🔍 Buscar competencia")

# Paso 2: Procesar búsqueda
if submitted:
    st.session_state.buscando_competidores = True

    with st.spinner(" Buscando competidores..."):
        coords = get_coordinates(user_input)
        if coords:
            # Guardar HTML del propio alojamiento
            guardar_html_de_booking(user_input)
            
            st.session_state.coords = coords
            #st.success("📍 Coordenadas del alojamiento encontradas")

            # Obtener y mostrar características del alojamiento propio
            own_data = extract_own_features_from_booking(user_input)
            st.session_state.own_data = own_data

            # DEBUG TEMPORAL: Mostrar own_data extraído
            st.write("📊 DEBUG - Datos del alojamiento propio extraídos:", own_data)

            #if own_data:
                #st.markdown("### 🧾 Características detectadas de tu alojamiento:")
                #st.markdown(f"📍 <b>Nombre:</b> {user_input}", unsafe_allow_html=True)
                #if "rating" in own_data:
                    #st.markdown(f"⭐ <b>Puntuación:</b> {own_data['rating']}", unsafe_allow_html=True)
                #if "total_reviews" in own_data:
                    #st.markdown(f"🗣️ <b>Opiniones:</b> {own_data['total_reviews']}", unsafe_allow_html=True)
                #if "num_rooms" in own_data:
                    #st.markdown(f"🛏️ <b>Habitaciones:</b> {own_data['num_rooms']}", unsafe_allow_html=True)
                #if "max_capacity" in own_data:
                    #st.markdown(f"👥 <b>Capacidad máxima:</b> {own_data['max_capacity']}", unsafe_allow_html=True)
                #if own_data.get("extras"):
                    #st.markdown("🎁 <b>Servicios detectados:</b>", unsafe_allow_html=True)
                    #for s in own_data["extras"]:
                        #st.markdown(f"✅ {s.capitalize()}")

            # Obtener y mostrar características de competidores
            results = get_cached_or_query_places(coords[0], coords[1], radius_m=search_radius * 1000)
            df_results = pd.DataFrame(results)
            df_results = df_results[
                ~((df_results["origin_lat"].round(6) == df_results["lat"].round(6)) &
                (df_results["origin_lon"].round(6) == df_results["lon"].round(6)))
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

    # Desactivar bandera
    st.session_state.buscando_competidores = False

# Paso 3: Mostrar resultados
if st.session_state.buscando_competidores:
    with st.spinner("🔄 Buscando competidores..."):
        time.sleep(0.5)

if not st.session_state.competitors.empty:
    st.write("### 🏘️ Alojamientos encontrados:")

    cols = st.columns(4)
    new_selection = []

    st.session_state.buscando_competidores = False

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
                st.markdown(f"- **{hotel}** – {row.iloc[0]['address']}")

        # Mapa de alojamientos
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
                layers=[pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position='[longitude, latitude]',
                    get_radius="size",
                    get_color='[color_r, color_g, color_b]',
                    pickable=True
                )],
                tooltip={"text": "{name}"}
            ))
        else:
            st.warning("No se encontraron coordenadas reales para los alojamientos seleccionados.")

        # BOTÓN DE SCRAPING
        if st.button("🚀 Ejecutar análisis de precios"):
            lanzar_scraper_para_seleccionados(st.session_state.competitors, st.session_state.selected)
            st.session_state.scraping_completado = True

    # ✅ Mostramos extras y recomendación si ya se ha hecho el scraping
    if st.session_state.get("scraping_completado", False):
        st.write("### 🧾 Resultados detallados por alojamiento:")

        for _, row in st.session_state.competitors[st.session_state.competitors["name"].isin(st.session_state.selected)].iterrows():
            badges = []

            if "cancelacion" in row and pd.notnull(row["cancelacion"]):
                badges.append(f"📌 <b>Cancelación:</b> {row['cancelacion']}")
            if "mascotas" in row:
                badges.append(f"🐶 <b>Mascotas:</b> {row['mascotas']}")
            if row.get("cunas") == "Sí":
                badges.append("🛏️ <b>Cunas disponibles</b>")
            if row.get("camas_supletorias") == "Sí":
                badges.append("🛏️ <b>Camas supletorias</b>")
            if "costo_extra" in row:
                badges.append(f"💰 <b>Coste adicional:</b> {row['costo_extra']}")
            for col in row.index:
                if col.startswith("servicio_") and row[col] == "Sí":
                    nombre = col.replace("servicio_", "").capitalize()
                    badges.append(f"✅ {nombre}")

            badge_html = "".join([
                f"""<div style="flex: 0 1 auto; background-color: #F0F4FF; color: #1A1A1A; padding: 8px 12px; border-radius: 8px;
                    border: 1px solid #D0D7DE; font-size: 14px; margin: 4px;">
                    {item}</div>""" for item in badges
            ])

            html = f"""
            <div style="background-color: white; border: 1px solid #D0D7DE; border-radius: 10px; padding: 20px; margin-bottom: 20px; max-width: 1000px;">
                <h4 style="color: #0076FF;">🏨 {row['name']}</h4>
                <p><b>💶 Precios:</b> {"Mín: {} € · Media: {} € · Máx: {} €".format(row['price_min'], row['price_avg'], row['price_max']) if pd.notnull(row['price_min']) else "No disponibles"}</p>
                <p><b>🎁 Extras detectados:</b></p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">{badge_html}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

        # ✅ Recomendación IA
        if "own_data" in st.session_state and st.session_state.own_data and st.session_state.selected:
            st.markdown("### 💡 Recomendación de precio para tu alojamiento")

            own = st.session_state.own_data
            df_comp = st.session_state.competitors
            competidores_filtrados = df_comp[df_comp["name"].isin(st.session_state.selected)]

            try:
                # Si no existe la columna 'guest_rating', asumimos mismo valor que el alojamiento propio
                if "guest_rating" not in competidores_filtrados.columns:
                    competidores_filtrados["guest_rating"] = own.get("rating", 0)

                precio_min, precio_max, razon = recomendar_precio(own, competidores_filtrados)

                st.markdown(f"""
                <div style="background-color: #F0FFF0; border: 2px solid #0076FF; padding: 16px; border-radius: 12px;">
                    <h4 style="color: #0076FF;">💶 Rango recomendado: <span style="color:#1E1E1E">{precio_min:.2f} € - {precio_max:.2f} €</span></h4>
                    <p style="margin-top:10px;">🧠 <b>Motivo:</b> {razon}</p>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"No se pudo generar una recomendación: {e}")


st.markdown("---")
st.caption("Versión estable · Streamlit · 2025")
st.markdown("Desarrollado por Germán Bermúdez Rodríguez - [GitHub](https://github.com/GermanBermudezRod) · [LinkedIn](https://www.linkedin.com/in/german-bermudez-rodriguez/)")

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("❌ Cerrar aplicación"):
        st.warning("Cerrando aplicación...")
        time.sleep(1)
        os._exit(0)
