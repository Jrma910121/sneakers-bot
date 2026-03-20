import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def enviar_notificacion(mensaje, foto_url=None):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Si tenemos una URL de foto válida, intentamos enviarla
    if foto_url and foto_url.startswith("http"):
        url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": foto_url,
            "caption": mensaje,
            "parse_mode": "Markdown"
        }
    else:
        # Si no hay foto, enviamos solo texto para asegurar que llegue algo
        url_api = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True # ESTO QUITA LA VISTA PREVIA FEA
        }
    
    try:
        r = requests.post(url_api, json=payload)
        print(f"Respuesta Telegram: {r.status_code}")
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(10, 15)) # Nike USA es lenta cargando
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Nike Sneaker"

        # 2. Precio
        precio = "Check site"
        try:
            # Buscamos por el atributo data-test que es el más fiable en USA
            precio_el = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"], [data-test="product-price-reduced"]')
            precio = precio_el.text
        except:
            # Fallback a buscar el símbolo $
            elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
            for el in elementos:
                if "$" in el.text and len(el.text) < 15:
                    precio = el.text
                    break

        # 3. Imagen (Búsqueda más profunda)
        foto_url = None
        try:
            # Nike USA usa mucho el atributo data-testid="hero-img"
            img_el = driver.find_element(By.CSS_SELECTOR, 'img[data-testid="hero-img"], .css-viha7l, img[alt*="' + nombre[:10] + '"]')
            foto_url = img_el.get_attribute("src")
        except:
            print("No se pudo extraer la imagen del producto")

        mensaje = (
            f"🇺🇸 *NIKE USA ALERT*\n\n"
            f"👟 *Product:* {nombre}\n"
            f"💰 *Price:* {precio}\n\n"
            f"🔗 [Link to Shop]({url})"
        )
        
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error monitoreando: {str(e)[:50]}", None

def main():
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100",
        "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007"
    ]

    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        time.sleep(5)
    
    driver.quit()

if __name__ == "__main__":
    main()
