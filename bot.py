import requests
from bs4 import BeautifulSoup
import json
import re

# 🔑 CONFIGURA ESTO
TELEGRAM_TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"
CHAT_ID = "8751177346"

URLS = [
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
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/HF0015-002",
    "https://www.nike.com/t/p-6000-shoes-XkgpKW/CD6404-026",
    "https://www.nike.com/t/v5-rnr-mens-shoes-WHxi2GRN/II6292-004",
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
    "https://www.nike.com/t/zoom-vomero-5-mens-shoes-MgsTqZ/HF1553-006",
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

]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}


def obtener_precio(url):
    try:
        response = requests.get(url, headers=HEADERS)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # 🟢 1. Método directo
        precio_tag = soup.find("div", {"data-test": "product-price"})
        nombre_tag = soup.find("h1")

        nombre = nombre_tag.text.strip() if nombre_tag else "Producto"

        if precio_tag:
            precio_texto = precio_tag.text.strip()
            precio = float(re.sub(r"[^\d.]", "", precio_texto))
            return nombre, precio

        # 🟡 2. Buscar en scripts JSON (Nike usa esto)
        scripts = soup.find_all("script")

        for script in scripts:
            if script.string and "price" in script.string:
                matches = re.findall(r'"currentPrice":\s*([0-9.]+)', script.string)
                if matches:
                    return nombre, float(matches[0])

        # 🔴 3. No encontrado
        return nombre, None

    except Exception as e:
        print("ERROR:", e)
        return "Error", None


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }

    requests.post(url, data=data)


def main():
    print("🔄 Revisando precios...\n")

    encontrados = []

    for url in URLS:
        nombre, precio = obtener_precio(url)
        print(f"DEBUG → {nombre} | Precio: {precio}")

        if precio and precio <= 180:
            encontrados.append(f"{nombre} - ${precio}\n{url}")

    if encontrados:
        mensaje = "🔥 OFERTAS ENCONTRADAS 🔥\n\n" + "\n\n".join(encontrados)
        enviar_telegram(mensaje)
    else:
        print("❌ No hay ofertas menores a $100")


if __name__ == "__main__":
    main()
