# 🏡 Comparador Inteligente de Alojamientos Turísticos Rurales

Este proyecto forma parte del Trabajo Final del Máster en Data Science & IA y está diseñado para convertirse en un producto real dentro de la empresa **Lares Gestión**, especializada en digitalización de complejos turísticos rurales. La herramienta permite a los propietarios de alojamientos rurales comparar su establecimiento con la competencia directa y recibir sugerencias inteligentes de precios basadas en IA.

---

## 🌍 Objetivo del Proyecto

Desarrollar una plataforma capaz de:

✅ Localizar alojamientos turísticos cercanos a un alojamiento concreto (radio configurable, por ejemplo 10 km).  
✅ Obtener información pública sobre esos alojamientos usando la **Google Places API**.  
✅ Extraer automáticamente precios reales visibles en **Booking.com** mediante Selenium.  
✅ Detectar servicios, políticas y características disponibles de cada alojamiento.  
✅ Generar una **recomendación de precio sugerido** basada en la competencia y las características propias.  
✅ Presentar toda la información en una interfaz clara y visual construida con **Streamlit**.

---

## ⚙️ Funcionalidades implementadas (versión alfa estable)

### 🔹 1. Geolocalización
Utiliza la API de OpenCage para obtener las coordenadas del alojamiento propio a partir de un texto libre.

### 🔹 2. Búsqueda de competencia cercana
A través de **Google Places API**, localiza alojamientos turísticos en un radio determinado desde el alojamiento base. Guarda los resultados y evita llamadas redundantes usando cacheo local en CSV.

### 🔹 3. Obtención de detalles y características
Con **Google Place Details API** y scraping en Booking se detectan:

- Nombre y dirección completa.
- Puntuación y número de opiniones.
- Capacidad máxima estimada.
- Número de habitaciones.
- Servicios detectados: desayuno, piscina, spa, limpieza, etc.
- Políticas (mascotas, cancelación, camas supletorias, etc.).

### 🔹 4. Scraping de precios con Selenium
Se automatiza la búsqueda de cada alojamiento en Booking.com:

- Se abre la ficha del alojamiento.
- Se detectan precios visibles directamente en el calendario.
- Si es posible, se seleccionan fechas consecutivas y se confirma la estancia.
- Se calculan y guardan: precio mínimo, máximo y promedio.
- Se almacena el HTML del alojamiento en `data/html/` para posteriores análisis.

### 🔹 5. Análisis del alojamiento propio
Se ejecuta un scraping similar al de los competidores para obtener el HTML del alojamiento propio, y se analizan los mismos datos:

- Se extrae automáticamente la puntuación.
- Se detecta el número de opiniones, extras, capacidad y habitaciones.

### 🔹 6. Recomendación inteligente de precios (IA)
El sistema sugiere un **rango de precio recomendado** para el alojamiento propio teniendo en cuenta:

- La media de precios visibles de la competencia (ajustada por comisión de Booking).
- La puntuación y número de extras del propio alojamiento vs los competidores.
- Una fórmula de ponderación para valorar diferencias.

---

## 📌 Componentes principales del proyecto

### `geolocation.py`
Obtiene las coordenadas del alojamiento base a partir del nombre.

### `places_search.py`
Consulta Google Places API para encontrar alojamientos cercanos. Incluye cacheo automático.

### `scraper_selenium.py`
Scrapea Booking para obtener precios reales y HTML completo de alojamientos (propio y competidores).

### `extract_additional_info.py`
Extrae desde el HTML guardado de Booking extras como política de cancelación, camas supletorias, coste adicional, etc.

### `extract_own_features.py`
Extrae del HTML del alojamiento propio su puntuación, servicios, capacidad y más.

### `price_recommender.py`
Algoritmo que recomienda un precio mínimo y máximo basándose en la comparación con la competencia cercana.

### `app.py`
Interfaz visual creada con **Streamlit**, integra todo el flujo:

1. Introducción del nombre del alojamiento propio.
2. Búsqueda de competencia cercana.
3. Visualización y selección manual de competidores.
4. Ejecución del scraping automatizado.
5. Presentación visual de los datos.
6. Sugerencia inteligente de precios.

---

## 🛠 Tecnologías utilizadas

- Python 3.10+
- Streamlit (interfaz)
- Selenium (scraping dinámico)
- BeautifulSoup (análisis de HTML)
- Google Places API
- OpenCage API
- Pandas / Requests / difflib / re / OS

---

## 📁 Estructura del proyecto

ProyectoMaster/
├── app.py
├── .env
├── requirements.txt
├── data/
│ ├── nearby_competitors.csv
│ └── html/
│ └── <nombre_hotel>.html
├── drivers/
│ └── chromedriver-win64/
├── html_snapshots/
│ └── <nombre_hotel>.html
├── src/
│ ├── geolocation.py
│ ├── places_search.py
│ ├── scraper_selenium.py
│ ├── extract_additional_info.py
│ ├── extract_own_features.py
│ └── price_recommender.py

## 🚧 Mejoras previstas

- 🎯 **Detectar precios por tipo de habitación** para mayor precisión.
- 🧠 Ajustar la lógica de recomendación de precios según temporada y meteorología.
- 🌤️ Integrar predicción meteorológica como variable que afecte al precio dinámico.
- 🔎 Mejorar robustez del scraping en casos donde Booking muestra estructuras dinámicas distintas.
- 🕸️ Scraping de páginas web oficiales de los alojamientos (cuando existan).
- 📊 Exportación automática a Power BI o generación de informes PDF.
- 🔒 Gestión de autenticación y perfiles de clientes.

## 🚀 Visión a futuro

Este proyecto no es solo un ejercicio académico: es la **primera versión funcional de un producto real** de **Lares Gestión**, diseñado para ayudar a propietarios de alojamientos rurales a tomar decisiones basadas en datos, competir mejor en su zona, y optimizar ingresos.

## 📅 Última actualización

**18 de mayo de 2025**

Desarrollado por **Germán Bermúdez Rodríguez**  
[🔗 GitHub](https://github.com/GermanBermudezRod) · [🔗 LinkedIn](https://www.linkedin.com/in/german-bermudez-rodriguez/)

