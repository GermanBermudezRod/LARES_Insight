import pandas as pd

def recomendar_precio(own_data, competitors_df):
    """
    Recomienda un precio medio por noche en base a la comparación con la competencia.
    """
    if own_data is None or competitors_df.empty:
        return None

    df = competitors_df.copy()

    # Usar 'rating' como 'guest_rating' si no está
    if "guest_rating" not in df.columns and "rating" in df.columns:
        df = df.rename(columns={"rating": "guest_rating"})

    # Filtrar competidores con precio medio válido
    df = df[pd.to_numeric(df["price_avg"], errors="coerce").notnull()]
    df["price_avg"] = df["price_avg"].astype(float) * 0.85  # Ajuste del 15% de comisión

    # Comparar número de extras
    def contar_extras(row):
        return sum(1 for col in row.index if col.startswith("servicio_") and row[col] == "Sí")

    df["n_extras"] = df.apply(contar_extras, axis=1)
    own_extras = contar_extras(pd.Series(own_data))

    # Diferencias de puntuación
    own_rating = float(own_data.get("rating", 0))
    df["score_diff"] = pd.to_numeric(df["guest_rating"], errors="coerce").fillna(0) - own_rating
    df["extra_diff"] = df["n_extras"] - own_extras

    # Ponderación de precios (más cercanos en extras y puntuación pesan más)
    df["peso"] = 1 / (1 + df["score_diff"].abs() + df["extra_diff"].abs())
    precio_recomendado = (df["price_avg"] * df["peso"]).sum() / df["peso"].sum()

    # Texto explicativo (opcional)
    razon = "Basado en {} alojamientos similares con una puntuación media de {:.1f} y número de extras comparables.".format(
        len(df), df["guest_rating"].mean()
    )

    return round(precio_recomendado * 0.95, 2), round(precio_recomendado * 1.05, 2), razon
