import urllib.request
import os

def descargar_rutas():
    archivo = "rutas_trufis.geojson"
    if not os.path.exists(archivo):
        print("Descargando rutas_trufis.geojson (aprox 2.2MB)...")
        url = "https://gist.githubusercontent.com/mauforonda/b094e77a0af814dba978f6ae564faa78/raw"
        urllib.request.urlretrieve(url, archivo)
        print("¡Descarga completada!")
    else:
        print("El archivo ya existe.")

if __name__ == "__main__":
    descargar_rutas()
