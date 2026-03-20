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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(8)
        
        # 1. Nombre del Producto
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. Detección de Descuento en Carrito
        promo_extra = False
        try:
            texto_pagina = driver.find_element(By.TAG_NAME, "body").text.lower()
            if ("extra" in texto_pagina and "cart" in texto_pagina) or \
               ("discount" in texto_pagina and "at checkout" in texto_pagina) or \
               ("extra" in texto_pagina and "bag" in texto_pagina):
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
                else:
                    precio_final = f"${nums[0]:.2f}"
            except:
                precio_final = precios_encontrados[0]
        elif len(precios_encontrados) == 1:
            precio_final = precios_encontrados[0]

        # 4. Imagen
        foto_url = None
        for sel in ['img[data-testid="hero-img"]', '.css-viha7l', 'img[alt*="' + nombre[:5] + '"]']:
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, sel)
                temp_url = img_el.get_attribute("src")
                if temp_url and "data:image" not in temp_url:
                    foto_url = temp_url
                    break
            except:
                continue

        # 5. Formato del Mensaje en ESPAÑOL
        if precio_original and precio_original != precio_final:
            display_price = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            display_price = f"<b>{precio_final}</b>"

        # Aviso de promoción adicional
        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA!</b> Este artículo tiene una rebaja adicional al añadirlo al carrito." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {display_price}{aviso_promo}\n\n"
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
