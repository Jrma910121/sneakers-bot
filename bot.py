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
    # Evitar detección
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Camuflaje extra
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    return driver

def obtener_datos_nike(driver, url):
    try:
        driver.get(url)
        time.sleep(12) # Tiempo vital para que cargue el JavaScript de Nike
        
        # Simulación de scroll para cargar imágenes perezosas (lazy loading)
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        
        # 1. Nombre
        try:
            nombre = driver.find_element(By.CSS_SELECTOR, "h1#pdp_product_title, .pdp-6-up-title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. PRECIO (Búsqueda por patrón de texto)
        precio_final = "Consultar"
        precio_original = ""
        try:
            # Buscamos elementos que tengan el símbolo '$' y que estén cerca del título
            elementos_precio = driver.find_elements(By.XPATH, "//div[contains(@data-test, 'product-price')]//text()[contains(., '$')]/..")
            if not elementos_precio:
                elementos_precio = driver.find_elements(By.XPATH, "//*[contains(@class, 'price') and contains(text(), '$')]")

            nums = []
            for ep in elementos_precio:
                txt = ep.text.replace(',', '').strip()
                val = ''.join(c for c in txt if c.isdigit() or c == '.')
                if val and '.' in val: nums.append(float(val))
            
            nums = sorted(list(set(nums)), reverse=True)
            if len(nums) >= 2:
                precio_original = f"${nums[0]:.2f}"
                precio_final = f"${nums[-1]:.2f}"
            elif len(nums) == 1:
                precio_final = f"${nums[0]:.2f}"
        except:
            pass

        # 3. IMAGEN (Búsqueda por atributo de resolución)
        foto_url = None
        try:
            # Buscamos todas las imágenes y nos quedamos con la que parezca ser la principal (Hero)
            imgs = driver.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and "static.nike.com/a/images" in src and "t_PDP" in src:
                    # Forzamos HD modificando los parámetros de la URL
                    base = src.split("?")[0]
                    foto_url = f"{base}?wid=1200&fmt=jpeg&qlt=90"
                    break
        except:
            pass

        # 4. DESCUENTO OCULTO
        promo_extra = False
        try:
            cuerpo = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "extra" in cuerpo and any(x in cuerpo for x in ["cart", "checkout", "bag", "code"]):
                promo_extra = True
        except:
            pass

        # 5. Formato Mensaje
        p_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>" if precio_original else f"<b>{precio_final}</b>"
        aviso = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nRevisa en la web para ver el precio final." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {p_display}{aviso}\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error: {str(e)[:30]}", None

def main():
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100",
        "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007"
    ]
    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        time.sleep(random.uniform(5, 10))
    driver.quit()

if __name__ == "__main__":
    main()
    
