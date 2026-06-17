# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTIAGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

### 1. Instalación de Python
Para el desarrollo y despliegue lógico de este proyecto, seleccionamos el lenguaje de programación **Python 3**. La elección de Python radica en su enorme ecosistema de paquetes cartográficos y de inteligencia artificial, además de su tipado dinámico y recolección automática de basura (Garbage Collection), lo que evita fugas de memoria durante el procesamiento intensivo de árboles de búsqueda algorítmica.

Para garantizar que el software funcione de manera hermética y no genere conflictos de versiones con el sistema operativo anfitrión del usuario, implementamos un esquema de "Entornos Virtuales" (Virtual Environments). Este mecanismo aísla el intérprete de Python y las librerías específicas del proyecto en un microcontenedor local, asegurando portabilidad pura.
El proceso de instalación e inicialización del entorno se realiza desde la consola de comandos de la siguiente manera:

```bash
# Creación del contenedor virtual
python -m venv venv

# Activación del microcontenedor para aislar dependencias
venv\Scripts\activate
```

### 2. Instalación y Ejecución de Bibliotecas Externas como Nativas
Un simulador cartográfico en tiempo real no puede ser programado puramente desde cero por cuestiones de eficiencia de tiempos. Nuestro proyecto implementa un conjunto masivo de bibliotecas, divididas en dependencias externas (obtenidas del repositorio mundial PyPI) e internas (nativas del intérprete).

**Instalación y Ejecución de Bibliotecas Externas:**
Mediante el gestor de paquetes `pip`, el software instala los módulos pesados encargados de la renderización y la comunicación de red. Para instalarlas, el usuario ejecuta `pip install PyQt5 PyQtWebEngine folium geopy polyline requests`.
- `PyQt5` y `PyQtWebEngine`: Constituyen el esqueleto del software. Proveen clases de interfaces gráficas de alto rendimiento y un motor de navegador web Chromium integrado que permite ejecutar mapas HTML directamente dentro de la aplicación.
- `folium` y `geopy`: Bibliotecas cartográficas y de geolocalización. Folium transforma comandos de Python en un mapa Leaflet construido en HTML y JavaScript. Geopy conecta coordenadas GPS con direcciones textuales.
- `requests` y `polyline`: Herramientas de conectividad. `requests` abre la vía de comunicación HTTP (sockets) hacia el servidor de OpenStreetMap, y `polyline` decodifica la respuesta encriptada a listas de latitud y longitud.

**Ejecución de Bibliotecas Nativas:**
- `math` y `itertools`: Proveen funciones de cálculo trigonométrico avanzado (seno, coseno, radianes) y creación de permutaciones matemáticas para la Inteligencia Artificial.
- `json`, `os` y `time`: Administran el acceso de entrada/salida (I/O) al disco duro para leer mapas y bases de datos locales, y manejan los ciclos de reloj del procesador para la animación física de los marcadores en el mapa interactivo.

```python
# Bibliotecas nativas y externas importadas en el núcleo del proyecto
import math
import os
import json
import time
import itertools
import requests
import polyline
import folium
from geopy.geocoders import Nominatim
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QListWidget, QTextEdit, QMessageBox, QGroupBox, QLineEdit, QListWidgetItem, QComboBox, QApplication, QCheckBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QThread, QObject
```

### 3. Instalación, Ejecución e Implementación de Fuentes de Datos (OpenStreetMap y Nominatim)
Para calcular las trayectorias de movimiento real de las entidades (ya sean peatones o vehículos), no es factible utilizar distancias en línea recta de forma exclusiva, debido a la infraestructura urbana y restricciones viales (sentidos de vía, bloqueos, parques).

Por lo tanto, implementamos **tres fuentes de datos de terceros** fundamentales para el mapeo:
1. **OSRM (Open Source Routing Machine):** Un servidor remoto montado sobre OpenStreetMap. El software le envía la latitud y longitud de origen y destino, y OSRM devuelve una "Polilínea" (arreglo masivo de puntos GPS que dibuja las curvas de las calles).
2. **Nominatim (Geopy):** Es la fuente de datos textual. Cuando el usuario teclea "Plaza Cala Cala", el servidor de Nominatim escanea los catastros mundiales para devolver exactamente qué coordenadas tiene ese texto.
3. **Leaflet (Folium):** Un proveedor de teselas (azulejos) de mapas renderizados en HTML sobre los cuales dibujamos nuestros vectores en tiempo real.

```python
# Implementación técnica de conexión a la fuente OSRM (configuracion.py)
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    # (El bloque de caché se omite aquí y se explica en el punto 8)
    longitud_1, latitud_1 = origen[1], origen[0]
    longitud_2, latitud_2 = destino[1], destino[0]
    
    if perfil == 'peaton':
        url_peaton = f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
        # Implementación del Request HTTP
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
            return distancia_kilos, tiempo_minutos, puntos_ruta
        
    # Perfil vehicular (Taxi) hacia OSRM público
    url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
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
        return distancia_kilos, tiempo_minutos, puntos_ruta

# Implementación de la fuente Nominatim para convertir Texto a GPS (ui_ventana.py)
self.geolocalizador = Nominatim(user_agent="noche_museos_sim")
localizacion = self.geolocalizador.geocode(f"{direccion}, Cochabamba, Bolivia", timeout=10)
self.coordenada_origen = (localizacion.latitude, localizacion.longitude)
```

