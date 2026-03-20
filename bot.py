import requests
import re
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
    # ... agrega más URLs aquí
]

# ---------------------------
# Funciones
# ---------------------------
def obtener_info_producto(url):
    """
    Extrae info de producto Nike: nombre, precio, foto
    usando JSON interno de la página.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        html = r.text

        # Buscar el JSON que contiene los datos reales
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*});', html)
        if not match:
            return "Producto Nike", None, None

        data = json.loads(match.group(1))

        # Acceder a los datos de la página
        product_id = list(data["products"].keys())[0]
        product = data["products"][product_id]

        nombre = product.get("fullTitle", "Producto Nike")
        precio = product.get("merchPrice", {}).get("currentPrice")
        foto_url = None

        # Fotos
        images = product.get("images", [])
        if images:
            foto_url = images[0].get("url")

        return nombre, precio, foto_url

    except Exception as e:
        print("Error:", e)
        return "Producto Nike", None, None

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
