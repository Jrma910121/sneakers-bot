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
        time.sleep(12) 
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. PRECIO REAL (Filtrado por Contenedor de Producto)
        precio_final = "Consultar"
        precio_original = ""
        try:
            # Intentamos localizar el área específica donde Nike pone el precio del producto principal
            # Usamos selectores que Nike USA prioriza para el precio actual
            selectors_precio = [
                'div[data-test="product-price"]',
                '.product-price',
                '[data-test="product-price-reduced"]',
                '.is--current-price'
            ]
            
            precios_encontrados = []
            for selector in selectors_precio:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elementos:
                    texto = el.text.replace('\n', ' ').strip()
                    # Extraer solo lo que parece precio ($XX.XX)
                    matches = re.findall(r'\$\d+(?:\.\d{2})?', texto)
                    for m in matches:
                        num = float(m.replace('$', ''))
                        if num > 15: # Evitamos precios de calcetines o envíos
                            precios_encontrados.append(num)
                if precios_encontrados: break

            # Limpiar duplicados manteniendo el orden de aparición
            unique_prices = []
            for p in precios_encontrados:
                if p not in unique_prices: unique_prices.append(p)

            if len(unique_prices) >= 2:
                # Nike suele poner: [Precio Rebajado, Precio Original] o viceversa
                p_actual = unique_prices[0]
                p_viejo = unique_prices[1]
                if p_viejo > p_actual:
                    precio_original = f"${p_viejo:.2f}"
                    precio_final = f"${p_actual:.2f}"
                else:
                    precio_final = f"${p_actual:.2f}"
            elif len(unique_prices) == 1:
                precio_final = f"${unique_prices[0]:.2f}"
        except:
            pass

        # 3. IMAGEN HD
        foto_url = None
        try:
            # Buscamos la imagen principal que no sea un icono pequeño
            img_el = driver.find_element(By.XPATH, "//img[contains(@src, 'static.nike.com/a/images') and not(contains(@src, 'width=64'))]")
            src = img_el.get_attribute("src")
            if src:
                base = src.split("?")[0]
                foto_url = f"{base}?wid=1500&fmt=jpeg&qlt=90"
        except:
            pass

        # 4. DETECCIÓN DE DESCUENTO EXTRA
        promo_extra = False
        try:
            full_text = driver.execute_script("return document.body.innerText").lower()
            if "extra" in full_text and any(x in full_text for x in ["cart", "checkout", "bag", "off"]):
                promo_extra = True
        except:
            pass

        # 5. Formato Mensaje
        p_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>" if precio_original else f"<b>{precio_final}</b>"
        aviso = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nEste modelo tiene rebaja adicional al añadirlo al carrito." if promo_extra else ""

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
    # Asegúrate de usar las URLs correctas de Nike USA
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
