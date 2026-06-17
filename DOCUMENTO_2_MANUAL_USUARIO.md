# MANUAL EXHAUSTIVO DE DESARROLLO EN PYTHON Y GUÍA DE USUARIO
## Proyecto: Optimización de Rutas para la Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

Este documento técnico funciona como la piedra angular del desarrollo e implementación del software que hemos construido. Aquí detallamos línea por línea la abstracción técnica detrás de la Inteligencia Artificial construida por nosotros en Python, junto a las instrucciones estrictas para su configuración e instalación.

---

## SECCIÓN I: INSTALACIÓN Y JUSTIFICACIÓN DEL ECOSISTEMA PYTHON
Nuestro programa requiere la instalación de un entorno virtual (`venv` en Python) o la instalación global de las librerías requeridas. Estructuramos el stack tecnológico para evitar el uso de servidores backend externos, condensando tanto la GUI (Interfaz) como la lógica y renderizado web en un solo archivo ejecutable.

**Comando de instalación global:**
```bash
pip install PyQt5 PyQtWebEngine folium geopy requests polyline
```

**Explicación Fundamental de las Bibliotecas (¿Para qué se instalaron?):**
1. **PyQt5 & PyQtWebEngine:** 
   - *Justificación (Teoría):* Las interfaces estándar de Python (Tkinter) carecen de soporte robusto para la navegación web interna. PyQt5 incorpora un puente de C++ hacia Python extremadamente rápido. `PyQtWebEngine` incluye una versión mínima de Google Chrome que se empaqueta dentro del programa.
   - *Comando de Terminal:* `pip install PyQt5 PyQtWebEngine`
   - *Código de Ejecución en el Proyecto:*
```python
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys

# Levantando el motor de interfaz en main.py y ui_ventana.py
aplicacion = QApplication(sys.argv)
visor_web = QWebEngineView()
```
2. **Folium (Librería Leaflet en Python):**
   - *Justificación (Teoría):* Dibujar calles a mano usando lienzos básicos es impensable para un mapa global. Python usa Folium para automatizar la inyección de una librería de código libre. Toma nuestros vectores de líneas (Latitud, Longitud) y genera un archivo en `Lenguaje de Marcado de Hipertexto` totalmente programable.
   - *Comando de Terminal:* `pip install folium`
   - *Código de Ejecución en el Proyecto:*
```python
import folium

# Generando el mapa de Cochabamba en ui_ventana.py
mapa_folium = folium.Map(location=[-17.3895, -66.1568], zoom_start=14)
folium.CircleMarker(location=[-17.3935, -66.1568], color='red').add_to(mapa_folium)
mapa_folium.save("mapa_museos.html")
```
3. **Geopy:**
   - *Justificación (Teoría):* El humano no comprende coordenadas `(-17.3897, -66.1579)`, comprende lenguaje (Ej. "Convento Santa Teresa"). Al invocar la herramienta a través de Geopy, enviamos la dirección textual a servidores internacionales, y recibimos el punto exacto de coordenadas geográficas.
   - *Comando de Terminal:* `pip install geopy`
   - *Código de Ejecución en el Proyecto:*
```python
from geopy.geocoders import Nominatim

# Código usado en ui_ventana.py para buscar el Punto de Partida
geolocalizador = Nominatim(user_agent="NocheMuseosCba")
ubicacion = geolocalizador.geocode("Plaza de las Banderas, Cochabamba")

if ubicacion:
    latitud_origen = ubicacion.latitude
    longitud_origen = ubicacion.longitude
```
4. **Requests & Polyline:**
   - *Justificación (Teoría):* Necesitamos decirle al auto de la simulación por dónde ir sin pasar encima de los edificios. `Requests` hace peticiones de red al servidor. `Polyline` es el decodificador matemático que traduce la cadena devuelta a una extensa lista Python de coordenadas geográficas.
   - *Comando de Terminal:* `pip install requests polyline`
   - *Código de Ejecución en el Proyecto:*
