# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTIAGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

## CAPÍTULO I: PREPARACIÓN DEL ENTORNO Y DATOS BASE

### Instalación de Python
Para el desarrollo de este proyecto decidimos usar **Python 3**. Lo elegimos porque es un lenguaje fácil de leer, excelente para el manejo de datos, y porque tiene un sistema automático que limpia la memoria de la computadora sin que nosotros tengamos que programarlo a mano. 

Para que nuestro proyecto funcione correctamente y no choque con otros programas que tenga el usuario en su computadora, creamos un "Entorno Virtual de Trabajo". Un entorno virtual es una caja protectora. Dentro de esta caja, instalamos una copia aislada de Python y todas las herramientas de nuestro proyecto.
Para instalarlo y activarlo en la computadora, abrimos la consola y escribimos:
```bash
python -m venv venv
venv\Scripts\activate
```

### Instalación y Ejecución de Bibliotecas Externas como Nativas
No programamos todo desde cero. Usamos "Bibliotecas", que son paquetes de código que otras personas ya hicieron. Para este proyecto instalamos dos grupos de bibliotecas:

**1. Bibliotecas Externas (Se descargan de internet usando `pip install`):**
- `PyQt5`: La usamos para crear la ventana de nuestro programa (botones, cajas de texto, etc).
- `PyQtWebEngine`: Es un navegador de internet disfrazado de código. Nos sirve para cargar el mapa interactivo dentro de nuestra propia ventana sin abrir Google Chrome.
- `requests`: Nos permite conectar el programa a internet para pedir rutas a servidores mundiales.
- `polyline`: Es una herramienta matemática que descomprime la información de la ruta que nos manda internet.
- `folium` y `geopy`: Herramientas cartográficas. Nos permiten dibujar los marcadores rojos de los museos y encontrar la latitud y longitud.
```bash
pip install PyQt5 PyQtWebEngine folium requests polyline geopy
```

**2. Bibliotecas Nativas (Ya vienen dentro de Python, solo hay que usarlas):**
- `math`: La usamos para fórmulas de distancia, trigonometría y divisiones matemáticas.
- `itertools`: Para armar todas las combinaciones posibles de museos.
- `json`: Sirve para crear y leer archivos de texto guardados en la computadora (nuestra memoria).
- `time` y `os`: Para pausar la ejecución (así el autito del mapa se mueve poco a poco y no de golpe) y para leer carpetas de Windows.

### Ubicación de todos los museos, cómo los ingresamos en el proyecto
Ningún programa sabe dónde están los museos por arte de magia. Nuestro equipo buscó manualmente las coordenadas de latitud y longitud de los 23 museos de Cochabamba usando mapas por satélite. 
Para ingresar esta información a nuestro proyecto, usamos una estructura de Python llamada "Diccionario". En el archivo `configuracion.py`, programamos este diccionario. Esto es como un libro de contactos muy rápido donde el programa busca un museo y obtiene su ubicación al instante.

```python
# Extracto del archivo configuracion.py
MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    '[D] Museo Arqueológico UMSS': (-17.395278, -66.157394),
    '[E] Iglesia de la Compañía de Jesús': (-17.393023, -66.157814),
    # ... (Se ingresaron los 23 recintos culturales de Cochabamba)
}
```

### Scripts de Automatización: Descargas y Precálculo del Sistema
Al hacer un simulador masivo, no podíamos exigirle al usuario que consiga los mapas a mano. Por eso programamos dos archivos extra que automatizan el trabajo previo al inicio del programa:

**1. Descargador de Mapas (`setup_trufis.py`):** 
Este archivo utiliza la biblioteca nativa `urllib.request`. Su función es ir directamente a un enlace de GitHub de datos libres de Cochabamba, y descargar un mapa de 2.2 Megabytes con todas las líneas de transporte, guardándolo automáticamente en la carpeta del usuario.
```python
# Archivo setup_trufis.py
def descargar_rutas():
    archivo = "rutas_trufis.geojson"
    if not os.path.exists(archivo):
        url = "https://gist.githubusercontent.com/mauforonda/b094e77a0af814dba978f6ae564faa78/raw"
        urllib.request.urlretrieve(url, archivo)
```