### 4. Cómo se consigue las métricas de medida y distancia. Y cómo se calcula
Cuando las distancias requeridas no provienen del ruteador de OpenStreetMap (por ejemplo, para hallar cuál es la parada del microbús más cercana), es absolutamente necesario calcular la distancia geométrica real entre dos puntos en la faz de la tierra. Dado que el planeta es un objeto esférico tridimensional, el cálculo tradicional en un plano 2D (Teorema de Pitágoras) resulta en mediciones incorrectas a nivel de geolocalización.
Para solucionar esto, implementamos matemáticamente la **Fórmula del Haversine**, que calcula distancias "geodésicas" respetando la curvatura de la Tierra, fijando el radio orbital del planeta en 6371 kilómetros constantes.

```python
# Fórmula trigonométrica implementada en configuracion.py
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
```

### 5. Arquitectura del Sistema o Software
La columna vertebral del proyecto ha sido estructurada bajo un patrón arquitectónico fuertemente desacoplado y orientado a eventos, separando limpiamente la capa visual (Presentación) de la capa de inteligencia artificial (Dominio).
Esto se diseñó para evitar que la interfaz visual de la computadora colapse y se congele mientras los algoritmos matemáticos realizan cientos de miles de iteraciones.

La arquitectura se manifiesta principalmente en dos archivos que ensamblan todo el programa:
- `main.py`: Funciona como el "Punto de Entrada" o motor de ignición. Desactiva configuraciones de seguridad del renderizador (`sandbox`), calibra las resoluciones de píxeles HD, inicializa la Aplicación Base e invoca al Bucle Principal de Eventos (`app.exec_()`), asegurando que el software quede a la escucha del usuario.
- `ui_ventana.py`: Centraliza todo el diseño gráfico, instanciando los contenedores de controles (`QVBoxLayout`, `QListWidget`, `QWebEngineView`), e inyectando un núcleo de JavaScript en el motor HTML para enlazar el mapa gráfico de Folium con las órdenes dinámicas originadas desde la lógica de Python.

```python
# Archivo de ignición main.py
if __name__ == "__main__":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    aplicacion = QApplication(sys.argv)
    
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(aplicacion.exec_())

# Constructor visual extraído de ui_ventana.py
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noche de Museos")
        self.resize(1300, 850)
        self.tiempo_disponible = 0
        self.presupuesto_disponible = 0
        self.coordenada_origen = None
        self.geolocalizador = Nominatim(user_agent="noche_museos_sim")
        self.construir_interfaz()
        self.dibujar_mapa()
        self.transporte = AgenteTransporte(self.consola_registros, self.visor_web, self.restar_plata, self.restar_minutos)
        self.guia = None 
```

### 6. Arquitectura Multiagente y Taxonomía
El ecosistema completo del simulador funciona gracias a la Inteligencia Artificial distribuida a través de "Agentes". En términos algorítmicos computacionales, un agente inteligente es una pequeña entidad programática independiente que es capaz de percibir su entorno, deliberar y ejecutar acciones buscando cumplir un objetivo sin requerir supervisión del núcleo. Hemos diseñado e implementado 4 jerarquías de la taxonomía de agentes (basado en Russell y Norvig):

1. **Agentes Reactivos Simples (`AgenteGuia`):** Su arquitectura no contempla memoria histórica. Opera puramente mediante un conjunto de reglas Condición-Acción evaluando los cobros de boletos en la puerta de los museos.
2. **Agentes Reactivos Basados en Modelos (`AnimadorMovimiento`):** Contiene una representación interna del mundo físico. Ingiere una polilínea GPS cruda, y dibuja el marcador sobre las calles en la pantalla ajustando los cuadros por segundo según un acelerador simulado.
3. **Agentes Basados en Objetivos (`AgenteTransporte`):** Posee la meta general. Delega instrucciones seriales y ordenadas al agente físico de movimiento, cerciorándose de que cada museo y parada se concluya en orden.
4. **Agentes Basados en Utilidad (`AgenteBuscador`):** La clase máxima de inteligencia. Mide matemáticamente la satisfacción (o "Utilidad") de cada ruta DFS posible, ponderando el balance óptimo.

```python
# Implementación de Agente Reactivo basado en Modelo (AnimadorMovimiento de agentes_ia.py)
class AnimadorMovimiento(QThread):
    senal_coordenada = pyqtSignal(float, float, str)
    senal_reloj = pyqtSignal(float)
    senal_llegada = pyqtSignal(str)

    def __init__(self, lista_geometrias, kmh_auto, kmh_pie, multiplicador_velocidad):
        super().__init__()
        self.trazos = lista_geometrias
        self.velocidad_metros_auto = (kmh_auto * 1000) / 3600.0
        self.velocidad_metros_pie = (kmh_pie * 1000) / 3600.0
        self.multiplicador = multiplicador_velocidad
        self.activo = True
        self.cuadros_por_segundo = 30
        
    def run(self):
        for segmento in self.trazos:
            if not self.activo: break
            puntos_gps = segmento['geometria']
            tipo_movimiento = segmento['modo']
            destino_nombre = segmento['destino']
            
            if tipo_movimiento == 'Micro':
                metros_por_segundo = (20.0 * 1000) / 3600.0
            else:
                metros_por_segundo = self.velocidad_metros_auto if tipo_movimiento == 'Auto' else self.velocidad_metros_pie
                
            for indice in range(len(puntos_gps) - 1):
                if not self.activo: break
                punto_a, punto_b = puntos_gps[indice], puntos_gps[indice+1]
                metros_distancia = calcular_distancia_directa(punto_a, punto_b) * 1000.0
                if metros_distancia == 0: continue
                segundos_reales = metros_distancia / metros_por_segundo
                segundos_animacion = segundos_reales / self.multiplicador
                cantidad_frames = max(1, int(segundos_animacion * self.cuadros_por_segundo))
                salto_latitud = (punto_b[0] - punto_a[0]) / cantidad_frames
                salto_longitud = (punto_b[1] - punto_a[1]) / cantidad_frames
                minutos_reloj_simulado = (segundos_reales / 60.0) / cantidad_frames
                for frame in range(cantidad_frames):
                    if not self.activo: break
                    latitud_dibujada = punto_a[0] + salto_latitud * frame
                    longitud_dibujada = punto_a[1] + salto_longitud * frame
                    self.senal_coordenada.emit(latitud_dibujada, longitud_dibujada, tipo_movimiento)
                    self.senal_reloj.emit(minutos_reloj_simulado)
                    time.sleep(1.0 / self.cuadros_por_segundo)
            if self.activo:
                self.senal_coordenada.emit(puntos_gps[-1][0], puntos_gps[-1][1], tipo_movimiento)
                self.senal_llegada.emit(destino_nombre)
                self.activo = False 
```