```python
import requests
import polyline

# Obteniendo ruta real en configuracion.py
url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"

headers = {"User-Agent": "NocheMuseosSimulador/1.0"}
respuesta = requests.get(url, headers=headers, timeout=5)
datos = respuesta.json()

if datos.get('code') == 'Ok':
    ruta_obtenida = datos['routes'][0]
    # Desencriptando a lista de Lat/Lon para la animación
    coordenadas_calle = polyline.decode(ruta_obtenida['geometry'])
```

**Explicación de las Bibliotecas Nativas (Preinstaladas en Python):**
El proyecto también hace uso extensivo de las librerías "Core" de Python, las cuales no requieren ser instaladas pero son fundamentales para el ecosistema:
1. **`math`**: Utilizada para los cálculos avanzados de trigonometría esférica necesarios para medir la distancia real en la Tierra entre dos coordenadas geográficas.
2. **`json`**: Encargada de leer y escribir nuestros cachés duales (`cache_peatonal.json` y `cache_taxi.json`), permitiendo la persistencia de datos sin conexión a internet y previniendo el bloqueo de nuestra dirección de protocolo de internet en servidores remotos.
3. **`os` y `sys`**: Librerías de sistema operativo. Proveen la capacidad de interactuar con el entorno (rutas relativas de archivos), controlar las banderas del motor de navegación visual y salir del programa de forma segura.
4. **`time`**: Controla el ritmo del Hilo de Animación frenando el bucle unos milisegundos para lograr el efecto visual de fluidez de movimiento (fotogramas por segundo) en los viajes de la simulación.
5. **`itertools`**: Fundamental para el Agente Buscador. Es el motor combinatorio que genera eficientemente todas las permutaciones posibles de las rutas seleccionadas por el usuario.

**El Papel Fundamental de OpenStreetMap (OSM) en el Proyecto:**

1. **Justificación (Teoría):** 
   OpenStreetMap es la inmensa base de datos geográfica comunitaria que da vida a toda nuestra simulación. Se incorpora al proyecto en dos pilares:
   - **Visualmente:** Cuando `folium` dibuja el mapa, no genera vectores de la nada, sino que descarga las *Teselas* (imágenes cuadradas) desde los servidores de OpenStreetMap.
   - **Físicamente:** La Interfaz de Programación de Aplicaciones de Enrutamiento utiliza los datos de OpenStreetMap en Bolivia para indicarle a la Inteligencia Artificial qué calles son de sentido único, dónde hay parques y veredas.
   
2. **Comando de Terminal (Instalación):** 
   *No aplica.* Al ser una base de datos pública y un servicio en la nube, OpenStreetMap no se instala localmente, sino que se accede a sus servidores vía internet durante la ejecución del programa.

3. **Código de Ejecución en el Proyecto:**
   En el archivo `configuracion.py`, realizamos una petición a los servidores OSRM basados en OpenStreetMap para rastrear el camino físico del peatón:
```python
import requests
import polyline

# Se invoca a routing.openstreetmap.de pidiendo la ruta peatonal (routed-foot)
url_peaton = f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"

headers = {"User-Agent": "NocheMuseosSimulador/1.0"}
respuesta = requests.get(url_peaton, headers=headers, timeout=5)
datos = respuesta.json()

if datos.get('code') == 'Ok':
    # Se extrae la cadena encriptada de OSM y se decodifica en puntos GPS
    ruta_obtenida = datos['routes'][0]
    puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
```

---

## SECCIÓN II: ARQUITECTURA DE SOFTWARE (PROGRAMACIÓN ORIENTADA A OBJETOS Y QTHREAD)
En interfaces gráficas, Python ejecuta su código línea por línea en el Hilo principal. Si le decíamos a Python "Explora 10 millones de combinaciones matemáticas para encontrar la ruta a los museos", la interfaz visual (los botones, el mapa) se quedaba completamente congelada. 

