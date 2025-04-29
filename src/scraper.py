import requests
from bs4 import BeautifulSoup
import re

def get_price_from_website(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # lanza error si no es 200 OK

        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        # Patrones comunes de precios
        patterns = [
            r"(\d{2,4}) ?€ ?(?:\/noche|por noche|por habitación|por persona)?",
            r"€ ?(\d{2,4})",
            r"(\d{2,4}) euros(?: por noche| por persona)?"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = match.group(1)
                return float(price)

        return None

    except requests.exceptions.RequestException as req_err:
        print(f"❌ Error de conexión con {url}: {req_err}")
        return None
    except Exception as e:
        print(f"⚠️ Error inesperado haciendo scraping en {url}: {e}")
        return None
