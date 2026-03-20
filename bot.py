import requests

# ---------------------------
# Configuración Telegram
# ---------------------------
TELEGRAM_TOKEN = "8759569270:AAExdcBmlmU-KrOo_80AZN_agXboIxU8k50"
TELEGRAM_CHAT_ID = "8751177346"

# ---------------------------
# Lista de URLs de productos
# ---------------------------
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
]

# ---------------------------
# Funciones
# ---------------------------
def obtener_info_producto(url):
    try:
        # Extrae el SKU (última parte de la URL)
        sku = url.rstrip("/").split("/")[-1]

        # Endpoint de Nike para obtener info del producto
        api_url = f"https://api.nike.com/product_feed/threads/v2/?filter=marketplace({sku})"
        headers = {"User-Agent": "Mozilla/5.0"}  # simula un navegador
        r = requests.get(api_url, headers=headers)
        data = r.json()

        # El JSON tiene la info en "objects"
        if "objects" in data and len(data["objects"]) > 0:
            prod = data["objects"][0]

            nombre = prod.get("title", "Producto Nike")
            precio = None
            if "price" in prod:
                precio = float(prod["price"]["current"]["raw"])
            foto_url = None
            if "imageUrls" in prod and len(prod["imageUrls"].get("productImage", [])) > 0:
                foto_url = prod["imageUrls"]["productImage"][0]

            return nombre, precio, foto_url

        return "Producto Nike", None, None

    except Exception as e:
        print("Error:", e)
        return None, None, None

def mensaje_motivacional(precio):
    if precio is None:
        return "❓ Precio no disponible, revisa más tarde."
    elif precio < 90:
        return "🔥 ¡Excelente precio! ¡Es hora de comprar!"
    elif 90 <= precio <= 110:
        return "💡 Buen precio, tu decides si aprovecharlo."
    else:
        return "⚠️ Precio alto, tal vez espera un poco."

def enviar_telegram(foto, mensaje, url):
    text = f"{mensaje}\n\nCompra aquí: {url}"
    if foto:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            params={"chat_id": TELEGRAM_CHAT_ID, "photo": foto, "caption": text},
        )
    else:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            params={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        )

def main():
    for url in URLS:
        nombre, precio, foto = obtener_info_producto(url)
        print(f"DEBUG → {nombre} | Precio: {precio}")
        mensaje = mensaje_motivacional(precio)
        enviar_telegram(foto, f"{nombre}\n{mensaje}", url)

if __name__ == "__main__":
    main()