### 2.1. El Multithreading mediante `QThread`
Nuestra solución técnica fue crear los Agentes usando clases que heredan explícitamente de la librería paralela de Qt (`QThread`). 
- **Agente `BuscadorRutas`:** Analiza y poda el árbol factorial. Lo programamos para ejecutarse en un núcleo distinto del procesador. A medida que avanza, emite una señal nativa `pyqtSignal(str)` que intercepta el Hilo Principal. Esto actualiza la consola en negro con verde del simulador sin colapsar la pantalla.
- **Agente `AnimadorMovimiento`:** También lo configuramos como un `QThread`. Su función es simple pero vital: posee un bloqueante (`time.sleep(1/30)`) que representa los fotogramas (30 FPS). En cada fotograma, predice matemáticamente el salto intermedio.

### 2.2. Rutas, Paradas de Micros y su Incorporación Visual

1. **Justificación (Teoría):** 
   A diferencia del trazado general de OSRM, las líneas de micros de Cochabamba no están en servidores internacionales. Los datos se descargaron desde un repositorio abierto de movilidad urbana en formato GeoJSON (`rutas_trufis.geojson`). 
   - *¿Las Paradas?* Cochabamba tiene un sistema de paradas flexibles. El algoritmo asume analíticamente el inicio y el fin del vector del trufi (y sus vértices más cercanos a los museos) como "paradas lógicas". 
   - *¿El Mapa?* Para incorporarlos visualmente sin sobrecargar la pantalla, usamos la librería de mapas para inyectar vectores de color morado (rutas) y círculos naranjas (paradas).

2. **Comando de Terminal (Instalación):** 
   Ejecutar el script preparador para descargar los vectores geográficos desde GitHub:
   ```bash
   python setup_trufis.py
   ```

3. **Código de Ejecución en el Proyecto:**
   En `ui_ventana.py`, el sistema lee el archivo JSON descargado y utiliza los comandos de `folium` para inyectarlos como gráficos en el mapa interactivo:
```python
# Incorporación al mapa en ui_ventana.py
import folium

with open("rutas_trufis.geojson", "r", encoding="utf-8") as f:
    datos_trufis = json.load(f)

for elemento in datos_trufis["features"]:
    coord_puntos = elemento["geometry"]["coordinates"]
    
    # 1. Dibujando la ruta del micro (Línea Morada)
    folium.PolyLine(locations=lista_formateada, color='purple', weight=3, opacity=0.6).add_to(mapa_folium)
    
    # 2. Dibujando la parada del micro (Punto Naranja) en el inicio de la línea
    inicio_gps = [coord_puntos[0][1], coord_puntos[0][0]]
    folium.CircleMarker(
        location=inicio_gps, radius=4, color='orange',
        fill=True, fill_color='orange', fillOpacity=0.9,
        tooltip="Parada"
    ).add_to(mapa_folium)
```

---

### 2.3. Mapeo de Ubicaciones: Los Museos

1. **Justificación (Teoría):** 
   Para que el Algoritmo (la red neuronal de búsqueda) pueda calcular distancias, necesita conocer el punto A y el punto B exactos. En lugar de levantar y mantener una pesada base de datos externa (como un servidor de bases de datos) para datos que rara vez cambian, decidimos mapear y codificar de forma fija y estática la lista de museos como un diccionario global en el programa. Cada nombre de museo actúa como la llave, y su valor es una Tupla matemática con su latitud y longitud, previamente extraída con precisión.

2. **Comando de Terminal (Instalación):** 
   *No aplica.* Al ser una variable nativa del lenguaje Python alojada en el archivo de configuración del proyecto, no requiere instalaciones ni descargas.

3. **Código de Ejecución en el Proyecto:**
   Dentro del archivo `configuracion.py` se declara el diccionario, el cual luego es exportado y leído por la interfaz (`ui_ventana.py`) para generar las listas y los marcadores visuales:
```python
# Extracto en configuracion.py
MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    # ... (20 museos más) ...
    '[W] Museo de Historia Natural Alcide dOrbigny': (-17.373723, -66.153692)
}

# Extracto en ui_ventana.py donde se construyen los checkboxes dinámicamente
from configuracion import MUSEOS

for nombre_museo in MUSEOS.keys():
    item = QListWidgetItem(nombre_museo)
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(Qt.Unchecked)
    self.lista_interfaz_museos.addItem(item)
```

