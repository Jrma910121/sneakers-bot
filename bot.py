import os
import time
import random
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def enviar_notificacion(mensaje, foto_url=None):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if foto_url and foto_url.startswith("http"):
        url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": foto_url, "caption": mensaje, "parse_mode": "HTML"}
        r = requests.post(url_api, json=payload)
        if r.status_code != 200:
            url_api = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML", "disable_web_page_preview": True}
            requests.post(url_api, json=payload)
    else:
        url_api = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML", "disable_web_page_preview": True}
        requests.post(url_api, json=payload)

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(12) 
        
        # 1. Nombre del Producto
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text
        except:
            nombre = "Producto Nike"

        # 2. PRECIO REAL (Filtrado Visual Estricto)
        precio_final = "Consultar"
        precio_original = ""
        
        try:
            # Buscamos SOLO en el área donde Nike pone el precio oficial (derecha arriba)
            # Evitamos el código fuente global para no pescar precios basura
            bloque_precio = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price-container"], .pdp-6-up-price, .product-price')
            texto_precios = bloque_precio.text.replace(',', '').strip()
            
            # Buscamos números con formato $XX.XX
            matches = re.findall(r'\$\s?(\d+(?:\.\d{2})?)', texto_precios)
            
            # Convertir a float y limpiar
            precios_lista = sorted(list(set([float(m) for m in matches])), reverse=True)
            
            if len(precios_lista) >= 2:
                # El mayor es el tachado, el menor es el actual
                precio_original = f"${precios_lista[0]:.2f}"
                precio_final = f"${precios_lista[-1]:.2f}"
            elif len(precios_lista) == 1:
                precio_final = f"${precios_lista[0]:.2f}"
        except:
            pass

        # 3. IMAGEN HD
        foto_url = None
        try:
            img = driver.find_element(By.XPATH, "//img[contains(@src, 'static.nike.com/a/images') and not(contains(@src, 'width=64'))]")
            src = img.get_attribute("src")
            if src:
                foto_url = src.split('?')[0] + "?wid=1500&fmt=jpeg&qlt=90"
        except: pass

        # 4. DESCUENTO EXTRA EN CARRITO
        promo_extra = False
        try:
            # Escanear solo banners de texto arriba del botón de compra
            msg_banner = driver.find_element(By.CSS_SELECTOR, '[data-test="pdp-messaging-banner"], .pdp-messaging').text.lower()
            if "extra" in msg_banner or "off" in msg_banner:
                promo_extra = True
        except:
            # Fallback: buscar en toda la página si el banner no tiene ese ID
            if "extra" in driver.page_source.lower() and "cart" in driver.page_source.lower():
                promo_extra = True

        # 5. Formato del Mensaje
        p_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>" if precio_original else f"<b>{precio_final}</b>"
        
        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nEste modelo tiene una rebaja adicional al pagar." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {p_display}\n"
            f"{aviso_promo}\n"
            f"--------------------------------\n"
            f"📌 <i>Nota: Precios antes de taxes. El valor final varía según el lugar de entrega en USA.</i>\n\n"
            f"📦 <b>Envío a Colombia:</b> Requiere el uso de casillero virtual.\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:30]}", None

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
