import os
import time
import random
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def enviar_notificacion(mensaje, foto_url=None):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    url_api = f"https://api.telegram.org/bot{token}/sendPhoto" if foto_url else f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "parse_mode": "HTML"}
    
    if foto_url:
        payload["photo"] = foto_url
        payload["caption"] = mensaje
    else:
        payload["text"] = mensaje

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
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        
        # ESPERA ACTIVA: Esperar hasta 20 segundos a que aparezca cualquier texto con "$"
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '$')]"))
            )
        except:
            pass # Si no aparece en 20s, intentamos extraer lo que haya
            
        time.sleep(5) # Tiempo extra para renderizado final

        # 1. Nombre
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. PRECIO (Búsqueda por coordenadas visuales para evitar errores)
        precio_final = "Consultar"
        precio_original = ""
        
        try:
            # Capturamos el texto de la parte superior derecha (donde Nike pone el precio)
            # Esto evita capturar precios de productos recomendados de abajo
            cuerpo_texto = driver.execute_script("return document.body.innerText")
            # Cortamos el texto para quedarnos solo con los primeros 3000 caracteres (zona del producto)
            zona_producto = cuerpo_texto[:3000]
            
            # Buscamos todos los precios en esa zona
            encontrados = re.findall(r'\$\s?(\d+(?:\.\d{2})?)', zona_producto)
            # Limpiar y convertir a números
            precios_num = sorted(list(set([float(p) for p in encontrados])), reverse=True)
            
            # Filtrar precios lógicos (zapatillas entre $25 y $4