---

### 2.4. Definición Matemática y Lógica de los 3 Modos de Transporte

1. **Justificación (Teoría):** 
   Nuestra Inteligencia Artificial no asume que el turista se teletransporta. Para modelar la Noche de Museos con realismo físico y económico, definimos tres "Modos de Transporte" que interactúan con el Presupuesto y el Tiempo del usuario:
   - **Modo Pie (Peatón):** Se utiliza la Interfaz de Programación de Aplicaciones externa en su perfil peatonal. Ignora el tráfico y el sentido único de las calles vehiculares. Su costo monetario es `0.0 Bs`.
   - **Modo Auto (Taxi):** Llama al servidor en perfil vehicular. Está atado a un multiplicador de costo (taxímetro lógico de `5.0 Bs por kilómetro`).
   - **Modo Micro (Transporte Público):** Es la red híbrida más compleja. Implica medir la caminata del turista hacia la parada, el viaje en la ruta estática del archivo de vectores geográficos, y la caminata final. El pasaje es estático (`3 Bs`). Si tomar el micro es más lento o caro que simplemente ir a pie directo, la heurística descarta la opción "Micro".

2. **Comando de Terminal (Instalación):** 
   *No aplica.* Esta es lógica central del negocio puramente programada en Python mediante bloques condicionales (`if/elif`).

3. **Código de Ejecución en el Proyecto:**
   El motor físico en `agentes_ia.py` define una función interna `calcular_segmento` que se encarga de ramificar la lógica según el tipo de viaje que la IA esté evaluando en ese milisegundo:
```python
# Extracto de agentes_ia.py -> AgenteBuscador -> calcular_segmento()

if tipo_viaje == 'Pie':
    # El peatón consulta su propio servidor de rutas peatonales
    _, _, geom_p = obtener_ruta_vehiculo(coord_a, coord_b, perfil="peaton")
    precio_pasaje = 0.0

elif tipo_viaje == 'Auto':
    # El coche extrae la distancia del servidor driving y calcula el costo según taxímetro
    d_vehiculo, t_vehiculo, geom_vehiculo = obtener_ruta_vehiculo(coord_a, coord_b, perfil="driving")
    precio_pasaje = self.costo_coche * d_vehiculo

elif tipo_viaje == 'Micro':
    # Lógica de Matriz de Transporte para emparejar la línea del archivo de vectores geográficos
    info_ruta = MATRIZ_TRANSPORTE[nodo_a][nodo_b]
    id_linea = info_ruta['lineas_disponibles'][0]
    ruta_fisica = LINEAS_TRUFIS.get(id_linea)
    precio_pasaje = 3.0 # Tarifa única de trufi/micro
```

---

### 2.5. Arquitectura de Almacenamiento Caché (Peatonal y Taxi)

1. **Justificación (Teoría):** 
   ¿Por qué creamos cachés? El proveedor de calles físicas impone reglas estrictas para evitar saturación de servidores (límites de peticiones por segundo). Si la Inteligencia Artificial intentara calcular los millones de combinaciones de la Noche de Museos preguntando a internet por cada cruce, el programa tardaría días en responder y nuestra conexión sería bloqueada mundialmente.
   - *Solución:* Creamos dos bancos de memoria local (`cache_peatonal.json` y `cache_taxi.json`). Calculamos todas las rutas existentes entre todos los museos una sola vez. Cuando el usuario hace clic en "Calcular", el Agente ya no acude a internet; lee los archivos del disco duro y los carga en la Memoria de Acceso Aleatorio del sistema, haciendo que la Inteligencia Artificial resuelva la ruta perfecta en una fracción de segundo.

2. **Comando de Terminal (Instalación):** 
   Antes de abrir la interfaz por primera vez, el ingeniero debe popular (llenar) los cachés vacíos con este comando:
   ```bash
   python precalcular_rutas.py
   ```

