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
    chrome_options.add_argument("--window-size=2560,1440") 
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # User-agent muy específico para evitar ser detectado como bot
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(12) # Tiempo extra para que los scripts de Nike carguen la promo
        
        # Simulación de interacción humana para disparar banners de promo
        driver.execute_script("window.scrollTo({top: 800, behavior: 'smooth'});")
        time.sleep(3)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(2)
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. DETECCIÓN AGRESIVA DE DESCUENTOS OCULTOS
        promo_extra = False
        try:
            # Buscamos en el HTML crudo (incluyendo lo que no se ve)
            html_source = driver.page_source.lower()
            
            # Lista de frases que usa Nike para promos en el carrito
            keywords_ocultas = [
                "extra 20%", "extra 25%", "extra 10%", 
                "off in cart", "off at checkout", 
                "discount applied in bag", "promo code",
                "member_promo", "extra_off"
            ]
            
            if any(key in html_source for key in keywords_ocultas):
                promo_extra = True
            
            # Si no lo encuentra, busca específicamente en los banners de 'Messaging'
            banners = driver.find_elements(By.CSS_SELECTOR, ".messaging-banner, .pdp-messaging, [data-test='pdp-messaging-banner']")
            for b in banners:
                if "extra" in b.text.lower() or "off" in b.text.lower():
                    promo_extra = True
                    break
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

        # 4. IMAGEN HD REAL (FORZADO)
        foto_url = None
        try:
            # Buscamos la imagen principal por múltiples métodos
            img_element = driver.find_element(By.CSS_SELECTOR, 'img[data-testid="hero-img"], .pdp-6-up-image img, img[alt*="' + nombre[:5] + '"]')
            raw_url = img_element.get_attribute("src")
            
            if not raw_url or "data:image" in raw_url:
                raw_url = img_element.get_attribute("data-src")

            if raw_url:
                # Limpieza y forzado de resolución 1600px
                base = raw_url.split("?")[0]
                foto_url = f"{base}?wid=1600&fmt=jpeg&qlt=95"
        except:
            pass

        # 5. Formato Mensaje (Español)
        if precio_original and precio_original != precio_final:
            texto_precio = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            texto_precio = f"<b>{precio_final}</b>"

        # Aviso de descuento con emoji llamativo
        aviso_promo = "\n\n🚨 <b>¡OFERTA OCULTA DETECTADA!</b>\nEste modelo tiene un <b>descuento adicional</b> al añadirlo al carrito o usar código." if promo_extra else ""

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
