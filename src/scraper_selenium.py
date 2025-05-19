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

def guardar_html_de_booking(nombre_hotel):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # Descomenta la línea siguiente si quieres ocultar el navegador:
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    try:
        # 1. Ir a la página principal de Booking
        driver.get("https://www.booking.com/")
        time.sleep(2)

        # 2. Buscar el alojamiento
        search_box = driver.find_element(By.NAME, "ss")
        search_box.clear()
        search_box.send_keys(nombre_hotel)
        time.sleep(2)
        search_box.send_keys(Keys.RETURN)
        time.sleep(6)

        # 3. Obtener el enlace del primer resultado
        hotel_link = driver.find_element(By.CSS_SELECTOR, "a[data-testid='title-link']")
        hotel_url = hotel_link.get_attribute("href")

        # 4. Entrar en la ficha del hotel
        driver.get(hotel_url)
        time.sleep(6)

        # 5. Guardar el HTML de la página
        html = driver.page_source
        safe_name = "".join(c for c in nombre_hotel if c.isalnum() or c in (' ', '-', '_')).rstrip()
        ruta = os.path.join("data", "html", f"{safe_name}.html")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ HTML guardado correctamente en {ruta}")

    except Exception as e:
        print(f"❌ Error al intentar guardar el HTML del alojamiento: {e}")

    finally:
        driver.quit()

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
    # Configuración del navegador
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
        search_box.send_keys(Keys.RETURN)
        time.sleep(6)

        # 1. Validar nombre y dirección
        try:
            result_name_elem = driver.find_element(By.CSS_SELECTOR, "div[data-testid='title']")
            result_name = result_name_elem.text.strip()
        except:
            result_name = ""

        try:
            result_address_elem = driver.find_element(By.CSS_SELECTOR, "span[data-testid='address']")
            result_address = result_address_elem.text.strip()
        except:
            result_address = ""

        zona_esperada = "ossa de montiel"
        otras_zonas_validas = ["lagunas de ruidera", "ruidera"]
        nombre_similar = similar(hotel_name, result_name) > 0.7
        zona_coincide = any(z in result_address.lower() for z in [zona_esperada] + otras_zonas_validas)

        if not (nombre_similar or zona_coincide):
            print("⚠️ El resultado no coincide ni por nombre ni por zona.")
            return "NO_MATCH", "NO_MATCH", "NO_MATCH"
        else:
            print(f"✅ Coincidencia aceptada: {result_name} | {result_address}")

        # 2. Ir al enlace del hotel
        hotel_link = driver.find_element(By.CSS_SELECTOR, "a[data-testid='title-link']")
        hotel_url = hotel_link.get_attribute("href")
        driver.get(hotel_url)
        time.sleep(6)

        # 3. Abrir calendario (aunque no seleccionemos fechas aún)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='date-display-field-start']"))
        )
        calendar_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='date-display-field-start']")
        driver.execute_script("arguments[0].scrollIntoView(true);", calendar_button)
        time.sleep(1)
        calendar_button.click()
        time.sleep(2)
        # 📁 Guardar snapshot del HTML del calendario para este hotel
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        snapshots_dir = os.path.join(project_root, "html_snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)

        safe_name = "".join(c for c in hotel_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        file_path = os.path.join(snapshots_dir, f"{safe_name}.html")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print(f"📄 HTML del hotel guardado en: {file_path}")

        # 4. Extraer precios directamente desde el DOM (sin buscar contenedor intermedio)
        #print("🔍 Extrayendo precios directamente de los días del calendario...")

        time.sleep(2)  # Esperamos brevemente para que se rendericen los precios

        print("🔍 Extrayendo precios directamente del calendario...")

        prices = []
        td_elements = driver.find_elements(By.CSS_SELECTOR, "td[role='gridcell']")

        for td in td_elements:
            try:
                # Buscar el primer div descendiente
                div = td.find_element(By.TAG_NAME, "div")
                
                # Dentro del div, buscar el primer span
                span = div.find_element(By.TAG_NAME, "span")
                text = span.text.strip()

                if "€" in text:
                    value = text.replace("€", "").replace("\xa0", "").replace(",", ".")
                    price = float(value)
                    prices.append(price)
            except Exception:
                continue  # Si no encuentra los elementos, simplemente salta al siguiente td

        print(f"💶 Precios encontrados: {prices}")


        print(f"💶 Precios encontrados en calendario: {prices}")

        # 5. Intentar seleccionar fechas si es posible (aunque ya tengamos precios)
        seleccion_ok = seleccionar_fecha_disponible(driver)
        if not seleccion_ok:
            print("⚠️ No se pudieron seleccionar fechas. Continuamos con precios visibles.")

        # 6. Guardar precios si se encontraron
        if prices:
            price_min = round(min(prices), 2)
            price_max = round(max(prices), 2)
            price_avg = round(sum(prices) / len(prices), 2)

            print(f"✅ Precios ➜ Min: {price_min} €, Max: {price_max} €, Media: {price_avg} €")
            return price_min, price_max, price_avg
        else:
            print("⚠️ No se encontraron precios visibles.")
            return None, None, None

    except Exception as e:
        print(f"❌ Error general en Selenium: {e}")
        logging.error(f"{hotel_name} - {e}")
        return None, None, None

    finally:
        driver.quit()