3. **Código de Ejecución en el Proyecto:**
   El código extrae la información y luego usa un mecanismo de volcado inteligente con espaciado (`indent=4`) para que los archivos temporales no se encripten en una sola línea interminable, sino que sean fáciles de inspeccionar por un ser humano:
```python
# Extracto de configuracion.py -> guardar_memoria()
import json

def guardar_memoria(perfil="driving"):
    # Bifurcación entre Caché Peatonal y Caché de Taxi
    if perfil == 'peaton':
        with open("cache_peatonal.json", "w", encoding="utf-8") as archivo:
            # indent=4 formatea el archivo hacia abajo, haciéndolo legible
            json.dump(memoria_peaton, archivo, indent=4)
    else:
        with open("cache_taxi.json", "w", encoding="utf-8") as archivo:
            json.dump(memoria_taxi, archivo, indent=4)
```

---

### 2.6. Arquitectura Multi-Agente (Los 4 Agentes del Proyecto)

1. **Justificación (Teoría):** 
   Para evitar que la interfaz gráfica se congele o bloquee mientras la computadora piensa, el proyecto usa un sistema concurrente basado en "Agentes". Cada agente es un hilo de procesamiento independiente.
   - `AgenteBuscador`: El cerebro matemático. Explora millones de permutaciones en segundo plano.
   - `AnimadorMovimiento`: El motor físico. Calcula los fotogramas para mover el auto en el mapa de forma fluida.
   - `AgenteGuia`: Un temporizador estático que cobra la entrada y emite señales de espera mientras el usuario "visita" el museo.
   - `AgenteTransporte`: El coordinador maestro que ordena a los otros agentes cuándo actuar y dibuja las líneas visuales en el mapa interactivo.

2. **Comando de Terminal (Instalación):** 
   Al depender directamente del núcleo del framework Qt para el paralelismo seguro, basta con tener PyQt instalado:
   ```bash
   pip install PyQt5
   ```

3. **Código de Ejecución en el Proyecto:**
   En `agentes_ia.py`, los agentes se crean heredando de `QThread`. Se usan `pyqtSignal` para mandar mensajes hacia la ventana principal de manera segura.
```python
# Creación y configuración del Agente en agentes_ia.py
from PyQt5.QtCore import QThread, pyqtSignal

class AgenteBuscador(QThread):
    # Señales para comunicarse con la UI sin congelarla
    ruta_encontrada = pyqtSignal(list, float, float)
    mensaje_consola = pyqtSignal(str)

    def run(self):
        # Lógica de búsqueda principal en hilo secundario
        self.buscar_rutas_dfs(...)
        self.mensaje_consola.emit("Búsqueda finalizada con éxito.")
```

### 2.6.1. Clasificación Teórica de la Inteligencia Artificial (Taxonomía)

1. **Justificación (Teoría):** 
   Nuestra arquitectura no fue diseñada al azar por nuestro equipo. Está fundamentada estrictamente en la taxonomía clásica de la Inteligencia Artificial (basada en Russell y Norvig), que hemos adaptado a la geografía y dinámica de los museos de la ciudad de Cochabamba:
   - **Agente Reactivo Simple (`AgenteGuia`):** Toma decisiones basadas únicamente en la percepción del momento actual. Por ejemplo, si el turista llega a la puerta del "Convento Museo Santa Teresa", nuestro agente no recuerda si el turista vino en Trufi o caminando; simplemente reacciona, cobra la entrada de 15 Bs e inicia el temporizador de visita.
   - **Agente Reactivo Basado en Modelos (`AnimadorMovimiento`):** Desarrollamos este agente para que mantenga un estado interno sobre cómo es el mundo físico. Calcula de forma determinista dónde debe estar el ícono del vehículo en el siguiente fotograma para generar la ilusión de movimiento.
   - **Agente Basado en Objetivos (`AgenteTransporte`):** Le programamos la meta absoluta de guiar al turista desde su punto de origen hasta su destino final. Es el orquestador maestro que lee nuestra matriz de rutas de micros de Cochabamba y coordina los despachos del motor de animación.
   - **Agente Basado en Utilidad (`AgenteBuscador`):** La joya de nuestro proyecto. Su objetivo no es simplemente llegar a la "Casona de Santiváñez", sino que evalúa una función de *utilidad* y *poda algorítmica*. Compara miles de rutas descartando aquellas que sobrepasan el Presupuesto y el Tiempo para maximizar la recompensa del turista.

