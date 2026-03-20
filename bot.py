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
    try:
        driver.get(url)
        # Esperamos un poco más para que cargue el JS dinámico
        time.sleep(7) 
        
        # Intentar obtener el nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Producto Nike"

        # --- ESTRATEGIA DE BÚSQUEDA MÚLTIPLE ---
        precio = None
        
        # 1. Intentar por Atributos de Test (Lo más estable)
        for data_test in ["product-price", "product-price-reduced", "v1-item-price"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, f'[data-test="{data_test}"]')
                if el.text:
                    precio = el.text
                    break
            except:
                continue

        # 2. Si falla, intentar por clases comunes (CSS)
        if not precio:
            for clase in [".product-price", ".is--current-price", ".headline-5"]:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, clase)
                    if "€" in el.text or "$" in el.text or "S/" in el.text: # Verifica si tiene símbolo de moneda
                        precio = el.text
                        break
                except:
                    continue

        # 3. Si sigue fallando, buscar cualquier texto que parezca un precio en el contenedor principal
        if not precio:
            try:
                # Busca dentro del contenedor de detalles del producto
                contenedor = driver.find_element(By.CLASS_NAME, "product-profile-info")
                if "€" in contenedor.text: # Ajusta el símbolo según tu país
                    # Esto es un último recurso, puede traer texto extra
                    precio = "Revisar link (bloqueo parcial)"
            except:
                pass

        if precio:
            return f"👟 *{nombre}*\n💰 Precio: {precio}\n🔗 [Link]({url})"
        else:
            return f"⚠️ *{nombre}*: No se pudo leer el precio (Posible bloqueo anti-bot)."
            
    except Exception as e:
        return f"❌ Error en la página: {nombre if 'nombre' in locals() else 'Desconocido'}"

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
