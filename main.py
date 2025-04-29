from src.scraper_selenium import get_price_from_booking

hotel_name = "Hotel rural Albamanjón - Parque Natural de las Lagunas de Ruidera"
price = get_price_from_booking(hotel_name)

if price:
    print(f"💶 Precio medio estimado en Booking (12-13 julio): {price} €")
else:
    print("❌ No se encontró precio visible.")
