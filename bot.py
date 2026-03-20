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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(10)
        
        # Scroll para asegurar carga de datos reales
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. DETECCIÓN DE PRECIOS REALES (MÉTODO PRIORITARIO)
        precio_final = "Ver en web"
        precio_original = ""
        
        try:
            # Buscamos el contenedor específico de precios del producto (evita recomendaciones)
            contenedor_precio = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price-container"], .product-price, .is--current-price')
            
            # Buscamos todos los precios dentro de ese contenedor específico
            tags_precio = contenedor_precio.find_elements(By.XPATH, ".//*[contains(text(), '$')]")
            precios_reales = []
            
            for p in tags_precio:
                texto = p.text.replace('\n', '').strip()
                if "$" in texto:
                    # Limpiar el texto para dejar solo el número
                    val = ''.join(c for c in texto if c.isdigit() or c == '.')
                    if val: precios_reales.append(float(val))
            
            precios_reales = sorted(list(set(precios_reales)), reverse=True)
            
            if len(precios_reales) >= 2:
                precio_original = f"${precios_reales[0]:.2f}"
                precio_final = f"${precios_reales[-1]:.2f}"
            elif len(precios_reales) == 1:
                precio_final = f"${precios_reales[0]:.2f}"
        except:
            precio_final = "Consultar"

        # 3. DETECCIÓN DE DESCUENTO OCULTO (MÉTODO AGRESIVO)
        promo_extra = False
        try:
            # Escanea banners de mensajería y el código fuente para "Extra Off"
            full_html = driver.page_source.lower()
            keywords = ["extra 20%", "extra 25%", "extra 10%", "off in cart", "off at checkout", "code"]
            
            banners = driver.find_elements(By.CSS_SELECTOR
