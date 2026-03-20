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
        
        # Espera activa para carga de elementos de precio
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//span[@data-testid='currentPrice-container']"))
            )
        except:
            pass
            
        time.sleep(5) 

        # 1. Nombre del Producto
        try:
            nombre = driver.find_element(By.ID, "pdp_product_title").text
        except:
            nombre = "Zapatilla Nike"

        # 2. Extracción de Precios usando selector específico de Nike
        precio_final = "Consultar"
        precio_original = ""
        
        try:
            # Usa el selector específico que encontramos en el HTML
            precio_element = driver.find_element(By.XPATH, "//span[@data-testid='currentPrice-container']")
            precio_text = precio_element.text.strip()
            
            # Extrae el número del precio (ej: "$115" -> "115")
            precio_match = re.search(r'\$\s?(\d+(?:\.\d{2})?)', precio_text)
            
            if precio_match:
                precio_final = f"${precio_match.group(1)}"
            else:
                precio_final = "Ver en Web"
                
        except Exception as e:
            print(f"Error extrayendo precio con selector primario: {e}")
            # Fallback a método anterior si falla
            try:
                cuerpo_texto = driver.execute_script("return document.body.innerText")
                zona_producto = cuerpo_texto[:5000]
                encontrados = re.findall(r'\$\s?(\d+(?:\.\d{2})?)', zona_producto)
                
                if encontrados:
                    precios_num = sorted(list(set([float(p) for p in encontrados])), reverse=True)
                    precios_logicos = [p for p in precios_num if 20 <= p <= 500]
                    
                    if len(precios_logicos) >= 1:
                        precio_final = f"${precios_logicos[-1]:.2f}"
                    else:
                        precio_final = "Ver en Web"
                else:
                    precio_final = "Ver en Web"
            except:
                precio_final = "Ver en Web"

        # 3. Imagen en Alta Resolución
        foto_url = None
        try:
            img = driver.find_element(By.XPATH, "//img[contains(@src, 'static.nike.com/a/images') and not(contains(@src, 'width=64'))]")
            src = img.get_attribute("src")
            if src:
                foto_url = src.split('?')[0] + "?wid=1500&fmt=jpeg&qlt=90"
        except:
            pass

        # 4. Detección de Promo Extra en Carrito
        promo_extra = False
        try:
            cuerpo_texto = driver.execute_script("return document.body.innerText")
            zona_producto = cuerpo_texto[:8000]
            
            if any(x in zona_producto.lower() for x in ["extra savings in bag", "extra off", "descuento en carrito", "carrito adicional"]):
                if any(y in zona_producto.lower() for y in ["off", "savings", "discount"]):
                    promo_extra = True
        except:
            pass

        # 5. Construcción del Mensaje
        if precio_original and precio_original != precio_final:
            p_display = f"<s>{precio_original}</s> 🔥 <b>{precio_final}</b>"
        else:
            p_display = f"<b>{precio_final}</b>"
            
        aviso_promo = "\n\n🎁 <b>¡DESCUENTO EXTRA EN CARRITO!</b>\nEste modelo tiene rebaja adicional al pagar." if promo_extra else ""

        mensaje = (
            f"🇺🇸 <b>ALERTA NIKE USA</b>\n\n"
            f"👟 <b>Producto:</b> {nombre}\n"
            f"💰 <b>Precio:</b> {p_display}\n"
            f"{aviso_promo}\n"
            f"--------------------------------\n"
            f"📌 <i>Nota: Precios antes de taxes (impuestos). El valor final varía según el estado de entrega en USA.</i>\n\n"
            f"📦 <b>Envío a Colombia:</b> Requiere el uso de casillero virtual para el transporte internacional.\n\n"
            f'🔗 <a href="{url}">Ver en la Tienda</a>'
        )
        return mensaje, foto_url

    except Exception as e:
        return f"❌ Error de carga: {str(e)[:30]}", None

def main():
    urls = [
        "https://www.nike.com/t/air-force-1-07-mens-shoes-jBrhbr/CT2302-100",
        "https://www.nike.com/t/air-max-excee-mens-shoes-vl97pm/FZ5486-007"
    ]
    driver = iniciar_driver()
    for link in urls:
        mensaje, foto = obtener_datos_nike(driver, link)
        enviar_notificacion(mensaje, foto)
        time.sleep(random.uniform(5, 8))
    driver.quit()

if __name__ == "__main__":
    main()
