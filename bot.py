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
    """Envía la notificación con imagen (si existe) o texto, usando HTML."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if foto_url and foto_url.startswith("http"):
        url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": foto_url,
            "caption": mensaje,
            "parse_mode": "HTML"
        }
    else:
        url_api = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
    
    try:
        r = requests.post(url_api, json=payload)
        print(f"Telegram Status: {r.status_code}")
    except Exception as e:
        print(f"Error Telegram: {e}")

def iniciar_driver():
    """Configuración de navegador indetectable."""
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
        time.sleep(random.uniform(10, 15))
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Nike Sneaker"

        # 2. Precios
        precio_actual = ""
        precio_original = ""

        try:
            # Buscamos el precio con descuento (o el único precio si no hay oferta)
            el_promo = driver.find_elements(By.CSS_SELECTOR, '[data-test="product-price-reduced"]')
            el_regular = driver.find_elements(By.CSS_SELECTOR, '[data-test="product-price"]')
            
            if el_promo:
                precio_actual = el_promo[0].text
                # Si hay promo, buscamos el original (tachado)
                el_full = driver.find_elements(By.CSS_SELECTOR, '[data-test="product-price-actual"]')
                if el_full:
                    precio_original = el_full[0].text
            elif el_regular:
                precio_actual = el_regular[0].text
        except:
            precio_actual = "Check Site"

        # 3. Imagen
        foto_url = None
        try:
            img_el = driver.find_element(By.CSS_SELECTOR, 'img[data-testid="hero-img"], .css-viha7l')
            foto_url = img_el.get_attribute("src")
        except:
            pass

        # 4. Formatear Mensaje en HTML
        # Si hay precio original, lo tachamos con <s>
        if precio_original and precio_original != precio_actual:
            display_price = f"<s>{precio_original}</s> 🔥 <b>{precio_actual}</b>"
        else:
            display_price = f"<b>{precio_actual}</b>"

        mensaje = (
            f"🇺🇸 <b>NIKE USA ALERT</b>\n\n"
            f"👟 <b>Product:</b> {nombre}\n"
            f"💰 <b>Price:</b> {display_price}\n\n"
            f'🔗 <a href="{url}">Link to Shop</a>'
        )
        
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:50]}", None

def main():
    # LISTA DE URLs (USA)
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-j1G9vB/CW2288-111"
    ]

    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        time.sleep(5)
    
    driver.quit()

if __name__ == "__main__":
    main()
