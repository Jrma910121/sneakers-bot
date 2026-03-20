import os
import time
import random
import requests
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
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(10)
        
        # Scroll para asegurar carga de datos reales
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. PRECIOS REALES (Solo del contenedor principal)
        precio_final = "Ver en web"
        precio_original = ""
        try:
            # Buscamos el bloque de precio oficial del producto
            contenedor_precio = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price-container"], .product-price')
            elementos_p = contenedor_precio.find_elements(By.XPATH, ".//*[contains(text(), '$')]")
            
            precios_lista = []
            for p in elementos_p:
                texto = p.text.replace('\n', '').strip()
                val = ''.join(c for c in texto if c.isdigit() or c == '.')
                if val: 
                    precios_lista.append(float(val))
            
            precios_lista = sorted(list(set(precios_lista)), reverse=True)
            
            if len(precios_lista) >= 2:
                precio_original = f"${precios_lista[0]:.2f}"
                precio_final = f"${precios_lista[-1]:.2f}"
            elif len(precios_lista) == 1:
                precio_final = f"${precios_lista[0]:.2f}"
        except:
            precio_final = "Consultar"

        # 3. DETECCIÓN DE DESCUENTO EXTRA (Sintaxis Corregida)
        promo_extra = False
        try:
            full_html = driver.page_source.lower()
            keywords = ["extra 20%", "extra 25%", "extra 10%", "off in cart", "off at checkout"]
            
            # Buscamos banners específicos de promoción
            banners = driver.find_elements(By.CSS_SELECTOR, ".messaging-banner, [data-test='pdp-messaging-banner']")
            texto_banners = " ".join([b.text.lower() for b in banners])
            
            if any(k in full_html for k in keywords) or any(k in texto_banners for k in keywords):
                promo_extra = True
        except:
            pass

        # 4. IMAGEN HD (Limpieza de URL para 1600px)
        foto_url = None
        try:
            img_el = driver.find_element(By.CSS_SELECTOR, 'img[data-testid="hero-img"], .pdp-6-up-image img')
            raw_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")
            if raw_url:
                base = raw_url.split("?")[0]
                foto_url = f"{base}?wid=1600&fmt=jpeg&qlt=90"
        except:
            pass

        # 5. Formato Mensaje (Español)
        precios_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>" if precio_original else f"<b>{precio_final}</b>"
        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nEste modelo tiene una rebaja adicional al añadirlo al carrito." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {precios_display}{aviso_promo}\n\n"
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
