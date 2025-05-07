import requests
import os
import pandas as pd
from dotenv import load_dotenv
from geopy.distance import geodesic
import time

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CACHE_FILE = os.getenv("COMPETITOR_CSV")

def search_nearby_lodgings(lat, lon, radius=10000):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": "lodging",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,formatted_address,types,website,formatted_phone_number,url,place_id,geometry",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("result", {})

def get_cached_or_query_places(lat, lon, threshold_km=0.2, radius_m=10000):
    if os.path.exists(CACHE_FILE):
        df = pd.read_csv(CACHE_FILE)

        matches = df.apply(lambda row: geodesic((lat, lon), (row["origin_lat"], row["origin_lon"])).km < threshold_km, axis=1)
        cached = df[matches]
        if not cached.empty:
            print("📁 Usando resultados cacheados")
            return cached.to_dict(orient="records")

    print("🌐 Buscando con Google Places API...")
    results = search_nearby_lodgings(lat, lon, radius=radius_m)
    data = []

    for place in results:
        details = get_place_details(place["place_id"])
        if details and "geometry" in details:
            loc = details["geometry"]["location"]

            types_list = details.get("types", [])
            type_primary = types_list[0] if types_list else None
            guest_rating = details.get("rating")

            data.append({
                "origin_lat": lat,
                "origin_lon": lon,
                "lat": loc["lat"],
                "lon": loc["lng"],
                "name": details.get("name"),
                "address": details.get("formatted_address"),
                "rating": guest_rating,
                "total_reviews": details.get("user_ratings_total"),
                "phone": details.get("formatted_phone_number"),
                "website": details.get("website"),
                "maps_url": details.get("url"),
                "types": ", ".join(types_list),
                "type_primary": type_primary,
                "guest_rating": guest_rating,
                "place_id": details.get("place_id")
            })
        time.sleep(1)  # Evita sobrepasar los límites de cuota

    if data:
        df_new = pd.DataFrame(data)
        if os.path.exists(CACHE_FILE):
            df_old = pd.read_csv(CACHE_FILE)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.drop_duplicates(subset=["place_id"], inplace=True)
            df_combined.to_csv(CACHE_FILE, index=False)
        else:
            df_new.to_csv(CACHE_FILE, index=False)

    return data