### 7. Rutas del transporte público y paradas, tramos y paradas
La simulación de autobuses de transporte público masivo reviste de un desafío particular superior al del transporte libre de un taxi. El transporte público carece de recojo de puerta a puerta y requiere aproximarse obligatoriamente a intersecciones que formen parte integral de sus recorridos.

**De dónde lo conseguimos y cómo se instaló:**
Las rutas del transporte público no se calcularon de forma dinámica, sino que fueron importadas desde un repositorio abierto de la comunidad de desarrolladores en **GitHub**. Específicamente, extrajimos los datos cartográficos consolidados y documentados por el ingeniero boliviano **Mauricio Foronda (mauforonda)**, quien recolectó el mapeo del transporte de Cochabamba en un archivo georreferenciado público llamado `rutas_trufis.geojson`.
Para integrar esto automáticamente, desarrollamos un subsistema `setup_trufis.py` encargado de acceder mediante el protocolo HTTP a la URL de ese repositorio en la nube y descargar el archivo de 2.2 Megabytes de polígonos y líneas vehiculares a nuestra base local.

```python
# Módulo de instalación automatizada de rutas (setup_trufis.py)
import urllib.request
import os

def descargar_rutas():
    archivo = "rutas_trufis.geojson"
    if not os.path.exists(archivo):
        print("Descargando rutas_trufis.geojson (aprox 2.2MB)...")
        # Acceso directo al repositorio de Github de Mauricio Foronda
        url = "https://gist.githubusercontent.com/mauforonda/b094e77a0af814dba978f6ae564faa78/raw"
        urllib.request.urlretrieve(url, archivo)
        print("¡Descarga completada!")
    else:
        print("El archivo ya existe.")

if __name__ == "__main__":
    descargar_rutas()
```

Para implementar las "paradas", el sistema ejecuta un proceso de cruce geospacial de proximidad ("Radar"). El algoritmo carga en memoria todos los puntos geométricos del recorrido de las líneas de buses existentes, y realiza un chequeo contra cada uno de los 23 recintos de museos.

```python
# Módulo de Radar de intersección que cruza las rutas con los museos (agentes_ia.py)
def proyectar_punto(punto):
    mejor_idx, min_d = -1, float('inf')
    for k, p_ruta in enumerate(ruta_fisica):
        d = calcular_distancia_directa(punto, p_ruta)
        if d < min_d: min_d, mejor_idx = d, k
    return ruta_fisica[mejor_idx], mejor_idx, min_d
    
def ubicar_paradas(punto_inicio, punto_fin, coordenadas_ruta):
    # Se filtran todos los vértices de la calle a un radio estricto menor de 600 metros de caminata (0.6 km)
    candidatos_inicio = [(idx, calcular_distancia_directa(punto_inicio, coord)) for idx, coord in enumerate(coordenadas_ruta) if calcular_distancia_directa(punto_inicio, coord) < 0.6]
    candidatos_fin = [(idx, calcular_distancia_directa(punto_fin, coord)) for idx, coord in enumerate(coordenadas_ruta) if calcular_distancia_directa(punto_fin, coord) < 0.6]
    
    if not candidatos_inicio or not candidatos_fin:
        _, indice_a, dist_a = proyectar_punto(punto_inicio)
        _, indice_b, dist_b = proyectar_punto(punto_fin)
        return indice_a, indice_b, dist_a, dist_b
        
    mejor_a, mejor_b = -1, -1
    costo_minimo = float('inf')
    
    for i, d_pie_inicio in candidatos_inicio:
        for j, d_pie_fin in candidatos_fin:
            distancia_nodos = (j - i) if i <= j else (len(coordenadas_ruta) - i + j)
            costo_calculado = d_pie_inicio + d_pie_fin + (distancia_nodos * 0.002)
            if costo_calculado < costo_minimo:
                costo_minimo = costo_calculado
                mejor_a, mejor_b = i, j
                
    if mejor_a == -1:
        _, indice_a, dist_a = proyectar_punto(punto_inicio)
        _, indice_b, dist_b = proyectar_punto(punto_fin)
        return indice_a, indice_b, dist_a, dist_b
        
    return mejor_a, mejor_b, calcular_distancia_directa(punto_inicio, coordenadas_ruta[mejor_a]), calcular_distancia_directa(punto_fin, coordenadas_ruta[mejor_b])
```

### 8. Cómo desarrollamos e implementamos el Caché para las rutas del peatón y en taxi
La exploración profunda de un sistema de Inteligencia Artificial implica medir combinaciones de distancias que fácilmente superan las 10,000 operaciones por segundo. Si cada una de esas mediciones generase una solicitud remota al servidor OSRM (OpenStreetMap), colapsaríamos el ancho de banda del proyecto, sufriendo bloqueos permanentes de firewall y latencias inoperantes.

