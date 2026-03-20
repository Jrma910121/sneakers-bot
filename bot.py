import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

# -----------------------------
# CONFIGURACIÓN DE TELEGRAM
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(nombre, precio, url, img_url):
    if precio is None:
        mensaje = f"❌ No se pudo obtener el precio de {nombre}\nLink: {url}"
    else:
        # Evaluar precio
        if precio < 90:
            recomendacion = "🎉 ¡Compra! Tiene un precio increíble 😎"
        elif 90 <= precio <= 110:
            recomendacion = "💡 Buen precio, tú decides"
        else:
            recomendacion = "⏳ Precio alto, quizá esperar"

        mensaje = f"{recomendacion}\nNombre: {nombre}\nPrecio: ${precio}\nLink: {url}"

    # Enviar foto + mensaje
    data = {
        "chat_id": CHAT_ID,
        "caption": mensaje,
        "photo": img_url
    }
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=data)


# -----------------------------
# LISTA DE URLS
# -----------------------------
URLS = [
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
# ... agrega todas las demás URLs aquí ...
]

# -----------------------------
# CONFIGURAR SELENIUM HEADLESS
# -----------------------------
options = Options()
options.headless = True
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# -----------------------------
# SCRAPING Y ENVÍO TELEGRAM
# -----------------------------
for url in URLS:
    try:
        driver.get(url)
        time.sleep(3)  # dar tiempo a que cargue JS

        # Nombre del producto
        nombre = driver.find_element(By.CSS_SELECTOR, "h1[data-test='product-title']").text

        # Precio
        try:
            precio_text = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']").text
            precio = float(precio_text.replace("$","").replace(",",""))
        except:
            precio = None

        # Imagen principal
        try:
            img_url = driver.find_element(By.CSS_SELECTOR, "img[data-test='product-image']").get_attribute("src")
        except:
            img_url = None

        print(f"DEBUG → {nombre} | Precio: {precio}")
        enviar_telegram(nombre, precio, url, img_url)

    except Exception as e:
        print(f"Error procesando {url}: {e}")

driver.quit()
