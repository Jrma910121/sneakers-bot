import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Oculta que es Selenium
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent muy específico de una versión actual de Windows
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Cambiar la propiedad webdriver a undefined para engañar a Nike
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def obtener_precio_nike(driver, url):
    try:
        driver.get(url)
        # Espera aleatoria para simular carga humana
        time.sleep(random.uniform(5.5, 8.5))
        
        # Hacer un pequeño scroll hacia abajo
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(2)

        # Intentar obtener el nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Producto Nike"

        # Búsqueda agresiva de precio
        precio = None
        # Selectores en orden de prioridad
        selectores = [
            'span[data-test="product-price"]',
            'div[data-test="product-price-reduced"]',
            '.product-price',
            '.is--current-price',
            '[data-test="product-price-actual"]'
        ]

        for selector in selectores:
            try:
                elementos = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elementos:
                    if el.text and ("€" in el.text or "$" in el.text):
                        precio = el.text
                        break
                if precio: break
            except:
                continue

        if precio:
            return f"✅ *{nombre}*\n💰 Precio: {precio}\n🔗 [Link]({url})"
        else:
            # Si falla, tomamos una captura de consola para debug (opcional)
            print(f"Fallo en {nombre}. HTML parcial: {driver.page_source[:500]}")
            return f"⚠️ *{nombre}*: No se detectó precio. Nike bloqueó el script."

    except Exception as e:
        return f"❌ Error en: {url[:40]}... \n{str(e)[:50]}"

def main():
    urls = [
        "https://www.nike.com/es/t/air-force-1-07-zapatillas-S9S7D8/CW2288-111",
        # Agrega más aquí
    ]

    driver = iniciar_driver()
    for link in urls:
        resultado = obtener_precio_nike(driver, link)
        enviar_telegram(resultado)
        time.sleep(random.uniform(3, 6)) # Pausa entre productos
    
    driver.quit()

if __name__ == "__main__":
    main()