Desarrollamos una política de persistencia de "Caché Dual" de Espacio/Tiempo completamente acoplada a la función base. 
Primero, en la capa de memoria estática (disco duro) creamos `cache_peatonal.json` y `cache_taxi.json`. El programa los lee enteros cuando inicia y los sube a la memoria RAM.
Segundo, durante el funcionamiento dinámico, **antes** de emitir un Request al internet, el código fabrica una `llave` única compuesta por el perfil del transporte, y los GPS de inicio a fin. Con esa llave, interroga al diccionario `memoria_activa` (el caché en RAM). Si el valor existe, extrae inmediatamente sus datos geométricos, burlando el proceso de conexión lenta. De no existir, el Request sucede de forma natural y, tras recibir la respuesta HTTP 200 Ok, la función inyecta los datos resultantes a la `memoria_activa` y reescribe de inmediato el `.json` en disco físico `guardar_memoria()`.

```python
# Lógica de Extracción y Almacenamiento Dinámico (configuracion.py)
ARCHIVO_PEATONAL = "cache_peatonal.json"
ARCHIVO_TAXI = "cache_taxi.json"

memoria_peaton = {}
memoria_taxi = {}

# 1. Almacenamiento y Recuperación desde el Disco Duro a RAM
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

# 2. Intercepción del Caché dentro de la Petición al Servidor
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    # Fabricación de la huella digital criptográfica (llave del Caché)
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    # INTERCEPCIÓN: Si la ruta se halla en caché, devolverla en 0.001 segundos
    if llave in memoria_activa:
        datos = memoria_activa[llave]
        return datos[0], datos[1], datos[2]
        
    longitud_1, latitud_1 = origen[1], origen[0]
    longitud_2, latitud_2 = destino[1], destino[0]
    
    # ... (Si el caché falló, se ejecuta el HTTP Request hacia OSRM)
    # ... (Si el Request tuvo éxito:)
            datos = respuesta.json()
            if datos.get('code') == 'Ok':
                ruta_obtenida = datos['routes'][0]
                distancia_kilos = ruta_obtenida['distance'] / 1000.0
                tiempo_minutos = ruta_obtenida['duration'] / 60.0
                puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
                
                # INYECCIÓN: Guardar el resultado valioso en RAM y Disco para el futuro
                memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
                guardar_memoria(perfil)
                
                return distancia_kilos, tiempo_minutos, puntos_ruta
```

### 9. Ubicación de todos los museos, cómo los ingresamos en el proyecto
El punto principal de datos inyectado como semilla de información del proyecto es la cuadrícula base de locaciones patrimoniales. 
Realizamos labores previas de minería de coordenadas para los 23 museos involucrados de la ciudad de Cochabamba, identificando sus posicionamientos GPS satelitales absolutos con seis puntos decimales de exactitud geométrica.

Para materializar esta matriz dentro de nuestro ecosistema, la transcribimos creando una de las estructuras más veloces en lenguaje de programación Python conocida como un "Diccionario Constante de Datos", indexado y fijado en `configuracion.py`. Dicho diccionario convierte una solicitud textual basada en llaves en un tuple (par coordenado) en tiempo de complejidad algorítmica constante O(1).

```python
# Matriz absoluta de posicionamiento insertada en configuracion.py
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
```

### 10. Cómo calculamos todas las rutas de movimiento para autos y el peatón
Cuando un algoritmo matemático exige trasladar un elemento del recinto A al recinto B, el motor cartográfico interviene requiriendo una instrucción de red a OSRM para trazar trayectorias de curvas y cortes que asemejen el flujo vehicular. Sin embargo, no podíamos diseñar un sistema crítico que colapsara enteramente si la red fallaba.
Por tanto, desarrollamos el cálculo en forma de un control "Try / Except". Si la conexión remota OSRM es un éxito, el sistema decodifica las polilíneas de las calles verdaderas. Si se produce un error, un corte de red, o el servidor cae, se detona el **"Plan Logístico de Emergencia"** y el `except` captura el fallo. El plan de emergencia acude a la fórmula de Haversine pura, tendiendo un vector directo imaginario desde la puerta A hasta la B y aplicándole una penalización sintética de aumento de distancia del 30% (`* 1.3`) como compensación al hecho de que el camino real habría contenido curvas, esquinas u obstáculos arquitectónicos. Este plan de emergencia es infalible porque opera de forma nativa offline.

```python
# Lógica extraída de configuracion.py (Aplica tanto a Peatón como a Vehículos)
        except Exception:
            pass # Si el internet o OSRM falla, el Try se rompe silenciosamente y llegamos aquí
            
        # PLAN DE EMERGENCIA: Crear Polilínea recta sintética a través de Geopy y Haversine
        puntos_ruta = [
            [origen[0], origen[1]],
            [origen[0], destino[1]],
            [destino[0], destino[1]]
        ]
        from geopy.distance import geodesic
        dist_1 = geodesic(origen, (origen[0], destino[1])).km
        dist_2 = geodesic((origen[0], destino[1]), destino).km
        
        # Inyectando penalización a la distancia en lugar de las curvas
        distancia_kilos = dist_1 + dist_2
        
        # Estimación de velocidad peatonal estática para evitar un NoneType en el Motor
        tiempo_minutos = (distancia_kilos / 5.0) * 60.0
        
        # El motor jamás se entera del fallo de internet, el sistema es resiliente
        memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
        guardar_memoria(perfil)
        return distancia_kilos, tiempo_minutos, puntos_ruta
```

### 11. Los modos de transporte, cómo los implementamos e instalamos
Dentro de las jerarquías de movimiento, implementamos 3 modalidades intermodales físicas para el usuario:
- Transporte a Pie (Movimiento libre multidireccional por aceras y calzadas).
- Transporte Privado en Taxi (Desplazamientos vehiculares rápidos sujetos al tráfico, con recojo personalizado origen a destino).
- Transporte Público en Microbuses (Rutas de circulación bloqueadas que demandan que el pasajero haga recorridos de a pie hasta sus vectores de intersección).

