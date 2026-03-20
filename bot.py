import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # User-Agent americano
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Ocultar rastro de bot
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def obtener_precio_usa(driver, url):
    try:
        driver.get(url)
        # Espera para que carguen los precios en dólares (dinámicos)
        time.sleep(random.uniform(8, 12))
        
        # Intentar obtener el nombre del modelo
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Nike Product (USA)"

        # Buscar el precio con el símbolo $
        precio = None
        # Buscamos elementos que contengan "$" y tengan números
        elementos_precio = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
        
        for el in elementos_precio:
            texto = el.text.strip()
            # Filtro para evitar textos largos, solo queremos el precio (ej: $110 o $110.00)
            if "$" in texto and len(texto) < 12 and any(c.isdigit() for c in texto):
                precio = texto
                break

        if precio:
            return f"🇺🇸 *NIKE USA ALERT*\n👟 *Product:* {nombre}\n💰 *Price:* {precio}\n🔗 [View on Nike]({url})"
        else:
            return f"⚠️ *{nombre}*: Price not found. Nike USA might be hiding it from the bot."

    except Exception as e:
        return f"❌ Error on USA site: {str(e)[:50]}"

def main():
    # --- LISTA DE PRODUCTOS USA ---
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100", # Ejemplo USA
        # Añade aquí más links de nike.com (sin /es/ o /mx/)
    ]

    driver = iniciar_driver()
    for link in urls:
        resultado = obtener_precio_usa(driver, link)
        enviar_telegram(resultado)
        time.sleep(5)
    
    driver.quit()

if __name__ == "__main__":
    main()