**2. Precálculo de Rutas (`precalcular_rutas.py`):**
Para que la computadora no tarde mucho la primera vez que el usuario presione "Calcular", programamos este archivo de calentamiento. Lo que hace es cruzar los 23 museos entre sí y pedirle a internet TODAS las rutas por adelantado, obligando al sistema a generar la memoria guardada (Caché).
```python
# Extracto de precalcular_rutas.py
def generar_caches():
    nombres = list(MUSEOS.keys())
    total_museos = len(nombres)
    for i in range(total_museos):
        for j in range(total_museos):
            if i == j: continue
            origen = MUSEOS[nombres[i]]
            destino = MUSEOS[nombres[j]]
            
            # Forzamos la descarga y el guardado en Caché para Peatón y Auto
            obtener_ruta_vehiculo(origen, destino, perfil="peaton")
            obtener_ruta_vehiculo(origen, destino, perfil="driving")
```

---

## CAPÍTULO II: ARQUITECTURA DEL SISTEMA E INTERFAZ GRÁFICA

### Arquitectura del Sistema o Software
La arquitectura de nuestro programa sigue un diseño donde el "cerebro" está separado del "cuerpo". 
Por un lado, tenemos la **Interfaz Visual**, que es todo lo que el usuario ve y toca (los botones y el mapa). Y por otro lado, está el **Motor Lógico**, que es ciego a la pantalla y solo procesa números, coordenadas y rutas. Separarlos nos permite hacer simulaciones muy pesadas sin que la ventana de la pantalla se quede colgada o "no responda".

### Arranque del Sistema y Configuración del Bucle Principal
Todo sistema informático necesita un punto de inicio y un Bucle Principal (un ciclo que hace que la ventana no se cierre al instante).
Para ejecutar nuestro simulador, creamos el archivo principal `main.py`. Aquí configuramos la pantalla para que tenga buena resolución (HD), apagamos la aceleración gráfica del mapa para evitar errores de video en algunas computadoras, e iniciamos el "Bucle Principal" (`app.exec_()`), el cual se queda esperando eternamente a que el usuario haga clic en algún botón.

```python
# Archivo main.py (Arranque del sistema)
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_ventana import VentanaPrincipal

if __name__ == "__main__":
    # Desactivamos restricciones de aceleración de gráficos para que funcione en cualquier PC
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    aplicacion = QApplication(sys.argv)
    
    # Creamos la ventana y ejecutamos el Bucle Infinito del programa
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(aplicacion.exec_())
```

### Construcción de la Interfaz Visual con PyQt5
Toda la pantalla de nuestro proyecto está construida usando la biblioteca PyQt5 en el archivo `ui_ventana.py`. Lo que hicimos fue crear una ventana dividida en columnas. Usamos herramientas como `QSpinBox` (para que el usuario seleccione números para el tiempo y el dinero) y `QCheckBox` (para que elija qué transportes permite).
Además, enlazamos los botones a las acciones del código mediante la función `clicked.connect()`. Es decir, al hacer clic en "Calcular", le avisamos a la Inteligencia Artificial que empiece a buscar.

```python
# Extracto de ui_ventana.py (Creación visual de botones)
caja_botones = QHBoxLayout()

self.boton_calcular = QPushButton("Calcular")
self.boton_calcular.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
# Conectamos el botón para que despierte al motor de búsqueda
self.boton_calcular.clicked.connect(self.empezar_busqueda)

self.boton_reiniciar = QPushButton("Reiniciar")
self.boton_reiniciar.setStyleSheet("background-color: #F44336; color: white;")
self.boton_reiniciar.clicked.connect(self.reiniciar_todo)

caja_botones.addWidget(self.boton_calcular)
caja_botones.addWidget(self.boton_reiniciar)
```

