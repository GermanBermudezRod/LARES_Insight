import os
import re
from bs4 import BeautifulSoup

HTML_DIR = "data/html"

SERVICIOS_CLAVE = [
    "desayuno", "limpieza", "parking", "toallas", "ropa de cama",
    "traslado", "masaje", "spa", "cena", "wifi", "piscina", "cocina"
]

def extract_own_features_from_booking(nombre_hotel):
    safe_name = "".join(c for c in nombre_hotel if c.isalnum() or c in (' ', '-', '_')).rstrip()
    nombre_archivo = f"{safe_name}.html"
    ruta = os.path.join(HTML_DIR, nombre_archivo)

    if not os.path.exists(ruta):
        return {}

    with open(ruta, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    texto_completo = soup.get_text(separator=" ").lower()
    result = {}

    # Puntuación y número de opiniones
    score_tag = soup.select_one('[data-testid="review-score-component"]')
    if score_tag:
        texto_score = score_tag.get_text(separator=" ").strip()

        # Buscar explícitamente el patrón 'Puntuación: 9,1' o similar
        if "Puntuación:" in texto_score:
            try:
                puntuacion = texto_score.split("Puntuación:")[-1].strip().split()[0].replace(",", ".")
                result["rating"] = puntuacion
            except Exception:
                result["rating"] = "0"
        else:
            result["rating"] = "0"

        # Buscar número total de opiniones (ej. 125 opiniones)
        match_reviews = re.search(r"(\d{2,6})", texto_score)
        if match_reviews:
            result["total_reviews"] = match_reviews.group()

    # Habitaciones (estimación)
    habitaciones = 0
    if "habitaciones" in texto_completo or "habitación" in texto_completo:
        for palabra in texto_completo.split():
            if palabra.isdigit():
                habitaciones = max(habitaciones, int(palabra))
    result["num_rooms"] = habitaciones if habitaciones > 0 else "No disponible"

    # Capacidad (estimada)
    capacidad = 0
    if "capacidad para" in texto_completo:
        partes = texto_completo.split("capacidad para")
        if len(partes) > 1:
            for token in partes[1].split():
                if token.isdigit():
                    capacidad = int(token)
                    break
    result["max_capacity"] = capacidad if capacidad > 0 else "No disponible"

    # Servicios adicionales encontrados
    servicios = [s for s in SERVICIOS_CLAVE if s in texto_completo]
    result["extras"] = servicios

    return result