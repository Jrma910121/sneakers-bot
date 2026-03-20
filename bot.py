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
    chrome_options.add_argument("--headless=new") # Nueva versión de headless más indetectable
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # --- EVITAR DETECCIÓN ---
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent más "fresco"
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Inyectar script para eliminar rastro de WebDriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

def obtener_precio_nike(driver, url):
    try:
        # Entrar primero a la home de Nike para generar cookies "limpias"
        driver.get("https://www.nike.com")
        time.sleep(random.uniform(2, 4))
        
        # Ahora sí vamos al producto
        driver.get(url)
        
        # Espera larga: Nike a veces muestra una pantalla de carga blanca (intersticial)
        time.sleep(random.uniform(10, 15))
        
        # Scroll errático para parecer humano
        driver.execute_script(f"window.scrollTo(0, {random.randint(300, 700)});")
        time.sleep(2)

        # Intentar capturar el nombre y precio con un selector de texto genérico 
        # (Si Nike bloquea los IDs, buscamos por contenido)
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1, #pdp_product_title").text
        except:
            nombre = "Producto"

        precio = None
        # Intentamos buscar cualquier elemento que contenga el símbolo de moneda
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '€') or contains(text(), '$')]")
        
        for el in elementos:
            texto = el.text.strip()
            # Filtramos para que sea un número corto (un precio) y no un párrafo largo
            if 0 < len(texto) < 15 and any(char.isdigit() for char in texto):
                precio = texto
                break

        if precio:
            return f"✅ *{nombre}*\n💰 Precio: {precio}\n🔗 [Link]({url})"
        else:
            # Si sigue fallando, mandamos lo que el bot "ve" en el título de la pestaña
            titulo_pagina = driver.title
            return f"⚠️ *{nombre}*: Bloqueo detectado. (Título detectado: {titulo_pagina})"

    except Exception as e:
        return f"❌ Error técnico: {str(e)[:50]}"

def main():
    urls = [
        "https://www.nike.com/es/t/air-force-1-07-zapatillas-S9S7D8/CW2288-111"
    ]

    driver = iniciar_driver()
    for link in urls:
        resultado = obtener_precio_nike(driver, link)
        enviar_telegram(resultado)
        time.sleep(random.uniform(5, 10))
    
    driver.quit()

if __name__ == "__main__":
    main()