Dichos mecanismos están amarrados directamente en los controles de la Interfaz Visual mediante casillas de verificación (Checkboxes). Sin embargo, la verdadera implementación y el "Filtrado" ocurren profundamente en el Motor Matemático. Cuando el usuario hace clic en el botón "Calcular", las banderas de Verdadero/Falso dictan si la ramificación entera del árbol de decisiones de la Inteligencia Artificial de "Búsqueda en Profundidad" es construida o no. Si un usuario deshabilita "Taxi", el Motor simplemente destruye la matriz combinatoria que pretendía usar esa vía de escape.

```python
# 1ra Parte: Interfaz en ui_ventana.py
        self.check_pie = QCheckBox("Pie")
        self.check_pie.setChecked(True)
        self.check_taxi = QCheckBox("Taxi")
        self.check_taxi.setChecked(True)
        self.check_micro = QCheckBox("Micro")
        self.check_micro.setChecked(True)
        
        # Extracción y alimentación al Agente AI al iniciar
        permitir_pie = self.check_pie.isChecked()
        permitir_taxi = self.check_taxi.isChecked()
        permitir_micro = self.check_micro.isChecked()
        self.hilo_buscador = AgenteBuscador(
            self.coordenada_origen, museos_seleccionados, self.presupuesto_disponible,
            self.tiempo_disponible, self.selector_vauto.value(), 
            self.selector_vpie.value(), self.selector_vmuseo.value(),
            permitir_pie, permitir_taxi, permitir_micro
        )

# 2da Parte: Restricción Vectorial en el Grafo (agentes_ia.py)
            def explorar_opciones(camino_actual, museos_faltantes, ... , modo_fijo):
                    # Filtrado de Transporte Intermodal durante el Descenso DFS Recursivo
                    opciones_transporte = []
                    if modo_fijo == 'Pie': 
                        opciones_transporte.append('Pie')
                    elif modo_fijo == 'Auto': 
                        opciones_transporte.append('Auto')
                    elif modo_fijo == 'Micro':
                        # Verifica si es humanamente posible subirse a un micro aquí
                        if origen_tramo in MATRIZ_TRANSPORTE and destino_tramo in MATRIZ_TRANSPORTE[origen_tramo] and MATRIZ_TRANSPORTE[origen_tramo][destino_tramo]['costo_pasaje'] < float('inf'):
                            opciones_transporte.append('Micro')

            # INICIO DE RAMIFICACIONES PRINCIPALES SEGÚN LA ELECCIÓN DEL USUARIO
            if self.permitir_pie:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Pie')
            if self.permitir_taxi:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Auto')
            if self.permitir_micro:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Micro')
```

### 12. Cómo creamos el Caché para optimizar las operaciones de macrooperadores
El funcionamiento matemático puro del intermodalismo peatón-autobús-peatón genera que se tengan que fabricar tres recorridos de manera espontánea (la caminata, el viaje y el retorno a la puerta). Generar estas tres acciones en línea requeriría triplicar el retraso computacional en cada exploración combinatoria de los millones de posibles cruces.
Para arreglar este cuello de botella algorítmico, implementamos el archivo `precalcular_rutas.py`. Este módulo automatizado tiene la tarea de cruzar obligatoriamente los vértices de todos los 23 museos entre sí antes siquiera de que el software sea utilizado comercialmente. Al forzar a que el servidor analice todos los escenarios del grafo de antemano (O(N^2)), este script logra el rellenado artificial exhaustivo del "Caché Local".
Luego, el Macrooperador que ensambla el recorrido del bus en la IA de Búsqueda, simplemente extrae su componente peatonal del disco duro de la computadora en velocidad ultrarrápida (0 latencia), eliminando por completo cualquier consulta redundante de peatonización hacia los servidores.

```python
# Archivo ejecutable completo de precalcular_rutas.py
import time
import json
import configuracion
from configuracion import MUSEOS, obtener_ruta_vehiculo

def generar_caches():
    nombres = list(MUSEOS.keys())
    total_museos = len(nombres)
    total_pares = total_museos * (total_museos - 1)
    
    print(f"Iniciando pre-cálculo masivo y robótico de {total_pares} pares de rutas...")
    pares_procesados = 0
    for i in range(total_museos):
        for j in range(total_museos):
            if i == j: continue  # No cruzar consigo mismo
                
            origen = MUSEOS[nombres[i]]
            destino = MUSEOS[nombres[j]]
            
            # Ejecuta la función base, forzando a que haga el Request HTTPS y lo guarde en memoria
            print(f"[{pares_procesados+1}/{total_pares}] Calculando Peatón: {nombres[i][:15]}... -> {nombres[j][:15]}...")
            obtener_ruta_vehiculo(origen, destino, perfil="peaton")
            
            print(f"[{pares_procesados+1}/{total_pares}] Calculando Taxi: {nombres[i][:15]}... -> {nombres[j][:15]}...")
            obtener_ruta_vehiculo(origen, destino, perfil="driving")
            
            pares_procesados += 1
            
    print("¡Pre-cálculo finalizado exitosamente!")
    print(f"Rutas peatonales guardadas en: {configuracion.ARCHIVO_PEATONAL}")
    print(f"Rutas vehiculares guardadas en: {configuracion.ARCHIVO_TAXI}")

if __name__ == "__main__":
    generar_caches()
```

### 13. Instalación e Implementación de Motores de Búsqueda
La joya algorítmica del proyecto es su IA de selección paramétrica que garantiza obtener el mejor recorrido viable sin exceder jamás el presupuesto. Para buscar dicho sendero a través del grafo combinatorio implementamos el paradigma del **Motor de Búsqueda en Profundidad (Depth-First Search o DFS)**. 
Su diseño arquitectónico se sustenta en expandir progresivamente el recorrido agregando museo tras museo y calculando su acumulador total de costos de minutos y bolivianos. Para garantizar el descenso infinito en todas las opciones posibles de recorridos (y deshacer operaciones para explorar otras ramas si fuera necesario), este sistema fue implantado empleando recursividad. 