### Renderizado de Mapas Dinámicos en Python
El mapa que ves a la derecha del programa no es una imagen estática. Lo construimos usando la herramienta `folium`, la cual genera un código en HTML y lo dibuja en nuestra ventana mediante el navegador interno de PyQt.
Para hacer que el "marcador" del autito se mueva por la calle sin tener que recargar el mapa (lo que daría parpadeos molestos), inyectamos un pequeño código de **JavaScript** dentro de Python. Este código empuja las coordenadas de la calle en vivo para que el autito ruede con una animación suave.

```python
# Inyección de JavaScript en Python (ui_ventana.py)
js_movimiento = """
<script>
    window.updateMovingMarker = function(lat, lon, color) {
        var latlng = [lat, lon];
        if (movingMarker) {
            movingMarker.setLatLng(latlng);
        } else {
            movingMarker = L.marker(latlng).addTo(mapInstance);
        }
    };
</script>
"""
mapa_folium.get_root().html.add_child(folium.Element(js_movimiento))
```

---

## CAPÍTULO III: MATEMÁTICAS, MAPAS Y TRANSPORTE

### Instalación, Ejecución e Implementación de OpenStreetMap
Para saber por qué calles debe ir el auto o el peatón, no podemos trazar una línea recta porque los edificios y las casas nos estorban. 
Por eso implementamos la base de datos libre más grande del mundo: **OpenStreetMap**. 
La ejecución de esta herramienta funciona así: Nuestro simulador envía una petición por la red al servidor mundial de OpenStreetMap entregando las coordenadas de origen y destino. El servidor nos responde entregándonos una línea perfecta, que respeta los semáforos, el sentido de las calles y los límites de la acera para peatones.

```python
# Conexión al servidor mundial de OpenStreetMap (en configuracion.py)
url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"

try:
    respuesta = requests.get(url, headers={"User-Agent": "NocheMuseosSimulador/1.0"}, timeout=5)
    datos = respuesta.json()
    if datos.get('code') == 'Ok':
        # Extracción de la distancia en kilómetros
        distancia_kilos = datos['routes'][0]['distance'] / 1000.0
        # polyline.decode descomprime la ruta de la calle
        puntos_ruta = polyline.decode(datos['routes'][0]['geometry'])
except Exception:
    pass
```

### Cómo se consigue las métricas de medida y distancia, y cómo se calcula
Para saber la distancia en metros de un punto "A" a un punto "B" en el mapa, no podemos medirlo plano porque la Tierra es una esfera. 
La forma en la que calculamos esto es implementando la **Fórmula Matemática de Haversine** en nuestro código. Esta fórmula toma la latitud, la longitud y la curva de la Tierra (basada en el radio promedio de la Tierra de 6371 kilómetros). Así, nuestro programa consigue saber la distancia real que existe en la calle.

```python
# Función matemática en configuracion.py
def calcular_distancia_directa(origen, destino):
    radio_tierra = 6371.0 # Kilómetros
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

### Instalación e Implementación de Cálculo de Tiempo por Tramo
Una vez que nuestra fórmula matemática nos devuelve la distancia real, saber el tiempo es muy simple: usamos la ley física que dice que el Tiempo es igual a la Distancia dividida por la Velocidad (`t = d / v`).
En nuestro simulador, el usuario puede seleccionar a qué velocidad caminará y a qué velocidad viajará el auto. El programa simplemente divide la distancia obtenida de OpenStreetMap entre la velocidad que seleccionó el usuario para saber con exactitud cuántos minutos durará el viaje de una calle a otra.

```python
# Extracto del código lógico de física de movimiento (agentes_ia.py)
velocidad_actual = self.velocidad_auto if modo == 'Auto' else self.velocidad_pie

