import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configuración (Usa variables de entorno para seguridad)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URLS = [
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
    # ... el resto de tus URLs
]

def configurar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def obtener_info_producto(driver, url):
    try:
        driver.get(url)
        time.sleep(3) # Nike a veces tarda en renderizar el JS
        
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Selectores mediante Meta Tags (más estables)
        foto_tag = soup.find("meta", property="og:image")
        foto_url = foto_tag["content"] if foto_tag else None

        nombre_tag = soup.find("meta", property="og:title")
        nombre = nombre_tag["content"] if nombre_tag else "Producto Nike"

        precio_tag = soup.find("meta", property="product:price:amount")
        precio = float(precio_tag["content"]) if precio_tag else None

        return nombre, precio, foto_url
    except Exception as e:
        print(f"Error en {url}: {e}")
        return None, None, None

def mensaje_motivacional(precio):
    if precio is None: return "❓ Precio no disponible."
    if precio < 90: return "🔥 ¡Excelente precio! ¡Es hora de comprar!"
    if precio <= 110: return "💡 Buen precio, tú decides."
    return "⚠️ Precio alto, tal vez espera un poco."

def enviar_telegram(foto, mensaje, url):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"{mensaje}\n\nCompra aquí: {url}"}
    
    if foto:
        payload["photo"] = foto
        requests.post(f"{base_url}/sendPhoto", data=payload)
    else:
        payload["text"] = payload.pop("caption")
        requests.post(f"{base_url}/sendMessage", data=payload)

def main():
    driver = configurar_driver()
    try:
        for url in URLS:
            nombre, precio, foto = obtener_info_producto(driver, url)
            if nombre:
                print(f"Procesado: {nombre} - ${precio}")
                mensaje = mensaje_motivacional(precio)
                enviar_telegram(foto, f"{nombre}\nPrecio: ${precio}\n{mensaje}", url)
    finally:
        driver.quit() # Cerramos el navegador al final de todo el ciclo

if __name__ == "__main__":
    main()
