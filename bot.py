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
    "https://www.nike.com/launch/t/air-max-90-anthracite-and-neon-yellow",
    "https://www.nike.com/t/air-max-plus-vii-mens-shoes-Qir8hMAo/HQ2197-800",
    "https://www.nike.com/t/air-max-95-big-bubble-womens-shoes-C8qkmu3G/HJ5996-003",
    "https://www.nike.com/t/air-max-plus-g-golf-shoes-etVKhXd4/FZ4150-001",
    "https://www.nike.com/t/air-max-dn8-leather-mens-shoes-GbnAW5Hb/IB6381-002",
    "https://www.nike.com/t/sb-air-max-95-skate-shoes-p6pzgr/HF7545-002",
    "https://www.nike.com/t/air-vapormax-plus-mens-shoes-nC0dzF/CK0900-001",
    "https://www.nike.com/t/air-max-95-g-golf-shoes-pqM06obj/HV4696-002"
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

        if precio and precio < 100:
            encontrados.append(f"{nombre} - ${precio}\n{url}")

    if encontrados:
        mensaje = "🔥 OFERTAS ENCONTRADAS 🔥\n\n" + "\n\n".join(encontrados)
        enviar_telegram(mensaje)
    else:
        print("❌ No hay ofertas menores a $100")


if __name__ == "__main__":
    main()