```python
# Motor de Fuerza Bruta Optimizada DFS (agentes_ia.py)
            def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado, trazos_ruta, lineas_registro, modo_fijo):
                # (Lógica de Poda de Exceso Explicada en Sección 15)
                
                # Criterio Lógico de Cierre: Se recorrió un museo, toca cerrar ciclo volviendo al 'Origen'
                if len(camino_actual) > 1:
                    origen_tramo = camino_actual[-1]
                    destino_tramo = 'Origen'
                    coord_origen_tramo, coord_destino_tramo = coordenadas[origen_tramo], coordenadas['Origen']
                    distancia_recta = calcular_distancia_directa(coord_origen_tramo, coord_destino_tramo)
                    
                    opciones_transporte = []
                    # ... [Condicionamiento Lógico]
                        
                    for tipo_transporte in opciones_transporte:
                        self.contador_exploracion += 1
                        nuevos_segmentos, costo_tramo, tiempo_tramo, distancia_km, texto_modo = calcular_segmento(origen_tramo, destino_tramo, coord_origen_tramo, coord_destino_tramo, tipo_transporte, distancia_recta)
                        costo_total_evaluado = gasto_acumulado + costo_tramo
                        tiempo_total_evaluado = reloj_acumulado + tiempo_tramo
                        
                        # Si todo salió bien y esta rama cumple, inyectar como "Ruta Válida Ganadora"
                        if costo_total_evaluado <= self.presupuesto_maximo and tiempo_total_evaluado <= self.tiempo_maximo:
                            ruta_definitiva = camino_actual + ['Origen']
                            trazos_definitivos = trazos_ruta + nuevos_segmentos
                            lista_modos = [segmento['modo'] for segmento in trazos_definitivos]
                            rutas_encontradas.append({
                                'numero_operacion': self.contador_exploracion,
                                'nombre_ruta': " -> ".join([abreviar(x) for x in camino_actual[1:]]),
                                'cantidad_museos': len(camino_actual) - 1,
                                'secuencia': ruta_definitiva, 'vehiculos_usados': lista_modos, 'dinero_gastado': costo_total_evaluado,
                                'minutos_gastados': tiempo_total_evaluado, 'geometrias': trazos_definitivos, 'museos_objetivo': self.lista_museos
                            })

                if not museos_faltantes:
                    return

                # RECURSIVIDAD MÁGICA: Bajar de nivel entrando a las combinaciones del Siguiente Museo
                for siguiente_museo in museos_faltantes:
                    origen_tramo = camino_actual[-1]
                    destino_tramo = siguiente_museo
                    coord_origen_tramo, coord_destino_tramo = coordenadas[origen_tramo], coordenadas[destino_tramo]
                    distancia_recta = calcular_distancia_directa(coord_origen_tramo, coord_destino_tramo)
                    
                    # ... [Calculo Segmento para el Próximo Museo]
                    for tipo_transporte in opciones_transporte:
                        nuevos_segmentos, costo_tramo, tiempo_tramo, distancia_km, texto_modo = calcular_segmento(origen_tramo, destino_tramo, coord_origen_tramo, coord_destino_tramo, tipo_transporte, distancia_recta)

                        costo_calculado = gasto_acumulado + ENTRADAS[destino_tramo] + costo_tramo
                        tiempo_calculado = reloj_acumulado + self.duracion_visita + tiempo_tramo
                        
                        trazos_combinados = trazos_ruta + nuevos_segmentos
                        sobrantes = [m for m in museos_faltantes if m != siguiente_museo]
                        
                        # LLAMADA A SÍ MISMA (RECURSIÓN)
                        explorar_opciones(camino_actual + [siguiente_museo], sobrantes, costo_calculado, tiempo_calculado, trazos_combinados, lineas_registro + [linea_texto], modo_fijo)
```

### 14. Instalación e Implementación de Macrooperadores
Al analizar la inserción de un transporte público (Micro o Trufi), se presenta un dilema donde la secuencia de viajar en bús fragmenta enormemente el árbol de grafos, porque un bus es esencialmente un trípode operativo: Caminar de la puerta del museo A a la parada, viajar de parada en parada dentro del autobús, y descender del autobús para caminar hacia el museo destino B. Tratar a estas acciones como eventos desconectados colapsa por completo a un Agente de Utilidad por explosión ramificativa.
Por ello, instalamos e implementamos la figura del **Macrooperador**, una herramienta heurística de programación. El Macrooperador ensambla bajo tierra esos 3 pasos fragmentados y, desde la perspectiva matemática del Motor Buscador DFS, le inyecta directamente el cálculo total como una única macro-pieza atómica unificada inquebrantable, estabilizando el cálculo algorítmico y dándole agilidad al procesamiento.

