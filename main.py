import pandas as pd
from src.scraper_selenium import get_price_from_booking
import time
import logging

# Configurar log de errores
logging.basicConfig(
    filename="price_scraper_errors.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cargar el CSV
csv_path = "data/nearby_competitors.csv"
df = pd.read_csv(csv_path)

# Asegurar que existen las columnas necesarias
for col in ["price_min", "price_max", "price_avg"]:
    if col not in df.columns:
        df[col] = None

# Recorrer cada alojamiento del CSV
for index, row in df.iterrows():
    hotel_name = row["name"]

    # Saltar si ya tiene un valor (incluyendo NO_MATCH)
    #if pd.notnull(row.get("price_min")):
    #    print(f"⏭️ Ya procesado: {hotel_name}")
    #    continue

    print(f"\n🔍 Procesando: {hotel_name}")

    try:
        price_min, price_max, price_avg = get_price_from_booking(hotel_name)

        # Guardar los resultados (aunque sean "NO_MATCH")
        df.at[index, "price_min"] = price_min
        df.at[index, "price_max"] = price_max
        df.at[index, "price_avg"] = price_avg

        if price_min == "NO_MATCH":
            print(f"⚠️ No coincidencia encontrada para: {hotel_name}")
        else:
            print(f"✅ Guardado ➜ Min: {price_min} €, Max: {price_max} €, Media: {price_avg} €")

    except Exception as e:
        print(f"❌ Error procesando {hotel_name}: {e}")
        logging.error(f"{hotel_name} - {e}")

    time.sleep(3)  # Espera entre peticiones para evitar bloqueos

# Guardar resultados en el CSV
df.to_csv(csv_path, index=False)
print("\n✅ Archivo actualizado correctamente.")
