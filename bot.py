import requests
from bs4 import BeautifulSoup
from telegram import Bot

# --- CONFIGURACIÓN ---
TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"  # Reemplaza con tu token
CHAT_ID = "8751177346"            # Reemplaza con tu chat ID
bot = Bot(token=TOKEN)

# --- FUNCIÓN PARA EXTRAER INFO DEL PRODUCTO ---
def obtener_info_producto(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Nombre y subtitulo
        nombre_tag = soup.find("h1", {"data-testid": "product_title"})
        subtitulo_tag = soup.find("h2", {"data-testid": "product_subtitle"})
        nombre = nombre_tag.text.strip() if nombre_tag else "Producto Nike"
        subtitulo = subtitulo_tag.text.strip() if subtitulo_tag else ""

        # Precio actual
        precio_tag = soup.find("span", {"data-testid": "currentPrice-container"})
        precio = precio_tag.text.strip() if precio_tag else "Precio no disponible"

        # Imagen principal
        foto_tag = soup.find("img", {"data-testid": "HeroImg"})
        foto_url = foto_tag["src"] if foto_tag else None

        return nombre, subtitulo, precio, foto_url

    except Exception as e:
        print("Error al obtener producto:", e)
        return "Producto Nike", "", "Precio no disponible", None

# --- FUNCIÓN PARA ENVIAR MENSAJE A TELEGRAM ---
def enviar_telegram(producto_url):
    nombre, subtitulo, precio, foto_url = obtener_info_producto(producto_url)

    mensaje = f"{nombre}\n{subtitulo}\nPrecio: {precio}\n{producto_url}"

    if foto_url:
        bot.send_photo(chat_id=CHAT_ID, photo=foto_url, caption=mensaje)
    else:
        bot.send_message(chat_id=CHAT_ID, text=mensaje)

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    url_producto = "https://www.nike.com/t/air-max-plus-g-golf-shoes-etVKhXd4"  # Cambia por el producto que quieras
    enviar_telegram(url_producto)
