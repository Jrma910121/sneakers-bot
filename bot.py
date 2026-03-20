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

    try:
        requests.post(url_api, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

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
        
        # Espera activa para que el símbolo $ aparezca en pantalla
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '$')]"))
            )
        except:
            pass
            
        time.sleep(5) 

        # 1. Nombre del Producto
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. Extracción de Precios (Lógica de zona superior)
        precio_final = "Consultar"
        precio_original = ""
        
        try:
            cuerpo_texto = driver.execute_script("return document.body.innerText")
            # Analizamos solo la parte superior para evitar precios de sugerencias
            zona_producto = cuerpo_texto[:3500]
            
            # Buscamos patrones de precio
            encontrados = re.findall(r'\$\s
