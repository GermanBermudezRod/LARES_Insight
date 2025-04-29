import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

# Obtener ruta del CSV desde .env
csv_path = os.getenv("COMPETITOR_CSV")

if not csv_path or not os.path.exists(csv_path):
    print("❌ El archivo CSV no existe o no está definido en .env")
else:
    # Leer el archivo CSV con pandas
    df = pd.read_csv(csv_path)

    # Mostrar resumen
    print("\n✅ Archivo cargado correctamente:")
    print(f"📦 {len(df)} alojamientos encontrados.\n")

    # Mostrar primeras filas
    print(df.columns)
    print(df.head(5))
