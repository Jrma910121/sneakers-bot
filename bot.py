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
    """Envía la notificación a Telegram. Si la foto falla, envía solo texto."""
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
        r = requests.post(url_api, json=payload)
        # Si la foto da error (ej. URL expirada o bloqueada), fallback a mensaje de texto
        if r.status_code != 200:
            url_api = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id, 
                "text": mensaje, 
                "parse_mode": "HTML", 
                "disable_web_page_preview": True
            }
            requests.post(url_api, json=payload)
    else:
        url_api = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": mensaje, 
            "parse_mode": "HTML", 
            "disable_web_page_preview": True
        }
        requests.post(url_api, json=payload)

def iniciar_driver():
    """Configuración del navegador con parámetros de sigilo y resolución HD."""
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
    
    # Ocultar rastro de automatización
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        
        # Scroll para activar carga de imágenes y precios dinámicos
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(8)
        
        # 1. Nombre del Producto
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. Detección de Descuento Adicional en Carrito
        promo_extra = False
        try:
            texto_pagina = driver.find_element(By.TAG_NAME, "body").text.lower()
            keywords = ["extra", "cart", "checkout", "bag", "discount"]
            # Si contiene 'extra' y alguna referencia al carrito/pago
            if "extra" in texto_pagina and any(x in texto_pagina for x in ["cart", "bag", "checkout"]):
                promo_extra = True
        except:
            pass

        # 3. Extracción de Precios
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

        # 4. Imagen con MEJORA DE CALIDAD (HD)
        foto_url = None
        selectors_img = [
            'img[data-testid="hero-img"]', 
            '.css-viha7l', 
            'img[alt*="' + nombre[:5] + '"]'
        ]
        
        for sel in selectors_img:
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, sel)
                temp_url = img_el.get_attribute("src")
                if temp_url and "data:image" not in temp_url:
                    # Limpiamos y forzamos resolución alta (1200px)
                    if "?" in temp_url:
                        base = temp_url.split("?")[0]
                        foto_url = f"{base}?wid=1200&fmt=jpeg&qlt=90"
                    else:
                        foto_url = f"{temp_url}?wid=1200"
                    break
            except:
                continue

        # 5. Formato del Mensaje (Español + HTML)
        if precio_original and precio_original != precio_final:
            texto_precio = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            texto_precio = f"<b>{precio_final}</b>"

        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA!</b> Este artículo tiene una rebaja adicional al añadirlo al carrito." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {texto_precio}{aviso_promo}\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error en el bot: {str(e)[:50]}", None

def main():
    # LISTA DE URLs A MONITOREAR
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-j1G9vB/CW2288-111",
        "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007"
    ]

    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        # Pausa aleatoria para evitar detección entre productos
        time.sleep(random.uniform(3, 7))
    
    driver.quit()

if __name__ == "__main__":
    main()
