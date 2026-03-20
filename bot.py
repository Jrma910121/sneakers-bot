import requests
from bs4 import BeautifulSoup
import json

# ---------------------------
# Configuración Telegram
# ---------------------------
TELEGRAM_TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"
TELEGRAM_CHAT_ID = "8751177346"

# ---------------------------
# Lista de URLs de productos
# ---------------------------
URLS = [
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/BV1358-003",
    # ... agrega el resto de tus URLs aquí
]

# ---------------------------
# Funciones
# ---------------------------
def obtener_info_producto(url):
    """
    Obtiene nombre, precio e imagen de un producto Nike
    usando JSON-LD de la página (sin Selenium)
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar el JSON-LD que contiene los datos del producto
        json_ld_tag = soup.find("script", type="application/ld+json")
        if not json_ld_tag:
            return "Producto Nike", None, None

        data = json.loads(json_ld_tag.string)

        # Nombre
        nombre = data.get("name", "Producto Nike")

        # Precio
        precio = None
        if "offers" in data and "price" in data["offers"]:
            precio = float(data["offers"]["price"])

        # Imagen
        foto_url = None
        if "image" in data:
            if isinstance(data["image"], list):
                foto_url = data["image"][0]
            else:
                foto_url = data["image"]

        return nombre, precio, foto_url

    except Exception as e:
        print("Error:", e)
        return "Producto Nike", None, None

def mensaje_motivacional(precio):
    """
    Mensaje según el precio
    """
    if precio is None:
        return "❓ Precio no disponible, revisa más tarde."
    elif precio < 90:
        return "🔥 ¡Excelente precio! ¡Es hora de comprar!"
    elif 90 <= precio <= 110:
        return "💡 Buen precio, tu decides si aprovecharlo."
    else:
        return "⚠️ Precio alto, tal vez espera un poco."

def enviar_telegram(foto, mensaje, url):
    """
    Envía la info del producto a Telegram
    """
    text = f"{mensaje}\n\nCompra aquí: {url}"
    if foto:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            params={"chat_id": TELEGRAM_CHAT_ID, "photo": foto, "caption": text},
        )
    else:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            params={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        )

def main():
    """
    Recorre todas las URLs, obtiene info y envía Telegram
    """
    for url in URLS:
        nombre, precio, foto = obtener_info_producto(url)
        print(f"DEBUG → {nombre} | Precio: {precio} | Foto: {foto}")
        mensaje = mensaje_motivacional(precio)
        enviar_telegram(foto, f"{nombre}\n{mensaje}", url)

if __name__ == "__main__":
    main()