# Tiempo = (Distancia / Velocidad) * 60 minutos
tiempo_horas = distancia_kilos / velocidad_actual
tiempo_minutos = tiempo_horas * 60
```

### Cómo calculamos todas las rutas de movimiento para autos y el peatón
Cuando el usuario intenta ir del Museo A al Museo B en auto o caminando, el programa manda una alerta al servidor de OpenStreetMap solicitando el perfil de viaje. Si elegimos peatón, el servidor nos devuelve calles peatonales y parques. Si elegimos auto, nos devuelve calles para vehículos. Si la computadora no tiene internet en ese momento, el programa implementa un "plan de emergencia", dibujando una línea recta de pájaro y multiplicando la distancia por un pequeño margen de error para que la simulación no se detenga.

```python
# Plan de Emergencia si falla OpenStreetMap (configuracion.py)
except Exception as e:
    # Si falla la red, forzamos una línea recta directa con un 30% extra de penalización por curvas
    distancia_kilos = calcular_distancia_directa(origen, destino) * 1.3
    tiempo_minutos = (distancia_kilos / 20.0) * 60
    puntos_ruta = [origen, destino]
    
    return distancia_kilos, tiempo_minutos, puntos_ruta
```

### Los modos de transporte, cómo los implementamos e instalamos
El simulador incorpora tres modos principales:
1. **Peatonal:** Implementado para poder ir caminando por las aceras de cualquier parte.
2. **Auto / Taxi:** Implementado para pedir un taxi libre que nos lleve de puerta a puerta usando el presupuesto en Bolívianos.
3. **Transporte Público (Micro y Trufi):** Este es diferente, porque los micros no se salen de su ruta. Lo implementamos leyendo las rutas físicas reales de Cochabamba para que el usuario pueda tomar micros en los cruces.

```python
# Interfaz de Modos de Transporte (ui_ventana.py)
self.check_pie = QCheckBox("Pie")
self.check_taxi = QCheckBox("Taxi")
self.check_micro = QCheckBox("Micro")

# El usuario decide qué algoritmos instalar en la memoria
permitir_pie = self.check_pie.isChecked()
permitir_taxi = self.check_taxi.isChecked()
```

### Rutas del transporte público y paradas (Cómo se instaló y de dónde lo conseguimos)
Para los Micros, conseguimos un archivo de datos libres llamado `rutas_trufis.geojson` que contiene dibujadas todas las rutas del transporte público de Cochabamba.
Lo instalamos integrándolo al archivo `configuracion.py`. Para calcular las paradas, hicimos un pequeño radar. El programa analiza todas las líneas de transporte y verifica qué calles están a una distancia menor a 400 metros de la puerta del museo. Si hay una calle cerca de la ruta del micro, la marca como una "Parada Matemática" permitiendo que el turista camine hasta ahí y suba al transporte.

```python
# Lógica del Radar de 400 metros para encontrar paradas en configuracion.py
# Análisis para encontrar Paradas cerca del Museo
paradas_cercanas = {nodo: set() for nodo in nodos_ciudad}

for nombre_nodo, coordenada_nodo in nodos_ciudad.items():
    for identificador_linea, ruta_linea in diccionario_lineas.items():
        for punto_ruta in ruta_linea:
            distancia_a_calle = calcular_distancia_directa(coordenada_nodo, punto_ruta)
            
            # Si el micro pasa a menos de 400 metros (0.4 km) del Museo, creamos una Parada
            if distancia_a_calle < 0.4:
                paradas_cercanas[nombre_nodo].add(identificador_linea)
                break
