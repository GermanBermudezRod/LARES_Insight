import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from difflib import SequenceMatcher
import logging
import time
import os

CHROMEDRIVER_PATH = r".\drivers\chromedriver-win64\chromedriver.exe"

# Calcular similitud entre nombres
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Seleccionar fechas automáticamente en el calendario
def seleccionar_fecha_disponible(driver, espera=10):
    try:
        print("📅 Abriendo calendario en ficha del hotel...")

        # 1. Asegurarse de que el botón del calendario está presente y hacer clic
        WebDriverWait(driver, espera).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='date-display-field-start']"))
        )
        calendar_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='date-display-field-start']")
        driver.execute_script("arguments[0].scrollIntoView(true);", calendar_button)
        time.sleep(1)
        calendar_button.click()
        time.sleep(2)

        # 2. REABRIR el calendario si se ha cerrado antes de seleccionar
        try:
            calendar_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='date-display-field-start']")
            driver.execute_script("arguments[0].scrollIntoView(true);", calendar_button)
            time.sleep(1)
            calendar_button.click()
            print("✅ Calendario reabierto correctamente")
            time.sleep(2)
        except Exception as e:
            print(f"❌ No se pudo reabrir el calendario: {e}")

        # 3. Buscar celdas del calendario visibles
        celdas = driver.find_elements(By.CSS_SELECTOR, "td[role='gridcell']")
        print(f"🔎 Encontradas {len(celdas)} celdas en el calendario.")

        for i in range(len(celdas) - 1):
            try:
                # Obtener spans internos
                span_precio_1 = celdas[i].find_element(By.CSS_SELECTOR, "div span")
                span_precio_2 = celdas[i + 1].find_element(By.CSS_SELECTOR, "div span")

                texto1 = span_precio_1.text.strip()
                texto2 = span_precio_2.text.strip()

                if "€" in texto1 and "€" in texto2:
                    # Highlight visual para depuración
                    driver.execute_script("arguments[0].style.border='3px solid red'", celdas[i])
                    driver.execute_script("arguments[0].style.border='3px solid green'", celdas[i + 1])
                    time.sleep(1)

                    celdas[i].click()
                    print(f"📆 Entrada seleccionada: {texto1}")
                    time.sleep(1)

                    celdas[i + 1].click()
                    print(f"📆 Salida seleccionada: {texto2}")
                    time.sleep(2)

                    # 4. Hacer clic en el botón de confirmar fechas (submit)
                    try:
                        layout = driver.find_element(By.CSS_SELECTOR, "div[data-testid='searchbox-layout-wide']")
                        submit = layout.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        driver.execute_script("arguments[0].scrollIntoView(true);", submit)
                        time.sleep(1)
                        submit.click()
                        print("✅ Fechas confirmadas correctamente.")
                        return True
                    except Exception as e:
                        print(f"⚠️ No se pudo confirmar fechas: {e}")
                        return False

            except Exception:
                continue

        print("⚠️ No se encontraron dos días consecutivos con precio.")
        return False

    except Exception as e:
        print(f"❌ Error general en selección de fechas: {e}")
        return False

# Función principal del scraper
def get_price_from_booking(hotel_name):
    # Cargar zona esperada desde coordinates_cache.csv
    try:
        coord_df = pd.read_csv("data/coordinates_cache.csv")
        row = coord_df[coord_df["name"].str.lower() == hotel_name.lower()]
        if not row.empty:
            zona_esperada = row.iloc[0]["address"].lower() if "address" in row.columns else ""
        else:
            zona_esperada = ""
    except Exception as e:
        print(f"⚠️ No se pudo leer zona desde CSV: {e}")
        zona_esperada = ""

    otras_zonas_validas = ["ossa de montiel", "lagunas de ruidera", "ruidera", "albacete"]

    # Resto de la función
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"\n🌐 Buscando: {hotel_name}")
        driver.get("https://www.booking.com/")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "ss")
        search_box.clear()
        search_box.send_keys(hotel_name)
        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-testid='autocomplete-result']"))
        )
        suggestions = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='autocomplete-result']")

        encontrado = False
        for suggestion in suggestions:
            texto = suggestion.text.lower()
            if zona_esperada and zona_esperada in texto:
                suggestion.click()
                print(f"✅ Sugerencia seleccionada: {texto}")
                encontrado = True
                break
            elif any(z in texto for z in otras_zonas_validas):
                suggestion.click()
                print(f"✅ Sugerencia válida seleccionada: {texto}")
                encontrado = True
                break

        if not encontrado:
            print("⚠️ No se encontró sugerencia con la zona esperada. Usando el primer resultado por defecto.")
            suggestions[0].click()

        time.sleep(6)

        # ... (aquí sigue todo tu código normal, sin tocar más)

    except Exception as e:
        print(f"❌ Error general en Selenium: {e}")
        logging.error(f"{hotel_name} - {e}")
        return None, None, None

    finally:
        driver.quit()
