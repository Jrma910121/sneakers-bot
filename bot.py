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
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        # Espera extendida para que el script de precios de Nike se ejecute
        time.sleep(15) 
        
        # Scroll para disparar eventos de carga
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(2)
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. PRECIO (Extracción por Regex sobre Texto Plano) - NUEVO MÉTODO
        precio_final = "Consultar"
        precio_original = ""
        try:
            # Obtenemos todo el texto visible de la página
            texto_pagina = driver.execute_script("return document.body.innerText")
            
            # Buscamos patrones de precio como $120.00 o $99
            encontrados = re.findall(r'\$\d+(?:\.\d{2})?', texto_pagina)
            
            # Limpiamos y eliminamos duplicados manteniendo el orden
            precios_limpios = []
            for p in encontrados:
                num = float(p.replace('$', ''))
                if num > 10 and num not in precios_limpios: # Filtro para evitar precios de envío o tallas
                    precios_limpios.append(num)
            
            # Tomamos los primeros 2 precios que aparezcan (suelen ser el original y el de oferta)
            if len(precios_limpios) >= 2:
                # En Nike, el primero suele ser el actual y el segundo el original, o viceversa.
                # Comparamos para poner el mayor como original.
                p1, p2 = precios_limpios[0], precios_limpios[1]
                precio_original = f"${max(p1, p2):.2f}"
                precio_final = f"${min(p1, p2):.2f}"
            elif len(precios_limpios) == 1:
                precio_final = f"${precios_limpios[0]:.2f}"
        except:
            pass

        # 3. IMAGEN HD (Método Directo)
        foto_url = None
        try:
            img_el = driver.find_element(By.XPATH, "//img[contains(@src, 'static.nike.com/a/images')]")
            src = img_el.get_attribute("src")
            if src:
                base = src.split("?")[0]
                foto_url = f"{base}?wid=1200&fmt=jpeg&qlt=90"
        except:
            pass

        # 4. DESCUENTO EXTRA (Búsqueda en texto)
        promo_extra = False
        if "extra" in texto_pagina.lower() and any(x in texto_pagina.lower() for x in ["cart", "checkout", "bag", "off"]):
            promo_extra = True

        # 5. Formato Mensaje
        p_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>" if precio_original else f"<b>{precio_final}</b>"
        aviso = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nEste producto tiene rebaja adicional al añadirlo al carro." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {p_display}{aviso}\n\n"
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