```

---

## CAPÍTULO IV: OPTIMIZACIÓN, BÚSQUEDA Y CACHÉ

### Instalación e Implementación de Motores de Búsqueda
Para hallar el mejor recorrido de la "Noche de Museos", usamos Inteligencia Artificial creando un Motor de Búsqueda de **Profundidad**.
Funciona explorando un camino por completo hasta el final (por ejemplo: Origen -> Museo A -> Museo B -> Origen). Si se da cuenta que sobró mucho dinero, la inteligencia "retrocede un paso" y se va por otra rama diferente probando (Museo A -> Museo C -> Museo B). De esta forma explora todas las posibilidades sin perderse.

```python
# Búsqueda en Profundidad Recursiva (agentes_ia.py)
for i, museo_destino in enumerate(museos_faltantes):
    # Generamos los cálculos para el museo escogido
    # ...
    
    # LA RECURSIÓN: El Motor se llama a sí mismo para avanzar al siguiente nivel de profundidad
    explorar_opciones(
        camino_actual + [{'destino': museo_destino}],
        museos_faltantes[:i] + museos_faltantes[i+1:], 
        nuevo_gasto, 
        nuevo_reloj
    )
```

### Instalación e Implementación de Poda
Si el usuario selecciona 10 museos, hay millones de combinaciones para recorrerlos. Sería imposible calcularlos todos a tiempo.
Por eso implementamos la **Poda**. La Poda es una regla en el código que evalúa constantemente el viaje. Si a mitad del recorrido el costo ya es más de 100 Bolivianos, y el usuario solo tiene 50, la Poda "corta" de inmediato ese camino y aborta su revisión futura. Esto evita que la computadora pierda tiempo analizando un camino que ya de por sí no es válido.

```python
# Poda implementada en agentes_ia.py
def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado...):
    
    # 1. Condición de Poda Algorítmica: Si nos pasamos de plata o tiempo, cortamos aquí mismo.
    if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
        m = len(museos_faltantes)
        # 2. Análisis Matemático para saber cuántos millones de caminos nos ahorramos de buscar
        ramas_cortadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
        self.contador_exploracion += ramas_cortadas
        
        # 3. Aborto Inmediato del proceso
        return
```

### Instalación e Implementación de Filtrado y Despliegue de Resultados
Después de hacer la Búsqueda y la Poda, sobreviven varias rutas que sí alcanzan en el presupuesto de dinero y de tiempo.
El programa las pasa por un Filtro Final. El Filtro Final cuenta cuántos museos visitó cada una de estas opciones ganadoras y elimina las más cortas. Como resultado final, solo despliega en la lista de la pantalla las opciones que visitaron la cantidad máxima absoluta de recintos culturales posibles con el dinero que tenías.

```python
# Filtrado de resultados finales (agentes_ia.py)
if rutas_validas:
    # 1. Encontrar el récord máximo de museos visitados
    max_museos = max(ruta['cantidad_museos'] for ruta in rutas_validas)
    
    # 2. Filtrar y eliminar cualquier ruta que no haya llegado a ese récord
    mejores_rutas = [ruta for ruta in rutas_validas if ruta['cantidad_museos'] == max_museos]
    
    # 3. Emitimos solo a los campeones
    self.finalizado_senal.emit(mejores_rutas)
```

### Cómo desarrollamos e implementamos el Caché para las rutas del peatón y en taxi
Si en cada milímetro que explora el Motor de Búsqueda nos conectáramos a OpenStreetMap, demoraríamos años y nos bloquearían el internet.
Para arreglar esto, creamos un Sistema de **Caché** (Una Memoria Guardada). El sistema crea un archivo de texto en la computadora llamado `cache_peatonal.json`. Cada vez que descubrimos una calle nueva, la escribimos en ese archivo para que nunca más la volvamos a descargar. Cuando la inteligencia busca de nuevo esa calle, va primero al Caché, lo cual es milésimas de segundo más rápido que pedirla al internet.

```python
# Sistema de Memoria Caché en configuracion.py
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    # ÉXITO: La ruta ya estaba guardada en el disco local de nuestra computadora
    if llave in memoria_activa:
        datos = memoria_activa[llave]
        return datos[0], datos[1], datos[2]
        
    # FALLO: La ruta es nueva, debemos conectarnos a OpenStreetMap
    url = f"..."
    # [...]
    
    # Compensación de Espacio y Tiempo: Guardamos lo que trajimos para el futuro
    memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
    guardar_memoria(perfil)
