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
    df = pd.DataFrame(columns=["name", "latitude", "longitude"])
    df.to_csv(CACHE_FILE, index=False)

def get_coordinates(name):
    """
    Devuelve las coordenadas de un alojamiento:
    - Busca primero en el CSV local
    - Si no está, lo consulta en la API de Google y guarda el resultado
    """
    df = pd.read_csv(CACHE_FILE)

    # Buscar en el CSV si ya existe
    row = df[df["name"].str.lower() == name.lower()]
    if not row.empty:
        lat = row.iloc[0]["latitude"]
        lon = row.iloc[0]["longitude"]
        return (lat, lon)

    # Si no está en el CSV, buscar en la API
    location = geolocator.geocode(name)
    if location:
        lat, lon = location.latitude, location.longitude

        # Guardar en el CSV
        new_row = pd.DataFrame([{"name": name, "latitude": lat, "longitude": lon}])
        new_row.to_csv(CACHE_FILE, mode="a", header=False, index=False)

        return (lat, lon)
    else:
        return None

def calculate_distance(coord1, coord2):
    """
    Calcula la distancia en kilómetros entre dos coordenadas (lat, lon).
    """
    return geodesic(coord1, coord2).kilometers
