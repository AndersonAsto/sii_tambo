import requests
from bs4 import BeautifulSoup
import csv
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_categoria(url, nombre_csv="productos.csv"):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    productos = []

    # Recorremos los <a> donde suelen estar los productos
    for item in soup.select("a"):
        texto = item.get_text(strip=True)
        if "S/" in texto:  # solo entradas con precio
            match = re.match(r"(.+?)S/\s*([\d\.]+)(?:\s*S/\s*([\d\.]+))?(?:\s*-\s*(\d+)\s*%)?", texto)
            if match:
                nombre = match.group(1).strip()
                precio_nuevo = match.group(2)
                precio_antiguo = match.group(3) if match.group(3) else ""
                descuento = match.group(4) if match.group(4) else "0"
                productos.append([nombre, precio_antiguo, precio_nuevo, descuento])

    # Guardar en CSV
    with open(f"output/{nombre_csv}", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Producto", "Precio Antiguo", "Precio Nuevo", "Descuento %"])
        writer.writerows(productos)

    print(f"✅ {len(productos)} productos guardados en {nombre_csv}")


if __name__ == "__main__":
    url = "https://www.tambo.pe/pedir/categoria/EkyQ5huGfp9SAEQ4a"
    scrape_categoria(url, "promociones-mundo_diageo.csv")

    url2 = "https://www.tambo.pe/pedir/categoria/rov9kbCPb5Pn5njsh"
    scrape_categoria(url2, "zonas-zonas_gamer.csv")
    
    url3 = "https://www.tambo.pe/pedir/categoria/uY82hjhM8DEfQPbQq"
    scrape_categoria(url3, "zonas-zona_fit.csv")
    
    url4 = "https://www.tambo.pe/pedir/categoria/hfncXunKsxaak46S9"
    scrape_categoria(url4, "zonas-zona_family.csv")
    
    url5 = "https://www.tambo.pe/pedir/categoria/7JgNfTHdQP2WrqdaH"
    scrape_categoria(url5, "zonas-el_siguiente_a_1.csv")