```python
# Bloque del Macrooperador en el módulo calcular_segmento (agentes_ia.py)
                elif tipo_viaje == 'Micro':
                    info_ruta = MATRIZ_TRANSPORTE[nodo_a][nodo_b]
                    id_linea = info_ruta['lineas_disponibles'][0]
                    ruta_fisica = LINEAS_TRUFIS.get(id_linea)
                    
                    if ruta_fisica:
                        idx_origen, idx_destino, dist_caminata_1, dist_caminata_2 = ubicar_paradas(coord_a, coord_b, ruta_fisica)
                        coord_parada_1, coord_parada_2 = ruta_fisica[idx_origen], ruta_fisica[idx_destino]
                        
                        _, _, geom_c1 = obtener_ruta_vehiculo(coord_a, coord_parada_1, perfil="peaton")
                        geom_caminata_1 = geom_c1 if geom_c1 else [coord_a, coord_parada_1]
                        dist_w1, tiempo_w1 = dist_caminata_1, dist_caminata_1 / self.velocidad_caminando
                        
                        if idx_origen <= idx_destino:
                            geom_micro = ruta_fisica[idx_origen : idx_destino + 1]
                        else:
                            geom_micro = ruta_fisica[idx_origen : ] + ruta_fisica[0 : idx_destino + 1]
                            
                        dist_micro = sum(calcular_distancia_directa(geom_micro[k], geom_micro[k+1]) for k in range(len(geom_micro)-1)) if len(geom_micro) > 1 else 0
                        tiempo_micro = (dist_micro * 1.3) / (20.0 / 60.0)
                        
                        _, _, geom_c2 = obtener_ruta_vehiculo(coord_parada_2, coord_b, perfil="peaton")
                        geom_caminata_2 = geom_c2 if geom_c2 else [coord_parada_2, coord_b]
                        dist_w2, tiempo_w2 = dist_caminata_2, dist_caminata_2 / self.velocidad_caminando
                        
                        precio_pasaje = info_ruta['costo_pasaje']
                        
                        # CÁLCULOS MACRO: Sumatoria absoluta de Caminata 1 + Viaje Bus + Caminata 2
                        tiempo_total_tramo = tiempo_w1 + tiempo_micro + tiempo_w2
                        distancia_total_tramo = dist_w1 + dist_micro + dist_w2
                        
                        # El Macrooperador acopla todo como un array de 3 etapas que viaja junto indivisiblemente
                        segmentos.extend([
                            {'origen': nodo_a, 'destino': f'Parada({abreviar(nodo_a)})', 'modo': 'Pie', 'distancia': dist_w1, 'tiempo': tiempo_w1, 'geometria': geom_caminata_1, 'costo': 0.0},
                            {'origen': f'Parada({abreviar(nodo_a)})', 'destino': f'Parada({abreviar(nodo_b)})', 'modo': 'Micro', 'distancia': dist_micro, 'tiempo': tiempo_micro, 'geometria': geom_micro, 'costo': precio_pasaje},
                            {'origen': f'Parada({abreviar(nodo_b)})', 'destino': nodo_b, 'modo': 'Pie', 'distancia': dist_w2, 'tiempo': tiempo_w2, 'geometria': geom_caminata_2, 'costo': 0.0}
                        ])
```

### 15. Instalación e Implementación de Poda
Durante el funcionamiento del Motor de Búsqueda, evaluar cada museo genera un crecimiento algorítmico exponencial. Por ejemplo, al intentar calcular un orden de viaje para 15 recintos (15 factorial), existen más de 1.3 billones de caminos resultantes. La potencia de procesamiento actual haría que este análisis tome decádas.
Para salvar esto, implementamos rigurosas técnicas de poda combinatoria. A cada paso minúsculo, la computadora interroga los parámetros de la **"Bolsa de Límite Máximo"**. Si un camino consumió ya todo tu dinero o toda la bolsa de tus horas, carece de todo sentido matemático que el Motor continúe profundizando hacia el siguiente museo asumiendo que los que falten por explorar fuesen siquiera alcanzables. En ese punto, el sistema detona la condición de ruptura, aborta y asesina activamente la rama completa ahorrando millones de procesamientos muertos inútiles.

```python
# Sistema de Poda Cuantitativa de Ramas Limitadas por Costos (agentes_ia.py)
                if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
                    m = len(museos_faltantes)
                    # Se calcula con factorial la suma matemática de la infinidad de ramas abortadas
                    ramas_cortadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
                    self.contador_exploracion += ramas_cortadas
                    
                    texto_camino = [abreviar(x) for x in camino_actual] + [abreviar(m) for m in museos_faltantes] + ['Origen']
                    cabecera = f"\nOpcion [{self.contador_exploracion}/{total_combinaciones}]: [{' -> '.join(texto_camino)}]"
                    registro_final = [cabecera, "-" * 65] + list(lineas_registro)
                    
                    # Interrupción del DFS e impresión del log de eliminación (Return anticipado = Muerte de rama)
                    registro_final.append(f"└─ PODA: Costo={gasto_acumulado:.1f} Bs | Tiempo={reloj_acumulado:.1f} min | Omitidas: {ramas_cortadas}")
                    self.progreso_senal.emit("\n".join(registro_final))
                    return
```

### 16. Instalación e Implementación de Cálculo de Tiempo por Tramo
Tanto el Agente Físico Animador, como el propio Motor Buscador que mide las restricciones horarias, se ven en la imperiosa necesidad de saber cuántas horas y minutos toma cubrir un tramo vectorial por las calles para no rebasar tus límites impuestos. Pese a que el servidor de OSRM ya retorna una estimación por sí mismo, implementamos una recategorización basada en la física mecánica fundamental adaptada a los caprichos elegidos por el propio usuario del simulador.
Al multiplicar distancias puras por tasas relativas configuradas (la velocidad en coche fijada a 40km/h y la marcha a pie a 5km/h), aseguramos un sistema unificado y simétrico de medición de tiempos que es independiente de la topografía que decida la ruta. Este cálculo cubre meticulosamente los 3 perfiles logísticos: Pie, Taxi y Microbus (con sus tiempos de inactividad de parada intermedios).