2. **Comando de Terminal (Instalación):** 
   *No aplica.* Esta clasificación es el pilar de la programación de las clases en `agentes_ia.py`.

3. **Código de Ejecución en el Proyecto (Implementación Real):**
   Las clases en `agentes_ia.py` contienen el código real que ejecuta estas teorías:

```python
# 1. AGENTE BASADO EN UTILIDAD (AgenteBuscador)
# Aplica la "Poda": Descarta la rama si la utilidad (Costo/Tiempo) supera las restricciones.
if costo_total_evaluado <= self.presupuesto_maximo and tiempo_total_evaluado <= self.tiempo_maximo:
    # Maximiza la recompensa guardando la ruta válida en la matriz
    rutas_encontradas.append({
        'numero_operacion': self.contador_exploracion,
        'cantidad_museos': len(camino_actual) - 1, # La utilidad máxima a conseguir
        'dinero_gastado': costo_total_evaluado
    })

# 2. AGENTE REACTIVO BASADO EN MODELOS (AnimadorMovimiento)
# Mantiene el modelo del mundo físico interpolando el espacio y tiempo (Física real)
fraccion = fotograma_actual / total_fotogramas
lat = lat_a + (lat_b - lat_a) * fraccion
lon = lon_a + (lon_b - lon_a) * fraccion
# Altera el entorno mandando la nueva coordenada a la Capa Visual
self.senal_coordenada.emit(lat, lon, modo_transporte)

# 3. AGENTE BASADO EN OBJETIVOS (AgenteTransporte)
# Cumple el objetivo principal delegando tareas y conectando eventos asíncronos.
def despachar_ruta(self):
    self.animador = AnimadorMovimiento(self.ruta['geometrias'], ...)
    # Si el animador llega al objetivo, el Agente Transporte toma el control de nuevo
    self.animador.senal_llegada.connect(self.procesar_llegada)
    self.animador.start()

# 4. AGENTE REACTIVO SIMPLE (AgenteGuia)
# Actúa sobre reglas simples Si-Entonces. Cobra entrada y restaura el control.
def run(self):
    tiempo_espera = self.duracion / self.multiplicador
    time.sleep(tiempo_espera) # Reacción: Detener a la persona en el museo
    self.senal_cobro.emit(self.costo_entrada) # Reacción: Cobrar dinero
    self.senal_fin.emit()
```

---

### 2.7. Motores de Búsqueda, Macro-Operadores y Poda Lógica

1. **Justificación (Teoría):** 
   Un **Macro-Operador** en IA es una abstracción que agrupa acciones complejas. Aquí, nuestro macro-operador es "Viajar del Museo A al B usando el mejor transporte". 
   - **Validación y Descartes (Poda):** El agente explora usando el algoritmo de **Búsqueda en Profundidad** (un método matemático para explorar todas las combinaciones posibles llegando hasta el final de cada camino). Si al intentar usar el macro-operador hacia el siguiente museo nota que el costo acumulado supera el Presupuesto, o el reloj rebasa el Tiempo Límite, se activa la "Poda" (el descarte inmediato de esa ruta). La rama se invalida y el agente retrocede sin seguir calculando rutas imposibles.
   - **Los Cachés (Recordatorio):** Toda la información requerida por los macro-operadores para calcular estas distancias instantáneamente se lee de los archivos locales `cache_peatonal.json` y `cache_taxi.json`. Sin ellos, la poda tardaría días en lugar de milisegundos.

2. **Comando de Terminal (Instalación):** 
   *No aplica.* Matemáticas de Árboles y Grafos puras.

