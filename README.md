# ProyectoMaster
Proyecto de análisis de precios de complejos turísticos rurales utilizando IA.
# Proyecto: Comparador Inteligente de Alojamientos Turísticos Rurales

Este proyecto tiene como objetivo desarrollar una herramienta de análisis competitivo para alojamientos turísticos rurales. Forma parte del Trabajo Final del Máster en Data Science & IA, y está alineado con los servicios de digitalización de una empresa enfocada en complejos turísticos rurales.

## Objetivo del Proyecto

Crear un sistema inteligente capaz de:

1. Localizar alojamientos turísticos cercanos a una dirección o casa rural determinada (por ejemplo, en un radio de 10km).
2. Obtener información detallada de dichos alojamientos (nombre, dirección, puntuación, número de opiniones, etc.) mediante la API de Google Places.
3. Guardar esta información en un fichero CSV para su posterior análisis.
4. Obtener automáticamente el precio medio por noche de cada alojamiento competidor, preferiblemente desde Booking.com.

## Situación Actual

Actualmente, el proyecto está en una fase funcional y modular:

### Módulos implementados:

- **Geolocalización**: A partir de una dirección física, obtenemos las coordenadas con la API de OpenCage (con opción a escalar a Google Maps).
- **Detección de competencia**: Usamos Google Places API para localizar alojamientos cercanos (10km).
- **Cacheo en CSV**: Si ya hemos realizado una búsqueda para una ubicación, usamos el CSV en lugar de hacer una nueva llamada a la API, lo que permite ahorrar límites de peticiones.
- **Obtención de detalles**: Usamos Google Places Details API para obtener información enriquecida de cada alojamiento.

### En progreso:

- **Extracción automática de precios**:
  - Hemos desarrollado un scraper con Selenium que abre Booking.com, introduce el nombre del alojamiento, fija fechas concretas y busca el precio mínimo visible por noche.
  - Actualmente estamos ajustando el scraper para que detecte correctamente los precios (usando scroll y extracción de HTML dinámico).

## Tecnologías utilizadas

- Python 3.10+
- Selenium (con ChromeDriver)
- Google Places API y Place Details API
- OpenCage Geocoder
- Pandas / BeautifulSoup / Requests
- Archivo `.env` para gestión de claves y rutas

## Estructura del proyecto

```
ProyectoMaster/
├── .env
├── requirements.txt
├── main.py
├── data/
│   └── nearby_competitors.csv
├── drivers/
│   └── chromedriver-win64/
├── src/
│   ├── geolocation.py
│   ├── places_search.py
│   ├── scraper.py
│   └── scraper_selenium.py
```

## Próximos pasos

- Mejorar la robustez del scraper para Booking (detección fiable de precios).
- Aplicar el scraping masivo a todos los alojamientos guardados en el CSV.
- Calcular estadísticas automáticas: media, desviación, ranking por valoración/precio, etc.
- Construcción de un dashboard (Power BI o web) para visualización final por el usuario.

## Fecha de actualización

29 de abril de 2025

---

Este proyecto está pensado para escalar en el futuro como producto dentro de la empresa, permitiendo a los propietarios de casas rurales analizar sus precios en tiempo real frente a su competencia más cercana.

