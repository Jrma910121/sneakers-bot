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
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Intentar enviar con foto, si falla o no hay, enviar solo texto
    if foto_url and foto_url.startswith("http"):
        url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": foto_url, "caption": mensaje, "parse_mode": "HTML"}
        r = requests.post(url_api, json=payload)
        if r.status_code != 200: # Si Telegram rechaza la foto, enviamos texto
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
        time.sleep(random.uniform(12, 18)) # Más tiempo para asegurar carga
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Nike Product"

        # 2. Precios (Búsqueda por texto para evitar fallos de selectores)
        precios_encontrados = []
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
        for el in elementos:
            t = el.text.strip()
            if "$" in t and 1 < len(t) < 15 and any(c.isdigit() for c in t):
                if t not in precios_encontrados:
                    precios_encontrados.append(t)

        # Lógica: Si hay 2 precios, el más alto suele ser el original
        precio_final = "Check Site"
        precio_original = ""
        
        if len(precios_encontrados) >= 2:
            # Ordenamos para identificar el mayor (original) y menor (oferta)
            # Limpiamos caracteres no numéricos para comparar
            nums = sorted([float(''.join(c for c in p if c.isdigit() or c == '.')) for p in precios_encontrados], reverse=True)
            precio_original = f"${nums[0]:.2f}"
            precio_final = f"${nums[-1]:.2f}"
        elif len(precios_encontrados) == 1:
            precio_final = precios_encontrados[0]

        # 3. Imagen (Selector genérico de Nike)
        foto_url = None
        for selector in ['img[data-testid="hero-img"]', '.css-viha7l', 'img[alt*="shoe"]', 'img[alt*="shoe"]']:
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, selector)
                foto_url = img_el.get_attribute("src")
                if foto_url: break
            except:
                continue

        # 4. Formato Mensaje
        if precio_original and precio_original != precio_final:
            display_price = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            display_price = f"<b>{precio_final}</b>"

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
    urls = ["https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100".
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
