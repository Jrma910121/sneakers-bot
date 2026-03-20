import requests
import re
import json
from bs4 import BeautifulSoup

# ---------------------------
# Configuración Telegram
# ---------------------------
TELEGRAM_TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"
TELEGRAM_CHAT_ID = "8751177346"

# ---------------------------
# Lista de URLs de productos Nike
# ---------------------------
URLS = [
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/BV1358-003",
    # agrega más URLs aquí
]

# ---------------------------
# Funciones
# ---------------------------
def obtener_info_producto(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        html = r.text

        # Valores por defecto
        nombre = "Producto Nike"
        precio = None
        foto_url = None

        # Nombre y foto de respaldo desde meta tags
        soup = BeautifulSoup(html, "html.parser")
        nombre_tag = soup.find("meta", property="og:title")
        if nombre_tag: nombre = nombre_tag["content"]
        foto_tag = soup.find("meta", property="og:image")
        if foto_tag: foto_url = foto_tag["content"]

        # Intentar extraer JSON interno de Nike
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*});', html)
        if match:
            data = json.loads(match.group(1))
            if "products" in data and data["products"]:
                product_id = list(data["products"].keys())[0]
                product = data["products"][product_id]

                # Precio
                if "merchPrice" in product and "currentPrice" in product["merchPrice"]:
                    precio = product["merchPrice"]["currentPrice"]

                # Foto principal
                images = product.get("images", [])
                if images:
                    foto_url = images[0].get("url", foto_url)

                # Nombre completo
                nombre = product.get("fullTitle", nombre)

        return nombre, precio, foto_url

    except Exception as e:
        print("Error:", e)
        return "Producto Nike", None, foto_url

def mensaje_motivacional(precio):
    if precio is None:
        return "❓ Precio no disponible, revisa más tarde."
    elif precio < 90:
        return "🔥 ¡Excelente precio! ¡Es hora de comprar!"
    elif 90 <= precio <= 110:
        return "💡 Buen precio, tu decides si aprovecharlo."
    else:
        return "⚠️ Precio alto, tal vez espera un poco."

def enviar_telegram(foto, mensaje, url):
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
    for url in URLS:
        nombre, precio, foto = obtener_info_producto(url)
        print(f"DEBUG → {nombre} | Precio: {precio} | Foto: {foto}")
        mensaje = mensaje_motivacional(precio)
        enviar_telegram(foto, f"{nombre}\n{mensaje}", url)

if __name__ == "__main__":
    main()
