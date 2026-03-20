# bot.py
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- Configuración de Telegram ----------
TELEGRAM_TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"
TELEGRAM_CHAT_ID = "8751177346"
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise Exception("❌ Faltan variables de entorno (Secrets): TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")

# ---------- Lista de URLs a monitorear ----------
PRODUCT_URLS = [
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/BV1358-003",
    "https://www.nike.com/t/air-max-plus-mens-shoes-x9G2xF/IF4390-001",
    "https://www.nike.com/t/air-max-plus-mens-shoes-x9G2xF/604133-050",
    "https://www.nike.com/t/air-max-90-mens-shoes-bAZ6AeHT/IQ0300-001",
    "https://www.nike.com/t/air-max-90-mens-shoes-bAZ6AeHT/CN8490-002",
    "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-006",
    "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FN7304-001",
    "https://www.nike.com/t/air-vapormax-plus-mens-shoes-nC0dzF/924453-004",
    "https://www.nike.com/t/air-max-torch-4-mens-shoes-AKTdGZxX/343846-002",
    "https://www.nike.com/t/zoom-vomero-5-se-sp-mens-shoes-MgsTqZ/CI1694-001",
    "https://www.nike.com/t/zoom-vomero-5-se-sp-mens-shoes-MgsTqZ/BV1358-003",
    "https://www.nike.com/t/zoom-vomero-5-se-sp-mens-shoes-MgsTqZ/FJ4151-007",
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/CN0149-001",
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/HF0015-002",
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/CD6404-026",
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/CD6404-028",
    "https://www.nike.com/u/custom-nike-air-max-plus-by-you-10001901/4088545884",
    "https://www.nike.com/t/air-max-plus-mens-shoes-x9G2xF/DM0032-030",
    "https://www.nike.com/t/air-max-dn8-se-mens-shoes-YPsmAOxu/HV4525-001",
    "https://www.nike.com/t/air-max-dn8-se-mens-shoes-YPsmAOxu/FQ7860-002",
    "https://www.nike.com/t/air-force-1-gore-tex-vibram-mens-shoes-ASaVZlAr/HV5953-100",
    "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100",
    "https://www.nike.com/t/nocta-air-force-1-low-mens-shoes-8T0Pt0/CZ8065-101",
    "https://www.nike.com/t/dunk-low-gore-tex-mens-shoes-hbKMFmET/HQ2053-001",
    "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007",
    "https://www.nike.com/t/air-max-moto-2k-mens-shoes-sHpe9Gv4/IQ4924-003",
    "https://www.nike.com/t/air-max-90-mens-shoes-bAZ6AeHT/DM0029-019",
    "https://www.nike.com/t/air-max-dn8-mens-shoes-YPsmAOxu/IM7405-700",
    "https://www.nike.com/t/air-max-95-big-bubble-mens-shoes-with-reflective-accents-2xNsHz6W/IB1667-003",
    "https://www.nike.com/t/air-max-plus-mens-shoes-x9G2xF/DM0032-105",
    "https://www.nike.com/t/air-max-plus-vii-mens-shoes-Qir8hMAo/HQ2197-800",
    "https://www.nike.com/t/air-max-95-big-bubble-womens-shoes-C8qkmu3G/HJ5996-003",
    "https://www.nike.com/t/air-max-plus-g-golf-shoes-etVKhXd4/FZ4150-001",
    "https://www.nike.com/t/air-max-dn8-leather-mens-shoes-GbnAW5Hb/IB6381-002",
    "https://www.nike.com/t/sb-air-max-95-skate-shoes-p6pzgr/HF7545-002",
    "https://www.nike.com/t/air-vapormax-plus-mens-shoes-nC0dzF/CK0900-001",
    "https://www.nike.com/t/air-max-95-g-golf-shoes-pqM06obj/HV4696-002",
    # ... agrega todas tus URLs aquí ...
]

# ---------- Funciones ----------
def enviar_telegram(texto, foto_url=None):
    """Envía un mensaje a Telegram con imagen opcional"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto" if foto_url else f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": texto} if foto_url else {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    if foto_url:
        data["photo"] = foto_url
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"❌ Error enviando Telegram: {response.text}")

def mensaje_motivador(precio):
    """Genera el mensaje motivador según tu lógica"""
    if precio < 90:
        return "🔥 ¡Este es un excelente precio! ¡Compra ahora antes de que suba! 🔥"
    elif 90 <= precio <= 110:
        return "🙂 Buen precio, depende de ti decidir si comprar ahora."
    else:
        return "💸 El precio está alto, quizá convenga esperar a que baje."

def obtener_info_producto(url):
    """Extrae el nombre, precio y foto de un producto usando Selenium"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)  # Selenium Manager detecta el driver automáticamente

    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
        nombre = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-1'))).text
        precio_text = driver.find_element(By.CSS_SELECTOR, 'div.product-price > div > span').text
        precio = float(precio_text.replace("$","").replace(",",""))
        foto_url = driver.find_element(By.CSS_SELECTOR, 'picture img').get_attribute("src")
    except Exception as e:
        print(f"❌ Error obteniendo datos de {url}: {e}")
        nombre, precio, foto_url = None, None, None
    driver.quit()
    return nombre, precio, foto_url

# ---------- Main ----------
def main():
    for url in PRODUCT_URLS:
        nombre, precio, foto_url = obtener_info_producto(url)
        if nombre and precio:
            print(f"DEBUG → {nombre} | Precio: {precio}")
            texto = f"👟 {nombre}\n{mensaje_motivador(precio)}\n🛒 Comprar aquí: {url}"
            enviar_telegram(texto, foto_url=foto_url)
        else:
            print(f"DEBUG → {nombre} | Precio: {precio}")

if __name__ == "__main__":
    main()
