import os
from bs4 import BeautifulSoup
import re

def extract_extras_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    name = os.path.basename(file_path).replace(".html", "")
    print(f"\n🔎 Analizando {name}...")

    # Unir todo el texto
    full_text = " ".join(soup.stripped_strings).lower()

    # 1. Política de cancelación
    cancel_match = re.search(r"(cancelaci[oó]n[^\.]{0,100})", full_text)
    cancel_policy = cancel_match.group(1).capitalize() if cancel_match else "No especificada"
    print(f"📌 Política de cancelación: {cancel_policy}")

     # 2. Mascotas
    mascotas_bloque = None
    for div in soup.find_all("div"):
        if div.get_text(strip=True).lower() == "mascotas":
            mascotas_bloque = div.find_next_sibling("div")
            break

    if mascotas_bloque:
        mascotas_texto = mascotas_bloque.get_text(strip=True).lower()
        if "no se admiten" in mascotas_texto or "no se aceptan" in mascotas_texto:
            print("🐶 Mascotas: 🚫 No se admiten mascotas")
        elif "se admiten" in mascotas_texto or "se aceptan" in mascotas_texto:
            print("🐶 Mascotas: ✅ Se admiten mascotas")
        else:
            print("🐶 Mascotas: ❓ Condiciones no claras")
    else:
        print("🐶 Mascotas: ❓ No especificado")

    # 3. Cunas / Camas supletorias
    if "cuna" in full_text:
        print("🛏️ Cunas disponibles")
    if "cama supletoria" in full_text or "camas supletorias" in full_text:
        print("🛏️ Camas supletorias disponibles")
    if "coste adicional" in full_text or "pueden tener coste adicional" in full_text:
        print("💰 Pueden tener coste adicional")

    # 4. Servicios adicionales
    servicios = [
        "desayuno", "limpieza", "parking", "toallas", "ropa de cama",
        "spa", "masaje", "traslado", "cena"
    ]
    encontrados = [s for s in servicios if s in full_text]
    if encontrados:
        print("🎁 Servicios adicionales encontrados:")
        for s in encontrados:
            print(f"   - ➕ {s.capitalize()}")

    # 5. Precios extra (por niño, persona o noche)
    precios_extras = re.findall(
        r"\b€\s?[0-9]{1,3}(?:[.,][0-9]{1,2})?\s?(?:por\s(?:niñ[oa]|persona|noche|adulto))",
        full_text
    )
    if precios_extras:
        print("💶 Precios de servicios extra encontrados:")
        for p in precios_extras:
            print(f"   - 💰 {p.strip()}")
    else:
        print("💶 Precios de servicios extra encontrados: Ninguno")

     # 6. Puntuación y número de comentarios
    review_component = soup.find("div", {"data-testid": "review-score-component"})
    if review_component:
        all_divs = review_component.find_all("div")
        all_spans = review_component.find_all("span")

        # Puntuación: segundo <div> hijo
        puntuacion = all_divs[1].text.strip() if len(all_divs) > 1 else "No disponible"

        # Comentarios: segundo <span> hijo del último <div>
        comentarios = all_spans[1].text.strip() if len(all_spans) > 1 else "No disponibles"

        print(f"⭐ Puntuación: {puntuacion}")
        print(f"🗣️ Comentarios: {comentarios}")
    else:
        print("⭐ Puntuación: No disponible")
        print("🗣️ Comentarios: No disponibles")

    # 7. HTML completo de las políticas de cunas/camas (bloque completo)
    child_policy_block = soup.find("div", {"data-test-id": "child-policies-block"})
    if child_policy_block:
        print("🧒 Políticas de cunas y camas supletorias:")
        print("----------------------------------------------")
        print(child_policy_block.get_text(separator="\n", strip=True))
        print("----------------------------------------------")
    else:
        print("🧒 Políticas de cunas y camas supletorias: ❌ No encontradas")

# Ruta local a los archivos HTML
snapshots_folder = "./html_snapshots"  # ← asegúrate de que la ruta es correcta

if os.path.exists(snapshots_folder):
    for filename in os.listdir(snapshots_folder):
        if filename.endswith(".html"):
            extract_extras_from_html(os.path.join(snapshots_folder, filename))
else:
    print("❌ La carpeta 'html_snapshots' no existe.")
