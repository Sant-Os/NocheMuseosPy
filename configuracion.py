import math
import requests
import polyline


MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    '[D] Museo Arqueológico UMSS': (-17.395278, -66.157394),
    '[E] Iglesia de la Compañía de Jesús': (-17.393023, -66.157814),
    '[F] Casa Departamental de Culturas': (-17.393081, -66.157084),
    '[G] Salón de Exposiciones Gíldaro Antezana': (-17.393008, -66.156494),
    '[H] Casona de la UNITEPC': (-17.392542, -66.156150),
    '[I] Salón de Exposiciones ABAP-CBBA': (-17.392294, -66.156730),
    '[J] Salón de Exposiciones Mario Unzueta': (-17.391564, -66.155680),
    '[K] Museo Francisco de Viedma': (-17.387265, -66.150514),
    '[L] Museo Alcides d\'Orbigny': (-17.373723, -66.153692),
    '[M] Palacio Portales (Fundación Simón I. Patiño)': (-17.374561, -66.153052),
    '[N] Casona de Mayorazgo': (-17.365018, -66.174732),
    '[O] Centro Cultural Juan Wallparrimachi': (-17.388766, -66.187239),
    '[P] Proyecto mARTadero': (-17.400032, -66.165723),
    '[Q] Casa del Arquitecto': (-17.396950, -66.159329),
    '[R] Casona del Banco Solidario': (-17.397657, -66.155581),
    '[S] Museo Esteban Arze': (-17.396419, -66.172168),
    '[T] Museo de la Reserva Moral y Estratégica': (-17.398620, -66.156797),
    '[U] Museo Mariscal Andrés de Santa Cruz': (-17.397133, -66.160901),
    '[V] Museo de Arte Chinchiri': (-17.385307, -66.262618),
    '[W] Museo de la Escuela de Armas Mcal. José Ballivián': (-17.378998, -66.143439)
}
ENTRADAS = {k: 0.0 for k in MUSEOS.keys()}

def calcular_distancia_haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

import os
import json

CACHE_FILE = "cache_rutas.json"
cache_rutas = {}

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_rutas = json.load(f)
    except Exception as e:
        print(f"Error cargando caché: {e}")

def guardar_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_rutas, f, indent=4)
    except Exception as e:
        print(f"Error guardando caché: {e}")

def obtener_ruta_osrm(coord_origen, coord_destino, modo):
    cache_key = f"{coord_origen[0]},{coord_origen[1]}|{coord_destino[0]},{coord_destino[1]}|{modo}"
    if cache_key in cache_rutas:
        c = cache_rutas[cache_key]
        if c[0] is None:
            return None, None, None
        return c[0], c[1], c[2]
    lon1, lat1 = coord_origen[1], coord_origen[0]
    lon2, lat2 = coord_destino[1], coord_destino[0]
    if modo == 'foot':
        url_base = "https://routing.openstreetmap.de/routed-foot/route/v1/driving"
    else:
        url_base = "https://routing.openstreetmap.de/routed-car/route/v1/driving"
    url = f"{url_base}/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=polyline"
    try:
        r = requests.get(url, timeout=5)
        datos = r.json()
        if datos.get('code') == 'Ok':
            ruta_osrm = datos['routes'][0]
            distancia_km = ruta_osrm['distance'] / 1000.0
            tiempo_min = ruta_osrm['duration'] / 60.0
            geometria = polyline.decode(ruta_osrm['geometry'])
            cache_rutas[cache_key] = [distancia_km, tiempo_min, geometria]
            guardar_cache()
            return distancia_km, tiempo_min, geometria
    except Exception as e:
        print(f"Error OSRM: {e}")
    cache_rutas[cache_key] = [None, None, None]
    guardar_cache()
    return None, None, None