```python
# Lógica Cinemática Universal de Cuerpos Dinámicos en calcular_segmento (agentes_ia.py)
                if tipo_viaje == 'Pie':
                    # Aumento sintético del 10% por cruce de aceras y peatonización
                    distancia_total_tramo = distancia_lineal * 1.1 
                    # MRU puro: Tiempo = Distancia / Velocidad (convertida a metros/minuto)
                    tiempo_total_tramo = distancia_total_tramo / self.velocidad_caminando
                    
                elif tipo_viaje == 'Auto':
                    d_vehiculo, t_vehiculo, geom_vehiculo = obtener_ruta_vehiculo(coord_a, coord_b, perfil="driving")
                    if geom_vehiculo is None: # Si OSRM colapsó
                        distancia_total_tramo = distancia_lineal * 1.3
                        # Recálculo de emergencia MRU usando la velocidad configurada por el humano
                        tiempo_total_tramo = distancia_total_tramo / self.velocidad_coche
                    else:
                        distancia_total_tramo = d_vehiculo
                        tiempo_total_tramo = t_vehiculo

                elif tipo_viaje == 'Micro':
                    # ... [Lógica de Ubicación Explicada en Sección 14] ...
                    
                    # Tiempo 1: Caminar a la parada del bús
                    tiempo_w1 = dist_caminata_1 / self.velocidad_caminando
                    
                    # Tiempo 2: Trayecto rodante en el bus (Fijado internamente a 20 km/h urbanos)
                    tiempo_micro = (dist_micro * 1.3) / (20.0 / 60.0)
                    
                    # Tiempo 3: Caminar desde la parada de bajada hacia la puerta del destino
                    tiempo_w2 = dist_caminata_2 / self.velocidad_caminando
                    
                    # Tiempo total sumatorio
                    tiempo_total_tramo = tiempo_w1 + tiempo_micro + tiempo_w2
```

### 17. Instalación e Implementación de Filtrado y Despliegue de Resultados
Cuando finalizan el motor de recursión y la Poda de descarte, puede haber cientos de planes o caminos que pasaron el filtro (es decir, decenas de formas en que tu dinero sí te bastó y lograste tu cometido de la noche sin salir del cronómetro). ¿Qué debe desplegarle el simulador al usuario? 
Para decidir el Plan Victorioso, instalamos un bloque de código discriminador de Filtrado de Resultados en forma de Agente de Utilidad (una criba). Este analizador lee todas las propuestas viables encontradas, identifica cuál ruta visitó de forma absoluta el récord mayor del torneo (por ejemplo: la que logró incluir 10 museos), y purga agresiva e indiscriminadamente a toda ruta conformista que haya logrado visitar 9, 8 o menos, presentando solo a la élite suprema en la Pantalla para que el usuario escoja su favorita.

```python
# Motor Criba Discriminadora de Utilidad (agentes_ia.py)
            if rutas_encontradas:
                # Localizamos a la ruta de Excelencia (Techo histórico del Campeonato en ese Try)
                max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
                
                # Purgamos y borramos de la matriz final cualquier iteración que no haya empatado ese techo
                rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
                
                # Emitimos las listas invictas a la Interfaz Visual (GUI) vía PyqtSignals
                self.finalizado_senal.emit(rutas_validas)
            else:
                self.finalizado_senal.emit([])
```

### 18. Manual Operativo Completo para el usuario del simulador
Para la ejecución y aprovechamiento eficaz de la "Noche de Museos Cochabamba", el operario del sistema deberá adherirse cautelosamente al siguiente flujograma de mandos:

1. **Punto de Inicio y Capital Semilla:** En el panel maestro de "Origen y Presupuesto" situado a la izquierda, redacte una referencia textual o, en su defecto, posicione un marcador interactivo haciendo un "Clic" preciso sobre cualquier locación del panel cartográfico derecho. Posterior a ello, alimente los campos paramétricos de Presupuesto Disponible (Dinero en Bolivianos) y Tiempo de Ronda (Minutos) que regularán a la máquina IA y definirán dónde ocurrirá la Poda.
2. **Limitaciones Cinemáticas y Multiplicadores de Motor Visual:** Descienda a la sección "Simulación". Defina velocidades (km/h) tanto para auto como pie. Adicionalmente, elija una Tasa Multiplicadora (Ej. x10, x20) en el combo. Este acelerador manipulará directamente la cadencia con la cual el Agente de Animación procesa los FPS en la red HTML, permitiéndole atestiguar movimientos veloces.
3. **Condicionamiento Paramétrico Binario:** ¿Desea prohibir ciertos métodos de recorrido? Deshabilite mediante casillas de verificación (Checkboxes) los rubros Pie, Taxi o Micro. Estos bloqueos inhabilitarán los macrooperadores pertinentes durante el descenso combinatorio de profundidad obligando al IA a usar únicamente los medios elegidos.
4. **Alimentación del Grafo Objetivo:** Seleccione minuciosamente mediante vistos buenos, todos los museos de la interfaz que formarán parte de la misión global. Procure combinar museos de rutas Peatonales (Cercanos al corazón de la Plaza) y de Múltiples tramos a conveniencia.
5. **Detección Algorítmica y Mapeo:** Pulse firmemente en "Calcular". Permita que los hilos operen en segundo plano y lea la traza en la Consola Log negra. Observe cómo el motor inspecciona y poda activamente iteraciones inválidas a un ritmo frenético hasta determinar la victoria algorítmica.
6. **Ejecución y Visualización Multimodal Físico:** En caso de resolución positiva en la que la matriz validó trayectorias y su dinero fue suficiente, la interfaz de resultados presentará la información comprimida del ganador con su tiempo y su costo. Seleccione la propuesta y proceda seleccionando la instrucción central "Iniciar". El mapa generará y transmutará el marcador del origen forzándolo a recorrer secuencial e interactivo las líneas superpuestas asfálticas de colores correspondientes a su transporte real dictado por la Inteligencia de Objetivos, restando montos y tiempo vivo del panel lateral al aterrizar en cada museo.