3. **Código de Ejecución en el Proyecto:**
```python
# Lógica de Validación y Poda en agentes_ia.py -> AgenteBuscador
def dfs(nodo_actual, museos_faltantes, ruta_actual, tiempo_acumulado, costo_acumulado):
    # Validación (Descarte)
    if tiempo_acumulado > self.tiempo_disponible or costo_acumulado > self.presupuesto_disponible:
        self.mensaje_consola.emit(f"PODA: Límite excedido hacia {nodo_actual}")
        return # Finaliza esta rama inmediatamente
        
    # Continuación usando macro-operadores de transporte
    for sig_nodo in museos_faltantes:
        tramos = calcular_segmento(nodo_actual, sig_nodo...)
        # Evaluar recursivamente las siguientes combinaciones
```

---

### 2.8. Cinemática: Cálculos de Tiempo por Tramo

1. **Justificación (Teoría):** 
   ¿Cómo sabe la computadora cuánto tiempo demorará un auto en recorrer Cochabamba? A través de cinemática básica adaptada al espacio geográfico: **`Tiempo = Distancia / Velocidad`**. 
   La API nos devuelve la `Distancia` matemática real del tramo, y la interfaz gráfica le provee a la IA la `Velocidad` seleccionada por el usuario (ej. Caminando a 5 km/h, Coche a 40 km/h).

2. **Comando de Terminal (Instalación):** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
```python
# Fragmentos de cálculo de tiempo en agentes_ia.py
if tipo_viaje == 'Pie':
    # La API entrega la distancia_total_tramo en kilómetros
    # Se divide entre la velocidad del humano y se obtiene el tiempo en horas
    tiempo_total_tramo = distancia_total_tramo / self.velocidad_caminando

elif tipo_viaje == 'Auto':
    tiempo_total_tramo = distancia_total_tramo / self.velocidad_coche
```

---

### 2.9. Filtrado y Despliegue de Resultados (Historial de Rutas)

1. **Justificación (Teoría):** 
   Si el turista elige 10 museos pero solo tiene tiempo para 3, el sistema no falla. A medida que la Búsqueda en Profundidad avanza, inyecta su "Número de Operación" en las rutas que lograron cumplir los límites de presupuesto y tiempo.
   Al finalizar, el servidor extrae la cantidad máxima de museos alcanzada por la mejor ruta, y devuelve un **Historial Exhaustivo** a la pantalla ordenado cronológicamente según cómo fueron validados, mostrando el identificador de la operación para mantener un registro transparente.

2. **Comando de Terminal (Instalación):** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
   Este bloque inyecta la operación y devuelve los ganadores (Extracto de `agentes_ia.py`):
```python
# Lógica de Extracción Final en agentes_ia.py
rutas_encontradas.append({
    'numero_operacion': self.contador_exploracion,
    'nombre_ruta': " -> ".join([abreviar(x) for x in camino_actual[1:]]),
    'cantidad_museos': len(camino_actual) - 1,
    # ... otros metadatos
})

if rutas_encontradas:
    # 1. ¿Cuál es el récord de museos visitados?
    max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
    
    # 2. Rescatar solo las rutas que igualan el récord
    rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
    
    # 3. Enviar todo el historial a la interfaz en su orden original
    self.finalizado_senal.emit(rutas_validas)
```

---

## SECCIÓN III: MANUAL OPERATIVO PARA EL USUARIO DEL SIMULADOR

El simulador que hemos desarrollado, a pesar de tener toda la carga algorítmica y teórica expuesta previamente, dispone de una Interfaz de Usuario que nuestro equipo diseñó ergonómicamente. A continuación explicamos los pasos y lógica de uso:

### PASO 1: Ingreso de Variables Estructurales (Módulo Izquierdo)

1. **Justificación (Teoría):** 
   - **Posición Inicial:** El turista no puede ir a ningún museo si no hay punto de partida (Origen). Debe introducir el nombre de la plaza y oprimir el botón **Origen**. Si el sistema falla por no reconocer el nombre, el usuario puede simplemente hacer **clic** en el mapa de la derecha; este interactúa vía un puente de programación web y retorna las coordenadas directamente al programa local.
   - **Restricción Económica:** Todo trayecto resta dinero. Se debe asignar el presupuesto en Bolivianos.
   - **Restricción Temporal:** El evento tiene hora límite. Se ajusta el tiempo (en minutos).

