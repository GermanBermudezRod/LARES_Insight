from geopy.geocoders import GoogleV3
from geopy.distance import geodesic
from dotenv import load_dotenv
import pandas as pd
import os

# Cargar claves desde .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicializar geolocalizador de Google
geolocator = GoogleV3(api_key=API_KEY)

# Ruta del archivo CSV que guarda las coordenadas cacheadas
CACHE_FILE = "data/coordinates_cache.csv"

# Asegurarse de que el CSV exista (si no, se crea)
if not os.path.exists(CACHE_FILE):
    df = pd.DataFrame(columns=["name", "latitude", "longitude", "address"])
    df.to_csv(CACHE_FILE, index=False)

def get_coordinates(name):
    """
    Devuelve las coordenadas de un alojamiento:
    - Busca primero en el CSV local (con coordenadas y zona)
    - Si no está, lo consulta en la API de Google y guarda el resultado incluyendo la zona
    - Si está pero no tiene zona (address), actualiza esa fila
    """
    df = pd.read_csv(CACHE_FILE)

    # Buscar en el CSV si ya existe
    row_idx = df[df["name"].str.lower() == name.lower()].index
    if not row_idx.empty:
        idx = row_idx[0]
        lat = df.at[idx, "latitude"]
        lon = df.at[idx, "longitude"]

        # Si falta la address, buscarla y actualizar
        if "address" not in df.columns or pd.isna(df.at[idx, "address"]):
            location = geolocator.reverse((lat, lon), exactly_one=True)
            address = None
            if location and location.raw and "address_components" in location.raw:
                for component in location.raw["address_components"]:
                    if "locality" in component["types"]:
                        address = component["long_name"]
                        break
                    elif "administrative_area_level_2" in component["types"]:
                        address = component["long_name"]

            df.at[idx, "address"] = address
            df.to_csv(CACHE_FILE, index=False)

        return (lat, lon)

    # Si no está en el CSV, buscar en la API
    location = geolocator.geocode(name)
    if location:
        lat, lon = location.latitude, location.longitude

        # Obtener también la zona/localidad (ciudad, pueblo...)
        address = None
        if location.raw and "address_components" in location.raw:
            for component in location.raw["address_components"]:
                if "locality" in component["types"]:
                    address = component["long_name"]
                    break
                elif "administrative_area_level_2" in component["types"]:
                    address = component["long_name"]

        # Construir nueva fila con zona
        new_row = pd.DataFrame([{
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "address": address
        }])

        # Asegurar que zona está en el CSV
        if "address" not in df.columns:
            df["address"] = None

        new_row.to_csv(CACHE_FILE, mode="a", header=False, index=False)
        return (lat, lon)

    else:
        return None

def calculate_distance(coord1, coord2):
    """
    Calcula la distancia en kilómetros entre dos coordenadas (lat, lon).
    """
    return geodesic(coord1, coord2).kilometers
