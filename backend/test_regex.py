import re

urls = [
    "https://www.amazon.com.mx/Apple-15-pulgadas-Almacenamiento-Starlight-Reacondicionado/dp/B0CFT385DR/ref=sr_1_1?dib=...",
    "https://www.amazon.com.mx/EooCoo-Compatible-Pulgadas-Protector-Transparente/dp/B0D25DLFHV/ref=sr_1_2?dib=..."
]

for url in urls:
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    if match:
        print(f"ASIN: {match.group(1)} -> https://www.amazon.com.mx/dp/{match.group(1)}")
    else:
        print("No match:", url)