2. **Comando de Terminal:** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
   Extracción de datos en `ui_ventana.py`:
```python
# Capturando los datos estructurales del turista
dinero_disponible = self.spin_presupuesto.value()
tiempo_disponible = self.spin_tiempo.value()

# Conexión del botón Origen
self.btn_origen.clicked.connect(self.buscar_origen)
```

### PASO 2: Configuración de Cinemática Física y Realidad Simulada

1. **Justificación (Teoría):** 
   - **Velocidad de Translación:** Ajuste mediante la caja numérica a qué velocidad avanza el peatón o el coche. 
   - **Duración de la Visita al Museo:** Lapso estático en minutos dentro de las exposiciones.
   - **Acelerador:** Multiplicador temporal. Un viaje real de 10 minutos puede correr fluidamente a lo largo de 60 segundos si elige aceleración x10.
   - **Modos de Transporte Permitidos:** Mediante tres casillas de verificación, usted decide qué vehículos usar (Pie, Taxi, Micro). Si deshabilita alguna opción, el sistema jamás recomendará usarla.

2. **Comando de Terminal:** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
```python
# Extrayendo la física desde la interfaz
vel_coche = self.spin_vel_coche.value()
vel_pie = self.spin_vel_pie.value()
acelerador = float(self.combo_acelerador.currentText().replace('x', ''))

# Verificando qué modos están habilitados
modos_permitidos = []
if self.check_pie.isChecked(): modos_permitidos.append('Pie')
if self.check_taxi.isChecked(): modos_permitidos.append('Auto')
if self.check_micro.isChecked(): modos_permitidos.append('Micro')
```

### PASO 3: Selección de Criterios (Los Museos)

1. **Justificación (Teoría):** 
   El simulador despliega una lista interactiva de los museos incorporados al evento. Active la **casilla de verificación** de cada lugar que su grupo quiera explorar. 
   *Advertencia algorítmica:* Seleccionar los 23 museos hará imposible que el simulador respete las variables temporales y de costo; el sistema desechará rutas imposibles automáticamente.

2. **Comando de Terminal:** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
   El código barre la lista visual y extrae solo las opciones que el usuario marcó:
```python
# Extrayendo los museos seleccionados
museos_seleccionados = []
for i in range(self.lista_interfaz_museos.count()):
    elemento = self.lista_interfaz_museos.item(i)
    if elemento.checkState() == Qt.Checked:
        museos_seleccionados.append(elemento.text())
```

### PASO 4: Compilación, Ejecución Matemática y Emulación

1. **Justificación (Teoría):** 
   - **Calcular:** Ejecuta la red neuronal matemática. Le enseñará qué trayectos descartó mediante poda para ahorrar sus recursos computacionales y de tiempo. Entregará en la caja inferior las únicas alternativas viables con instrucciones exactas.
   - **Iniciar:** El sistema deshabilitará todos los botones (para proteger los procesos matemáticos internos) y comenzará a mover el indicador sobre las calles bolivianas siguiendo la geometría real. El reloj interno y los contadores en la parte baja (`Presupuesto` y `Tiempo`) bajarán progresivamente hasta culminar.

2. **Comando de Terminal:** 
   *No aplica.*

3. **Código de Ejecución en el Proyecto:**
   Lanzamiento del Hilo Concurrente:
```python
# Bloqueo de interfaz e inicio del cálculo en segundo plano
self.btn_calcular.setEnabled(False)
self.btn_iniciar.setEnabled(False)

# Envío de parámetros al Agente
self.agente_buscador = AgenteBuscador(
    origen=self.origen, 
    museos=museos_seleccionados, 
    presupuesto=dinero_disponible, 
    #... etc
)
self.agente_buscador.start() # Inicia el Multithreading
```
