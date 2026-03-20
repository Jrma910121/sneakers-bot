import os
import time
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
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def obtener_precio_nike(driver, url):
    """Lógica para extraer el precio de una sola URL."""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Esperar a que el título cargue
        nombre = wait.until(EC.presence_of_element_located((By.ID, "pdp_product_title"))).text
        
        # Pausa para asegurar que los scripts de precio carguen
        time.sleep(3) 
        
        precio = None
        for selector in ['[data-test="product-price"]', '[data-test="product-price-reduced"]', '.product-price']:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, selector)
                if elemento.text:
                    precio = elemento.text
                    break
            except:
                continue
        
        if precio:
            return f"👟 *{nombre}*\n💰 Precio: {precio}\n🔗 [Link]({url})"
        else:
            return f"⚠️ *{nombre}*: No se pudo leer el precio."
            
    except Exception as e:
        return f"❌ Error en link: {url[:30]}... \nDetalle: {str(e)[:50]}"

def main():
    # --- LISTA DE PRODUCTOS ---
    urls = [
        "https://www.nike.com/es/t/air-force-1-07-zapatillas-S9S7D8/CW2288-111",
        "https://www.nike.com/es/t/ Dunk-Low-Retro-zapatillas-S9S7D8/DD1391-100",
        # Añade aquí todas las URLs que quieras, separadas por coma
    ]
    # --------------------------

    driver = iniciar_driver()
    enviar_telegram(f"🚀 *Iniciando monitoreo de {len(urls)} productos...*")
    
    for link in urls:
        resultado = obtener_precio_nike(driver, link)
        enviar_telegram(resultado)
        time.sleep(2) # Pausa entre productos para evitar bloqueos
        
    driver.quit()

if __name__ == "__main__":
    main()