```

### Instalación e Implementación de Macrooperadores
Cuando una persona usa un micro en la vida real, tiene que hacer tres cosas: 1) Caminar a la parada, 2) Viajar en el transporte, y 3) Caminar hasta la puerta del Museo.
Para la computadora, hacer 3 cosas separadas confunde la inteligencia artificial. Por eso construimos e implementamos un **Macrooperador**. Un macrooperador es una función de código que junta esas 3 cosas y las empaqueta en un solo "Movimiento de Viaje". Esto hace que la computadora planifique muchísimo más rápido.

```python
# Extracto del Macrooperador en agentes_ia.py
elif tipo_viaje == 'Micro':
    # ... código de búsqueda de paradas
    
    # El Macrooperador inserta 3 acciones físicas como si fueran una sola pieza unificada
    segmentos.extend([
        {'origen': nodo_a, 'destino': f'Parada', 'modo': 'Pie', 'geometria': caminata_1, 'costo': 0.0},
        {'origen': f'Parada', 'destino': f'Parada', 'modo': 'Micro', 'geometria': micro, 'costo': pasaje},
        {'origen': f'Parada', 'destino': nodo_b, 'modo': 'Pie', 'geometria': caminata_2, 'costo': 0.0}
    ])
```

### Cómo creamos el caché para optimizar las operaciones de macrooperadores
El Macrooperador, al tener que combinar caminata y microbús, necesita saber las calles peatonales. Para armarse de manera ultrarrápida sin tener que ir a OpenStreetMap, le ordenamos al Macrooperador que alimente sus líneas de caminata directamente desde el Caché Peatonal (`cache_peatonal.json`) que habíamos inventado antes. Así logramos que calcular un viaje en micro tome prácticamente cero segundos.

---

## CAPÍTULO V: ARQUITECTURA MULTIAGENTE Y TAXONOMÍA

En Ciencias de la Computación, un Agente Inteligente es un pequeño bloque de código o "robot virtual" que toma sus propias decisiones y no depende del resto del programa. En nuestro sistema implementamos 4 Agentes trabajando en equipo.

### Arquitectura Multiagente y Taxonomía (Los agentes explicados de forma sencilla)
1. **Agentes Reactivos Simples (El Agente Guía):** Es un robot que solo reacciona a su presente inmediato. En nuestro proyecto, es el Guía que te espera en el museo. No sabe de dónde vienes. Su única función es reaccionar si llegas a su puerta, cobrarte el dinero de la entrada y detener el reloj durante la visita.
2. **Agentes Reactivos Basados en Modelos (El Agente Animador Físico):** Es un robot que entiende cómo funciona la física y el movimiento en el mundo real. En el simulador, se encarga de recibir las coordenadas del GPS y dibujar cuadro por cuadro al auto deslizándose por la carretera respetando las leyes de velocidad y tiempo.
3. **Agentes Basados en Objetivos (El Agente de Transporte):** Este robot tiene una meta clara y es capaz de coordinar los pasos para lograrla. Es el agente que dirige al animador físico y le dice qué calles tomar y cuándo detenerse, asegurándose de que la ruta final se cumpla museo tras museo sin desvíos.
4. **Agentes Basados en Utilidad (El Agente Buscador Supremo):** El más inteligente de todos. No solo sabe llegar a la meta, sino que escoge el camino que dé más beneficio o "Utilidad". Este agente es el encargado de correr el motor de búsqueda, aplicar la poda matemática, comparar las rutas válidas y decidir cuál es la ruta que ahorra más tiempo y da mayor cantidad de museos.

```python
# Estructura de Clases para los 4 Agentes Multiagente
class AgenteBuscador(QThread):
    # Agente de Utilidad (Búsqueda A* y Poda)
    pass

