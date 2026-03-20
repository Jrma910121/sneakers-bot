import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def enviar_telegram_con_foto(mensaje, foto_url):
    """Envía una foto con un texto descriptivo y sin vista previa de link."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    
    # Usamos sendPhoto en lugar de sendMessage
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": foto_url,
        "caption": mensaje,
        "parse_mode": "Markdown"
    }
    # Al enviar como foto, la vista previa del link del mensaje no se genera
    requests.post(url, json=payload)

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

def obtener_datos_nike_usa(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(8, 12))
        
        # 1. Obtener Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Nike Product"

        # 2. Obtener Precio
        precio = "Not found"
        elementos_precio = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
        for el in elementos_precio:
            texto = el.text.strip()
            if "$" in texto and len(texto) < 12 and any(c.isdigit() for c in texto):
                precio = texto
                break

        # 3. Obtener Imagen del Producto (Mejorado)
        # Nike usa imágenes con el atributo 'alt' igual al nombre del producto o clases específicas
        foto_url = "https://www.nike.com/static/images/logo.png" # Imagen por defecto si falla
        try:
            # Buscamos la primera imagen del carrusel de producto
            img_element = driver.find_element(By.CSS_SELECTOR, "img[data-testid='hero-img'], img.css-viha7l")
            foto_url = img_element.get_attribute("src")
        except:
            try:
                # Intento alternativo
                img_element = driver.find_element(By.CSS_SELECTOR, "#pdp-6-up-image-0, .pdp-6-up-image")
                foto_url = img_element.get_attribute("src")
            except:
                pass

        mensaje = (
            f"🇺🇸 *NIKE USA ALERT*\n\n"
            f"👟 *Product:* {nombre}\n"
            f"💰 *Price:* {precio}\n\n"
            f"🔗 [Link to Shop]({url})"
        )
        
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:50]}", None

def main():
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-j1G9vB/CW2288-111"
    ]

    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike_usa(driver, link)
        if foto:
            enviar_telegram_con_foto(mensaje, foto)
        else:
            # Si no hay foto, enviar solo texto (fallback)
            requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage", 
                          json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": mensaje, "parse_mode": "Markdown"})
        time.sleep(5)
    
    driver.quit()

if __name__ == "__main__":
    main()
