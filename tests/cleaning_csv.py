import pandas as pd

# Ruta al CSV que quieres limpiar
csv_path = "data/nearby_competitors.csv"

# Leer el CSV completo (permitiendo columnas duplicadas)
df = pd.read_csv(csv_path)

# Eliminar columnas duplicadas conservando la primera aparición
df_clean = df.loc[:, ~df.columns.duplicated()]

# Guardar el CSV limpio sobrescribiendo el anterior
df_clean.to_csv(csv_path, index=False)

print("✅ CSV limpiado correctamente. Columnas duplicadas eliminadas.")