class AgenteTransporte(QObject):
    # Agente de Objetivos (Sigue la ruta designada)
    pass

class AgenteGuia:
    # Agente Reactivo (Cobra entradas y hace esperar en el museo)
    pass
    
class AnimadorMovimiento(QThread):
    # Agente Basado en Modelos Físicos (Mueve el marcador según el GPS)
    pass
```

### Comunicación entre Agentes y la Interfaz Gráfica
¿Cómo puede el Agente seguir buscando rutas pesadas durante un minuto sin que la ventana de la computadora "se cuelgue"? 
Esto lo logramos instalando "Hilos en Segundo Plano" (`QThread`). Metimos a los Agentes de Búsqueda y de Movimiento en sus propios carriles paralelos de trabajo, separados de la Interfaz Visual. Para poder comunicarse entre ellos, usan un sistema llamado "Señales" (`pyqtSignal`). Los agentes lanzan una señal, y la interfaz la recibe para actualizar el mapa y la barra de dinero sin bloquearse ni congelar la PC.

```python
# Instalación de Señales e Hilos (agentes_ia.py)
class AgenteBuscador(QThread):
    # Declaración de las Señales (Cables de comunicación a la pantalla principal)
    progreso_senal = pyqtSignal(str)
    finalizado_senal = pyqtSignal(list)
    
    def run(self):
        # ... El agente de IA realiza su búsqueda matemática gigante y luego emite los resultados ...
        self.finalizado_senal.emit(rutas_validas)
```

---

## CAPÍTULO VI: MANUAL OPERATIVO COMPLETO PARA EL USUARIO DEL SIMULADOR

Para utilizar y maniobrar el software "Noche de Museos Cochabamba", siga cuidadosamente estos pasos de control:

1. **Definir el Origen y Recursos:** En la parte izquierda de la pantalla, encontrará la sección "Origen y Presupuesto". Escriba su ubicación inicial o haga Clic en cualquier parte del mapa visual. Debajo, ingrese el Presupuesto (Dinero en Bolivianos) y el Tiempo libre (En minutos) que tiene para todo el recorrido en la noche.
2. **Definir las Velocidades:** En el panel "Simulación", escriba a qué velocidad de kilómetros por hora caminará usted y a qué velocidad viaja en auto. Elija también un nivel en el botón "Acelerar Simulación" (Ej. x10 o x20) para que la animación del auto en el mapa sea rápida y su vista se sienta fluida.
3. **Restricciones de Transporte:** Si no desea ir en algún medio de transporte, puede desmarcar las casillas "Pie, Taxi, Micro" para que el buscador ignore ese modo de viaje.
4. **Seleccionar los Museos de Interés:** Marque con un "Visto Bueno" las casillas de los museos de la lista que usted tiene planeado visitar. Puede seleccionar desde 2 hasta todos los museos de la ciudad.
5. **Generar Cálculo Inteligente:** Presione el botón azul "Calcular". El sistema mostrará en la consola de texto oscura cómo la inteligencia se conecta a OpenStreetMap, explora la ciudad, "Poda" las rutas que exceden sus límites y analiza todo en tiempo récord.
6. **Iniciar el Recorrido Visual en Mapa:** Si la computadora encuentra alternativas exitosas, las colocará en la pequeña lista de abajo y se habilitará el botón verde "Iniciar". 
   Seleccione una ruta de la lista y haga clic en **Iniciar** para observar en tiempo real cómo el marcador virtual se desliza calle por calle en el mapa derecho, visitando cada museo paso a paso, dibujando líneas de color rojo (Auto), punteadas (A Pie) o moradas (Micros) mientras la cantidad de dinero y tiempo bajan en vivo en el sistema de caja registradora de la parte superior.
