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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(8) # Más tiempo para que carguen los banners de promo
        
        # Scroll profundo para forzar la aparición de mensajes de marketing
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(5) 
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Producto Nike"

        # 2. DETECCIÓN ULTRA-SENSIBLE DE DESCUENTO
        promo_extra = False
        try:
            # Opción A: Buscar en el texto general (incluyendo capas ocultas)
            texto_completo = driver.execute_script("return document.body.innerText").lower()
            
            # Opción B: Buscar específicamente en los elementos de "Messaging" de Nike
            banners = driver.find_elements(By.CSS_SELECTOR, '[data-test="pdp-messaging-banner"], .pdp-messaging, .promo-link, .pdp-promo')
            texto_banners = " ".join([b.text.lower() for b in banners])
            
            # Combinamos todo para el escaneo
            pool_texto = texto_completo + " " + texto_banners
            
            keywords = ["extra", "off in cart", "off at checkout", "discount applied", "member product"]
            if "extra" in pool_texto and any(word in pool_texto for word in ["cart", "checkout", "bag", "code", "off"]):
                promo_extra = True
        except:
            pass

        # 3. Precios
        precios_encontrados = []
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
        for el in elementos:
            t = el.text.strip()
            if "$" in t and 1 < len(t) < 15 and any(c.isdigit() for c in t):
                if t not in precios_encontrados:
                    precios_encontrados.append(t)

        precio_final = "Ver en web"
        precio_original = ""
        
        if len(precios_encontrados) >= 2:
            try:
                nums_raw = []
                for p in precios_encontrados:
                    val = ''.join(c for c in p if c.isdigit() or c == '.')
                    if val: nums_raw.append(float(val))
                nums = sorted(list(set(nums_raw)), reverse=True)
                if len(nums) >= 2:
                    precio_original = f"${nums[0]:.2f}"
                    precio_final = f"${nums[-1]:.2f}"
            except:
                precio_final = precios_encontrados[0]
        elif len(precios_encontrados) == 1:
            precio_final = precios_encontrados[0]

        # 4. Imagen con CALIDAD HD 2000px
        foto_url = None
        selectors_img = ['img.pdp-6-up-image', 'img[data-testid="hero-img"]', '.css-viha7l']
        for sel in selectors_img:
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, sel)
                temp_url = img_el.get_attribute("src")
                if temp_url and "data:image" not in temp_url:
                    base = temp_url.split("?")[0]
                    # Subimos a 1600px para máxima nitidez
                    foto_url = f"{base}?wid=1600&fmt=jpeg&qlt=95"
                    break
            except:
                continue

        # 5. Formato Mensaje (ESPAÑOL)
        if precio_original and precio_original != precio_final:
            display_price = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            display_price = f"<b>{precio_final}</b>"

        # Aviso resaltado
        aviso_carrito = "\n\n🎁 <b>¡DESCUENTO ADICIONAL!</b>\nEste producto tiene una rebaja extra al añadirlo al carrito o usar un código." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {display_price}{aviso_carrito}\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:50]}", None

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
