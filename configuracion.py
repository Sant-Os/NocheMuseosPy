import math
import os
import json
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

ENTRADAS = {clave: 0.0 for clave in MUSEOS.keys()}

def calcular_distancia_directa(origen, destino):
    radio_tierra = 6371.0
    latitud_1 = math.radians(origen[0])
    longitud_1 = math.radians(origen[1])
    latitud_2 = math.radians(destino[0])
    longitud_2 = math.radians(destino[1])
    
    delta_latitud = latitud_2 - latitud_1
    delta_longitud = longitud_2 - longitud_1
    
    a = math.sin(delta_latitud / 2)**2 + math.cos(latitud_1) * math.cos(latitud_2) * math.sin(delta_longitud / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radio_tierra * c

ARCHIVO_PEATONAL = "cache_peatonal.json"
ARCHIVO_TAXI = "cache_taxi.json"

memoria_peaton = {}
memoria_taxi = {}

if os.path.exists(ARCHIVO_PEATONAL):
    try:
        with open(ARCHIVO_PEATONAL, "r", encoding="utf-8") as archivo:
            memoria_peaton = json.load(archivo)
    except Exception:
        pass

if os.path.exists(ARCHIVO_TAXI):
    try:
        with open(ARCHIVO_TAXI, "r", encoding="utf-8") as archivo:
            memoria_taxi = json.load(archivo)
    except Exception:
        pass

def guardar_memoria(perfil):
    try:
        if perfil == 'peaton':
            with open(ARCHIVO_PEATONAL, "w", encoding="utf-8") as archivo:
                json.dump(memoria_peaton, archivo, indent=4)
        else:
            with open(ARCHIVO_TAXI, "w", encoding="utf-8") as archivo:
                json.dump(memoria_taxi, archivo, indent=4)
    except Exception:
        pass

def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    if llave in memoria_activa:
        datos = memoria_activa[llave]
        return datos[0], datos[1], datos[2]
        
    longitud_1, latitud_1 = origen[1], origen[0]
    longitud_2, latitud_2 = destino[1], destino[0]
    
    if perfil == 'peaton':
        url_peaton = f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
        try:
            import time
            time.sleep(0.3)
            headers = {"User-Agent": "NocheMuseosSimulador/1.0"}
            respuesta = requests.get(url_peaton, headers=headers, timeout=5)
            datos = respuesta.json()
            if datos.get('code') == 'Ok':
                ruta_obtenida = datos['routes'][0]
                distancia_kilos = ruta_obtenida['distance'] / 1000.0
                tiempo_minutos = (distancia_kilos / 5.0) * 60.0
                puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
                memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
                guardar_memoria(perfil)
                return distancia_kilos, tiempo_minutos, puntos_ruta
        except Exception:
            pass
            
        puntos_ruta = [
            [origen[0], origen[1]],
            [origen[0], destino[1]],
            [destino[0], destino[1]]
        ]
        from geopy.distance import geodesic
        dist_1 = geodesic(origen, (origen[0], destino[1])).km
        dist_2 = geodesic((origen[0], destino[1]), destino).km
        distancia_kilos = dist_1 + dist_2
        tiempo_minutos = (distancia_kilos / 5.0) * 60.0
        
        memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
        guardar_memoria(perfil)
        return distancia_kilos, tiempo_minutos, puntos_ruta
        
    url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
    
    try:
        import time
        time.sleep(0.3)
        headers = {"User-Agent": "NocheMuseosSimulador/1.0"}
        respuesta = requests.get(url, headers=headers, timeout=5)
        datos = respuesta.json()
        if datos.get('code') == 'Ok':
            ruta_obtenida = datos['routes'][0]
            distancia_kilos = ruta_obtenida['distance'] / 1000.0
            tiempo_minutos = ruta_obtenida['duration'] / 60.0
            puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
            memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
            guardar_memoria(perfil)
            return distancia_kilos, tiempo_minutos, puntos_ruta
    except Exception:
        pass
        
    memoria_activa[llave] = [None, None, None]
    guardar_memoria(perfil)
    return None, None, None

LINEAS_TRUFIS = {}

def cargar_rutas_trufis():
    global LINEAS_TRUFIS
    archivo_rutas = "rutas_trufis.geojson"
    if not os.path.exists(archivo_rutas):
        return {}
        
    try:
        with open(archivo_rutas, "r", encoding="utf-8") as archivo:
            datos_trufis = json.load(archivo)
    except Exception:
        return {}
        
    diccionario_lineas = {}
    for elemento in datos_trufis.get("features", []):
        propiedades = elemento.get("properties", {})
        tipo_transporte = propiedades.get("tipo_linea", "TRUFI")
        nombre_linea = propiedades.get("linea", "Desconocida")
        identificador = f"{tipo_transporte} {nombre_linea}"
        
        geometria = elemento.get("geometry", {})
        if geometria.get("type") == "LineString":
            if identificador not in diccionario_lineas:
                diccionario_lineas[identificador] = []
            coordenadas_invertidas = [[coordenada[1], coordenada[0]] for coordenada in geometria.get("coordinates", [])]
            diccionario_lineas[identificador].extend(coordenadas_invertidas)
            
    LINEAS_TRUFIS = diccionario_lineas
    nodos_ciudad = {"Origen": (-17.391, -66.248)}
    nodos_ciudad.update(MUSEOS)
    
    matriz_transportes = {nodo_a: {nodo_b: {'costo_pasaje': float('inf'), 'lineas_disponibles': []} for nodo_b in nodos_ciudad} for nodo_a in nodos_ciudad}
    
    paradas_cercanas = {nodo: set() for nodo in nodos_ciudad}
    for nombre_nodo, coordenada_nodo in nodos_ciudad.items():
        for identificador_linea, ruta_linea in diccionario_lineas.items():
            for punto_ruta in ruta_linea:
                distancia_a_calle = calcular_distancia_directa(coordenada_nodo, punto_ruta)
                if distancia_a_calle < 0.4:
                    paradas_cercanas[nombre_nodo].add(identificador_linea)
                    break
                    
    for nodo_origen in nodos_ciudad:
        for nodo_destino in nodos_ciudad:
            if nodo_origen == nodo_destino:
                continue
            lineas_en_comun = paradas_cercanas[nodo_origen].intersection(paradas_cercanas[nodo_destino])
            if lineas_en_comun:
                matriz_transportes[nodo_origen][nodo_destino] = {'costo_pasaje': 3.0, 'lineas_disponibles': list(lineas_en_comun)}
            elif paradas_cercanas[nodo_origen] and paradas_cercanas[nodo_destino]:
                matriz_transportes[nodo_origen][nodo_destino] = {'costo_pasaje': 6.0, 'lineas_disponibles': [list(paradas_cercanas[nodo_origen])[0], list(paradas_cercanas[nodo_destino])[0]]}
                    
    return matriz_transportes

MATRIZ_TRANSPORTE = cargar_rutas_trufis()
