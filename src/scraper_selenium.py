from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

        # 1. Hacer clic en el botón de fechas del hotel
        WebDriverWait(driver, espera).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='date-display-field-start']"))
        )
        calendar_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='date-display-field-start']")
        driver.execute_script("arguments[0].scrollIntoView(true);", calendar_button)
        time.sleep(1)
        calendar_button.click()
        time.sleep(2)

        # 2. Obtener todos los días visibles con data-date
        dias = driver.find_elements(By.CSS_SELECTOR, "span[data-date]")

        # 3. Buscar dos días consecutivos con texto que contenga €
        for i in range(len(dias) - 1):
            dia_texto = dias[i].text
            siguiente_texto = dias[i + 1].text

            if "€" in dia_texto and "€" in siguiente_texto:
                dia_entrada = dias[i]
                dia_salida = dias[i + 1]

                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", dia_entrada)
                    dia_entrada.click()
                    print(f"📆 Entrada: {dia_entrada.get_attribute('data-date')}")

                    time.sleep(1)
                    dia_salida.click()
                    print(f"📆 Salida: {dia_salida.get_attribute('data-date')}")

                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"⚠️ Error haciendo clic en fechas: {e}")
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

        # 4. Extraer precios antes de seleccionar fechas
        print("🔍 Extrayendo precios visibles ANTES de seleccionar fechas...")
        time.sleep(2)
        price_elements = driver.find_elements(By.CSS_SELECTOR, "div.c8079eaf8c.e6208ee469.b0e227d988 span.b1f25950bd")
        prices = []

        for elem in price_elements:
            text = elem.text.strip().replace("€", "").replace("\xa0", "").replace(",", ".")
            try:
                price = float(text)
                prices.append(price)
            except ValueError:
                continue

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
