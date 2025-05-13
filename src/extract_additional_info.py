import os
from bs4 import BeautifulSoup

html_dir = "html_snapshots"

servicios_clave = [
    "desayuno", "limpieza", "parking", "toallas", "ropa de cama",
    "traslado", "masaje", "spa", "cena"
]

def analizar_html(nombre_archivo):
    ruta = os.path.join(html_dir, nombre_archivo)
    with open(ruta, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    nombre_hotel = os.path.splitext(nombre_archivo)[0]
    print(f"\n🔎 Analizando {nombre_hotel}...")

    texto_completo = soup.get_text(separator=" ").lower()

    # Política de cancelación
    politica = "No especificada"
    for fragmento in soup.find_all(text=True):
        if "cancelación" in fragmento.lower():
            politica = fragmento.strip()
            break
    print(f"📌 Política de cancelación: {politica}")

    # Mascotas
    mascotas = "❓ No especificado"
    if "no se admiten mascotas" in texto_completo:
        mascotas = "🚫 No se admiten mascotas"
    elif "se admiten mascotas" in texto_completo:
        mascotas = "✅ Se admiten mascotas"
    print(f"🐶 Mascotas: {mascotas}")

    # Cunas y camas supletorias
    camas = []
    if "cuna" in texto_completo:
        camas.append("🛏️ Cunas disponibles")
    if "cama supletoria" in texto_completo or "camas supletorias" in texto_completo:
        camas.append("🛏️ Camas supletorias disponibles")
    if "coste adicional" in texto_completo or "puede tener un coste" in texto_completo:
        camas.append("💰 Pueden tener coste adicional")

    print("🛏️ Cunas/Camas supletorias:")
    for cama in camas:
        print(f"   - {cama}")

    # Servicios adicionales
    encontrados = []
    for servicio in servicios_clave:
        if servicio in texto_completo:
            encontrados.append(f"➕ {servicio.capitalize()}")

    print("🎁 Servicios adicionales encontrados:")
    for serv in encontrados:
        print(f"   - {serv}")

    # Precios
    precios_encontrados = set()
    precios_detallados = set()

    for td in soup.find_all("td", role="gridcell"):
        # Buscar el div dentro del td
        div_precio = td.find("div")
        if div_precio:
            span_precio = div_precio.find("span")
            if span_precio:
                texto = span_precio.get_text(strip=True).replace("\xa0", " ")

                if "€" in texto:
                    if any(p in texto.lower() for p in ["por niño", "por persona", "por noche"]):
                        precios_detallados.add(texto)
                    else:
                        # Solo aceptar si tiene estructura correcta tipo "€ 249"
                        partes = texto.split()
                        for parte in partes:
                            if "€" in parte and any(c.isdigit() for c in parte):
                                precios_encontrados.add(parte.strip())

    if precios_encontrados:
        print("💶 Precios (por noche):")
        for p in sorted(precios_encontrados):
            print(f"   - {p}")
    else:
        print("💶 Precios (por noche): Ninguno")

    if precios_detallados:
        print("📋 Otros precios encontrados:")
        for p in sorted(precios_detallados):
            print(f"   - {p}")

# Función para extraer información adicional de un archivo HTML para App.py
def extract_extras_from_html(nombre_hotel):
    safe_name = "".join(c for c in nombre_hotel if c.isalnum() or c in (' ', '-', '_')).rstrip()
    nombre_archivo = f"{safe_name}.html"
    ruta = os.path.join(html_dir, nombre_archivo)

    if not os.path.exists(ruta):
        return {}  # Nada que extraer

    with open(ruta, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    texto_completo = soup.get_text(separator=" ").lower()
    resultado = {}

    # Política de cancelación
    politica = "No especificada"
    for fragmento in soup.find_all(text=True):
        if "cancelación" in fragmento.lower():
            politica = fragmento.strip()
            break
    resultado["politica_cancelacion"] = politica

    # Mascotas
    if "no se admiten mascotas" in texto_completo:
        resultado["mascotas"] = "No"
    elif "se admiten mascotas" in texto_completo:
        resultado["mascotas"] = "Sí"
    else:
        resultado["mascotas"] = "No especificado"

    # Cunas y camas supletorias
    resultado["cunas"] = "Sí" if "cuna" in texto_completo else "No"
    resultado["camas_supletorias"] = "Sí" if "cama supletoria" in texto_completo or "camas supletorias" in texto_completo else "No"
    resultado["coste_adicional"] = "Sí" if "coste adicional" in texto_completo or "puede tener un coste" in texto_completo else "No"

    # Servicios adicionales
    encontrados = [s.capitalize() for s in servicios_clave if s in texto_completo]
    resultado["servicios_adicionales"] = ", ".join(encontrados) if encontrados else "Ninguno"

    return resultado

# Ejecutar análisis para todos los archivos .html
for archivo in os.listdir(html_dir):
    if archivo.endswith(".html"):
        analizar_html(archivo)
