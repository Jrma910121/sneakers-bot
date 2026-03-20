import requests
from bs4 import BeautifulSoup
import json
import os

# 🔐 SEGURIDAD: variables desde GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

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
"https://www.nike.com/t/air-max-95-g-golf-shoes-pqM06obj/HV4696-002"
]

# 📩 Enviar foto + mensaje
def enviar_telegram(nombre, precio, decision, url_producto, imagen):
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    mensaje = f"""
👟 *{nombre}*

💰 Precio: ${precio}

{decision}

👉 Comprar aquí:
{url_producto}
"""

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": imagen,
        "caption": mensaje,
        "parse_mode": "Markdown"
    }

    requests.post(api_url, json=payload)


# 🧠 Lógica de decisión
def evaluar_precio(precio):
    if precio < 90:
        return "🔥 *¡CÓMPRALAS YA!* Este precio está regalado 💸"
    elif 90 <= precio <= 110:
        return "😏 *Buen precio*… si te gustan, no lo pienses mucho 👀"
    else:
        return "⏳ *Precio alto*… mejor espera que bajen 💤"


# 🔎 Scraping Nike (JSON interno)
def obtener_datos(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        script = soup.find("script", {"id": "__NEXT_DATA__"})
        if not script:
            return None, None, None

        data = json.loads(script.string)

        product = data["props"]["pageProps"]["initialState"]["Threads"]["products"]

        for key in product:
            info = product[key]

            nombre = info.get("title")
            precio = info.get("price", {}).get("currentPrice")

            imagen = None
            if "images" in info and len(info["images"]) > 0:
                imagen = info["images"][0].get("url")

            return nombre, precio, imagen

    except Exception as e:
        print("Error:", e)
        return None, None, None


def main():
    # 🚫 Validación de seguridad
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERROR: Faltan variables de entorno (Secrets)")
        return

    print("🔄 Revisando precios...\n")

    for url in URLS:
        nombre, precio, imagen = obtener_datos(url)

        print(f"DEBUG → {nombre} | Precio: {precio}")

        if precio and imagen:
            decision = evaluar_precio(precio)
            enviar_telegram(nombre, precio, decision, url, imagen)


if __name__ == "__main__":
    main()
