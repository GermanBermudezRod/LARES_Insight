Proyecto: Comparador Inteligente de Alojamientos Turísticos Rurales

Este proyecto tiene como objetivo desarrollar una herramienta de análisis competitivo para alojamientos turísticos rurales. Forma parte del Trabajo Final del Máster en Data Science & IA, y está alineado con los servicios de digitalización de una empresa enfocada en complejos turísticos rurales.

🌍 Objetivo del Proyecto

Crear un sistema inteligente capaz de:

Localizar alojamientos turísticos cercanos a una dirección o casa rural determinada (por ejemplo, en un radio de 10km).

Obtener información detallada de dichos alojamientos (nombre, dirección, puntuación, número de opiniones, etc.) mediante la API de Google Places.

Guardar esta información en un fichero CSV para su posterior análisis.

Obtener automáticamente el precio medio por noche de cada alojamiento competidor desde Booking.com usando automatización con Selenium.

🔄 Situación Actual

Actualmente, el proyecto está en una fase funcional avanzada y modular:

✅ Módulos implementados:

Geolocalización: A partir de una dirección física, obtenemos las coordenadas con la API de OpenCage (con opción a escalar a Google Maps).

Detección de competencia: Usamos Google Places API para localizar alojamientos cercanos (10km).

Cacheo en CSV: Si ya hemos realizado una búsqueda para una ubicación, usamos el CSV en lugar de hacer una nueva llamada a la API, lo que permite ahorrar límites de peticiones.

Obtención de detalles: Usamos Google Places Details API para obtener información enriquecida de cada alojamiento.

Scraper de precios en Booking.com:

Abre automáticamente la ficha de Booking del alojamiento.

Abre el calendario de fechas disponible y extrae los precios visibles mostrados directamente.

Intenta seleccionar fechas consecutivas disponibles con precio.

Guarda los precios visibles (mínimo, máximo y media) aunque no se puedan seleccionar fechas.

Guarda un snapshot del HTML para cada hotel en la carpeta /html_snapshots/ para posterior análisis.

Escribe los resultados en el fichero nearby_competitors.csv.

⚠️ En progreso:

Ajustes de robustez para la selección automática de fechas.

Validación más precisa de coincidencia entre el hotel buscado y el encontrado.

Extracción de tipo de habitación y precios más detallados.

🏨 Tecnologías utilizadas

Python 3.10+

Selenium (con ChromeDriver)

Google Places API y Place Details API

OpenCage Geocoder

Pandas / BeautifulSoup / Requests / difflib

Archivo .env para gestión de claves y rutas

📁 Estructura del proyecto

ProyectoMaster/
├── .env
├── requirements.txt
├── main.py
├── data/
│   └── nearby_competitors.csv
├── html_snapshots/
│   └── *.html
├── drivers/
│   └── chromedriver-win64/
├── src/
│   ├── geolocation.py
│   ├── places_search.py
│   ├── scraper.py
│   └── scraper_selenium.py

🔢 Próximos pasos

Optimizar selección automática de fechas sin depender de HTML inconsistente.

Añadir comparación entre nombre y dirección para mejorar precisión de resultados.

Mejorar la tolerancia a errores y la velocidad del scraping.

Añadir visualizaciones finales en Power BI o aplicación web.

📅 Fecha de actualización

30 de abril de 2025

Este proyecto está pensado para escalar en el futuro como producto dentro de la empresa, permitiendo a los propietarios de casas rurales analizar sus precios en tiempo real frente a su competencia más cercana y optimizar su estrategia comercial.

