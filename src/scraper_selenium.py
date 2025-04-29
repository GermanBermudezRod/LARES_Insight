from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re

CHROMEDRIVER_PATH = r".\drivers\chromedriver-win64\chromedriver.exe"

def get_price_from_booking(hotel_name):
    checkin_date = "2024-07-10"
    checkout_date = "2024-07-11"

    options = Options()
    # Quitar el modo headless para ver el navegador
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 1. Abrir Booking
        driver.get("https://www.booking.com/")
        time.sleep(2)

        # 2. Buscar alojamiento
        search_box = driver.find_element(By.NAME, "ss")
        search_box.clear()
        search_box.send_keys(hotel_name)
        time.sleep(2)
        search_box.send_keys(Keys.RETURN)

        time.sleep(5)

        # 3. Cargar página con fechas
        current_url = driver.current_url
        url_with_dates = f"{current_url}&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1"
        driver.get(url_with_dates)

        # 4. Esperar a que cargue
        time.sleep(8)

        # 5. Simular scroll para cargar contenido dinámico
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # 6. Guardar HTML para inspección
        with open("booking_debug_scroll.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        # 7. Buscar precio en todo el texto de la página
        full_text = driver.page_source
        matches = re.findall(r"(\d{2,4}) ?€", full_text)
        prices = [float(p) for p in matches]

        if prices:
            avg_price = sum(prices) / len(prices)
            return round(avg_price, 2)
        else:
            return None

    except Exception as e:
        print(f"❌ Error en Selenium: {e}")
        return None

    finally:
        driver.quit()
