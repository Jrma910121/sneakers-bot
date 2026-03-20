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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(8)
        
        # Scroll suave para activar carga de imágenes y banners de promo
        driver.execute_script("window.scrollTo({top: 600, behavior: 'smooth'});")
        time.sleep(3)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(5)
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. DETECCIÓN DE DESCUENTO EXTRA (Banner y Texto)
        promo_extra = False
        try:
            # Escaneamos el texto de toda la página para encontrar avisos de promo
            texto_completo = driver.execute_script("return document.body.innerText").lower()
            keywords_promo = ["extra", "off in cart", "off at checkout", "discount applied in bag", "promo code"]
            
            # Si contiene 'extra' y alguna referencia a compra/pago
            if "extra" in texto_completo and any(word in texto_completo for word in ["cart", "bag", "checkout", "off", "code"]):
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

        # 4. Imagen - SOPORTE PARA SRCSET (ALTA CALIDAD)
        foto_url = None
        selectors_img = [
            'img[data-testid="hero-img"]',
            'img[class*="css-viha7l"]',
            'img.pdp-6-up-image',
            '.pdp-6-up-image img'
        ]
        
        for sel in selectors_img:
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, sel)
                # Primero intentamos sacar el srcset para la mejor resolución
                src_data = img_el.get_attribute("srcset")
                if src_data:
                    # Tomamos la última URL del set (es la de mayor resolución)
                    foto_url = src_data.split(",")[-1].split(" ")[0].strip()
                else:
                    foto_url = img_el.get_attribute("src")
                
                if foto_url and "data:image" not in foto_url:
                    # Limpiamos URL y forzamos resolución 1600px
                    base = foto_url.split("?")[0]
                    foto_url = f"{base}?wid=1600&fmt=jpeg&qlt=95"
                    break
            except:
                continue

        # 5. Mensaje en ESPAÑOL
        if precio_original and precio_original != precio_final:
            texto_precio = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            texto_precio = f"<b>{precio_final}</b>"

        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA!</b>\nEste producto tiene una rebaja adicional al añadirlo al carrito." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {texto_precio}{aviso_promo}\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:40]}", None

def main():
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100",
        "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007"
    ]
    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        time.sleep(random.uniform(5, 8))
    driver.quit()

if __name__ == "__main__":
    main()
