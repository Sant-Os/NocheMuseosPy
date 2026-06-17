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

### 3. Instalación, Ejecución e Implementación de OpenStreetMap
Para calcular las trayectorias de movimiento real de las entidades (ya sean peatones o vehículos), no es factible utilizar distancias en línea recta de forma exclusiva, debido a la infraestructura urbana y restricciones viales (sentidos de vía, bloqueos, parques).
Por lo tanto, instalamos e implementamos una conexión en red con el servidor de la "Máquina de Enrutamiento de Código Abierto" respaldada por la gigantesca base de datos mundial de **OpenStreetMap** (OSRM). 

**Implementación técnica:**
El software emite una petición (Request) al puerto API de OpenStreetMap entregando el perfil de transporte (peatón o auto) junto a la latitud y longitud geométrica exacta del origen y el destino. El servidor remoto analiza el grafo de la ciudad de Cochabamba y responde entregando una "Polilínea", la cual es un arreglo masivo de puntos GPS que dibuja una línea a través del asfalto de las calles evadiendo las edificaciones.

```python
# Extracto del código base de conectividad OSRM (configuracion.py)
import requests
import polyline

# Se arma la petición HTTP para el servidor de OpenStreetMap
url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"

try:
    # Solicitamos la geometría real de la calle, con un tiempo de espera límite (timeout) de 5 segundos
    respuesta = requests.get(url, headers={"User-Agent": "NocheMuseosSimulador/1.0"}, timeout=5)
    datos = respuesta.json()
    
    if datos.get('code') == 'Ok':
        # Desempaquetamos la distancia métrica otorgada por el servidor y la pasamos a Kilómetros
        distancia_kilos = datos['routes'][0]['distance'] / 1000.0
        
        # Descomprimimos la Polilínea cifrada en un array explícito de Coordenadas de trazado de asfalto
        puntos_ruta = polyline.decode(datos['routes'][0]['geometry'])
except Exception as e:
    pass
```

### 4. Cómo se consigue las métricas de medida y distancia. Y cómo se calcula
Cuando las distancias requeridas no provienen del ruteador de OpenStreetMap (por ejemplo, para hallar cuál es la parada del microbús más cercana), es absolutamente necesario calcular la distancia geométrica real entre dos puntos en la faz de la tierra. Dado que el planeta es un objeto esférico tridimensional, el cálculo tradicional en un plano 2D (Teorema de Pitágoras) resulta en mediciones incorrectas a nivel de geolocalización.
Para solucionar esto, implementamos matemáticamente la **Fórmula del Haversine**, que calcula distancias "geodésicas" respetando la curvatura de la Tierra, fijando el radio orbital del planeta en 6371 kilómetros constantes.

```python
import math

def calcular_distancia_directa(origen, destino):
    """Calcula la distancia geodésica exacta entre dos puntos considerando la curva terrestre."""
    radio_tierra = 6371.0  # El radio estándar volumétrico de la Tierra en Kilómetros

    # Convertir grados de latitud/longitud decimal a Radianes trigonométricos
    latitud_1 = math.radians(origen[0])
    longitud_1 = math.radians(origen[1])
    latitud_2 = math.radians(destino[0])
    longitud_2 = math.radians(destino[1])
    
    delta_latitud = latitud_2 - latitud_1
    delta_longitud = longitud_2 - longitud_1
    
    # Ecuación central de la Trigonometría Esférica de Haversine
    a = math.sin(delta_latitud / 2)**2 + math.cos(latitud_1) * math.cos(latitud_2) * math.sin(delta_longitud / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Retorna la magnitud de distancia multiplicando el ángulo por el radio planetario
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
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_ventana import VentanaPrincipal

if __name__ == "__main__":
    # Desactivamos restricciones en tarjetas gráficas para maximizar compatibilidad en PCs genéricas
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    aplicacion = QApplication(sys.argv)
    
    # Inicialización del Componente Visual y Arranque del Bucle de Escucha Permanente (Main Loop)
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(aplicacion.exec_())
```

### 6. Arquitectura Multiagente y Taxonomía
El ecosistema completo del simulador funciona gracias a la Inteligencia Artificial distribuida a través de "Agentes". En términos algorítmicos computacionales, un agente inteligente es una pequeña entidad programática independiente que es capaz de percibir su entorno, deliberar y ejecutar acciones buscando cumplir un objetivo sin requerir supervisión del núcleo. Hemos diseñado e implementado 4 jerarquías de la taxonomía de agentes (basado en Russell y Norvig):

1. **Agentes Reactivos Simples (`AgenteGuia`):** 
Su arquitectura no contempla memoria histórica ni de planificación a futuro. Opera puramente mediante un conjunto de reglas Condición-Acción. El Agente Guía percibe si el vehículo llegó a la coordenada del museo. Si es así, su acción es retener al usuario, consumiendo el presupuesto designado para la entrada del museo y restando el tiempo de estadía acordado. Una vez finalizado el estímulo, se apaga.

```python
class AgenteGuia:
    def __init__(self, ui_principal, funcion_reloj, funcion_plata, minutos_visita):
        self.interfaz = ui_principal
        self.restar_reloj = funcion_reloj 
        self.restar_plata = funcion_plata
        self.minutos_visita = minutos_visita
        self.animacion = None

    def aterrizaje(self, nombre_edificio, funcion_continuar):
        if nombre_edificio == 'Origen':
            # ... (Lógica de fin de tour en la UI) ...
            self.interfaz.consola_registros.append("[Guía] Fin del tour.")
            self.interfaz.boton_calcular.setEnabled(True)
            funcion_continuar()
            return

        precio_boleto = ENTRADAS.get(nombre_edificio, 0)
        if precio_boleto > 0:
            self.restar_plata(precio_boleto, f"entrada a {nombre_edificio}")
            
        self.interfaz.consola_registros.append(f"[Guía] Explorando {nombre_edificio}...")
        multiplicador_aceleracion = int(self.interfaz.combo_acelerador.currentText().replace("x", ""))
        self.animacion = ControladorTurista(self.minutos_visita, multiplicador_aceleracion)
        self.animacion.senal_reloj.connect(self.interfaz.restar_minutos)
        
        def al_salir():
            self.interfaz.consola_registros.append(f"[Guía] Saliendo de {nombre_edificio}.")
            nombre_limpio = nombre_edificio.replace("'", "\\'")
            self.interfaz.visor_web.page().runJavaScript(f"if(window.updateMuseumMarker) updateMuseumMarker('{nombre_limpio}', 'green');")
            funcion_continuar()
            
        self.animacion.senal_salida.connect(al_salir)
        self.animacion.start()
```

2. **Agentes Reactivos Basados en Modelos (`AnimadorMovimiento`):**
Contiene una representación interna del mundo físico. A diferencia del agente simple, este agente reconoce variables físicas complejas como tasas de interpolación espacial y cinemática en cuadros por segundo. Su tarea es ingerir una polilínea GPS cruda, y dibujar el marcador sobre las calles en la pantalla usando un cálculo de desplazamientos proporcionales, ajustándose según el acelerador simulado x10, x20, etc.

```python
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

3. **Agentes Basados en Objetivos (`AgenteTransporte`):**
Posee la meta general. Su trabajo no es buscar cómo llegar, sino asegurar la ejecución metódica de los hitos del plan global. Este agente recibe el itinerario pre-calculado ganador, y delega instrucciones seriales y ordenadas al agente físico de movimiento, cerciorándose de que cada museo y parada en el plan de transporte se concluya estrictamente en el orden asignado.

```python
class AgenteTransporte:
    def __init__(self, consola_ui, web_ui, funcion_dinero, funcion_tiempo):
        self.consola = consola_ui
        self.visor_mapa = web_ui
        self.restar_plata = funcion_dinero
        self.restar_reloj = funcion_tiempo
        self.ruta_actual = None
        self.indice_tramo = 0
        self.animacion = None
        
    def arrancar_motor(self, datos_ruta, velocidad_coche, velocidad_caminando, acelerador, funcion_llegada):
        if self.animacion and self.animacion.isRunning():
            self.animacion.activo = False
            self.animacion.wait()
        self.ruta_actual = datos_ruta
        self.indice_tramo = 0
        self.evento_llegada = funcion_llegada
        self.siguiente_movimiento(velocidad_coche, velocidad_caminando, acelerador)
        
    def siguiente_movimiento(self, velocidad_coche=None, velocidad_caminando=None, acelerador=None):
        if self.ruta_actual and self.indice_tramo < len(self.ruta_actual['geometrias']):
            segmento = self.ruta_actual['geometrias'][self.indice_tramo]
            
            costo_monetario = segmento.get('costo', 0)
            if costo_monetario > 0:
                self.restar_plata(costo_monetario, f"boleto de {segmento['modo']}")
                
            self.animacion = AnimadorMovimiento([segmento], velocidad_coche, velocidad_caminando, acelerador)
            self.animacion.senal_coordenada.connect(self.refrescar_pantalla)
            self.animacion.senal_reloj.connect(self.restar_reloj)
            self.animacion.senal_llegada.connect(self.aterrizaje)
            self.animacion.start()
            
            self.velocidad_coche = velocidad_coche
            self.velocidad_caminando = velocidad_caminando
            self.acelerador = acelerador
        else:
            self.consola.append("[Vehículo] Destino final alcanzado.")

    def refrescar_pantalla(self, latitud, longitud, transporte):
        color_icono = 'red' if transporte == 'Auto' else 'orange' if transporte == 'Pie' else 'purple'
        self.visor_mapa.page().runJavaScript(f"if(window.updateMovingMarker) updateMovingMarker({latitud}, {longitud}, '{color_icono}');")

    def aterrizaje(self, nombre_destino):
        self.indice_tramo += 1
        self.evento_llegada(nombre_destino, lambda: self.siguiente_movimiento(self.velocidad_coche, self.velocidad_caminando, self.acelerador))
```

4. **Agentes Basados en Utilidad (`AgenteBuscador`):**
La clase máxima de inteligencia implementada. Mientras un agente de objetivos se conforma con simplemente completar una ruta, el Agente Buscador explora todas las formas factibles de completarla. Mide matemáticamente la satisfacción (o "Utilidad") de cada ruta posible, ponderando el balance óptimo entre cantidad de museos visitados, consumo de minutos y pérdida de capital económico. Elige unilateralmente el plan superior para dárselo al Agente de Transporte.

```python
class AgenteBuscador(QThread):
    progreso_senal = pyqtSignal(str)
    finalizado_senal = pyqtSignal(list)
    error_senal = pyqtSignal(str)
    
    def __init__(self, origen, museos, presupuesto, tiempo, vel_auto, vel_pie, tiempo_museo, permitir_pie=True, permitir_taxi=True, permitir_micro=True):
        super().__init__()
        self.coordenada_origen = origen
        self.lista_museos = museos
        self.presupuesto_maximo = presupuesto
        self.tiempo_maximo = tiempo
        self.velocidad_coche = vel_auto / 60.0
        self.velocidad_caminando = vel_pie / 60.0
        self.duracion_visita = tiempo_museo
        self.costo_coche = 5.0
        self.costo_caminar = 0.0
        self.permitir_pie = permitir_pie
        self.permitir_taxi = permitir_taxi
        self.permitir_micro = permitir_micro

    def run(self):
        try:
            # (El código gigante de "explorar_opciones" del motor de búsqueda DFS 
            # se detalla por separado más adelante en el Punto 13 y Punto 15).
            if self.permitir_pie:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Pie')
            if self.permitir_taxi:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Auto')
            if self.permitir_micro:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Micro')
                
            if rutas_encontradas:
                max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
                rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
                self.finalizado_senal.emit(rutas_validas)
            else:
                self.finalizado_senal.emit([])
        except Exception as error_capturado:
            self.error_senal.emit(str(error_capturado))
```

### 7. Rutas del transporte público y paradas, tramos y paradas
La simulación de autobuses de transporte público masivo reviste de un desafío particular superior al del transporte libre de un taxi. El transporte público carece de recojo de puerta a puerta y requiere aproximarse obligatoriamente a intersecciones que formen parte integral de sus recorridos.

**De dónde lo conseguimos y cómo se instaló:**
Desarrollamos un subsistema `setup_trufis.py` encargado de descargar un archivo georreferenciado cartográfico en formato abierto (`rutas_trufis.geojson`) proveniente de una base de datos pública del mapeo del transporte de Cochabamba (2.2 Megabytes de polígonos y líneas vehiculares).

Para implementar las "paradas", el sistema ejecuta un proceso de cruce geospacial de proximidad ("Radar"). El algoritmo carga en memoria todos los puntos geométricos del recorrido de las líneas de buses existentes, y realiza un chequeo contra cada uno de los 23 recintos de museos. Si un vértice callejero del microbús colisiona con el área de cobertura del museo (fijada estrictamente en un radio menor a 400 metros de distancia), ese vértice del asfalto se categoriza internamente en la estructura de datos como una "Parada Matemática Válida" desde la cual un Peatón puede hacer interconexión intermodal hacia el museo.

```python
# Lógica de escáner geoespacial para la detección de intersecciones de Parada de Micro (configuracion.py)
paradas_cercanas = {nodo: set() for nodo in nodos_ciudad}

# Bucle O(N*M) que cruza cada museo contra todos los puntos cartográficos de las líneas
for nombre_nodo, coordenada_nodo in nodos_ciudad.items():
    for identificador_linea, ruta_linea in diccionario_lineas.items():
        for punto_ruta in ruta_linea:
            
            # Cálculo directo de la distancia del vértice al edificio del museo
            distancia_a_calle = calcular_distancia_directa(coordenada_nodo, punto_ruta)
            
            # Tolerancia de proximidad: Si la línea pasa a menos de 400 metros (0.4 km) es una parada factible
            if distancia_a_calle < 0.4:
                paradas_cercanas[nombre_nodo].add(identificador_linea)
                break
```

### 8. Cómo desarrollamos e implementamos el Caché para las rutas del peatón y en taxi
La exploración profunda de un sistema de Inteligencia Artificial implica medir combinaciones de distancias que fácilmente superan las 10,000 operaciones por segundo. Si cada una de esas mediciones generase una solicitud remota al servidor OSRM (OpenStreetMap), colapsaríamos el ancho de banda del proyecto, sufriendo bloqueos permanentes de firewall y latencias inoperantes.

Desarrollamos una política de persistencia de "Caché Dual" de Espacio/Tiempo. 
El software aloja en su directorio raíz dos repositorios locales JSON (`cache_peatonal.json` y `cache_taxi.json`). Cuando el Agente Buscador consulta la latitud A a la longitud B, el sistema actúa como un proxy. Primero realiza un barrido de búsqueda "Llave-Valor" en su Caché en Disco. Si halla una coincidencia, obtiene la distancia, la ruta y el tiempo en 0.001 segundos y aborta la petición a internet. De lo contrario, solicita el trazado al servidor OSRM mundial y, acto seguido, guarda obligatoriamente dicha trayectoria en su Caché interno para solventar peticiones colindantes futuras.

```python
# Sistema de retención e inyección proxy de Caché Dual (configuracion.py)
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    # Firma criptográfica visual de la ruta (Ejemplo: "driving|-17.3,-66.1|-17.4,-66.2")
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    # ÉXITO PROXY: Extracción ultrarrápida si la ruta ya figura en el Disco de Memoria
    if llave in memoria_activa:
        datos = memoria_activa[llave]
        return datos[0], datos[1], datos[2]
        
    # FALLO: Llamada remota mediante red al servidor OpenStreetMap (OSRM)
    # [...] Invocación de request.get() vista anteriormente
    
    # Retención obligatoria de los datos traídos en la memoria y sincronización al Disco Duro
    memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
    guardar_memoria(perfil)
```

### 9. Ubicación de todos los museos, cómo los ingresamos en el proyecto
El punto principal de datos inyectado como semilla de información del proyecto es la cuadrícula base de locaciones patrimoniales. 
Realizamos labores previas de minería de coordenadas para los 23 museos involucrados de la ciudad de Cochabamba, identificando sus posicionamientos GPS satelitales absolutos con seis puntos decimales de exactitud geométrica.

Para materializar esta matriz dentro de nuestro ecosistema, la transcribimos creando una de las estructuras más veloces en lenguaje de programación Python conocida como un "Diccionario Constante de Datos", indexado y fijado en `configuracion.py`. Dicho diccionario convierte una solicitud textual basada en llaves en un tuple (par coordenado) en tiempo de complejidad algorítmica constante O(1).

```python
# Declaración de la Matriz Central Constante (configuracion.py)
MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    '[D] Museo Arqueológico UMSS': (-17.395278, -66.157394),
    '[E] Iglesia de la Compañía de Jesús': (-17.393023, -66.157814),
    '[F] Museo de Historia de la Medicina': (-17.382025, -66.151741),
    '[G] Casona Mayorazgo': (-17.373678, -66.165403),
    # ... (Matriz extendida y completada con la totalidad de los 23 museos de Cochabamba)
}
```

### 10. Cómo calculamos todas las rutas de movimiento para autos y el peatón
Cuando un algoritmo matemático exige trasladar un elemento del recinto A al recinto B, el motor cartográfico interviene requiriendo una instrucción de red a OSRM para trazar trayectorias de curvas y cortes que asemejen el flujo vehicular. Sin embargo, no podíamos diseñar un sistema crítico que colapsara enteramente si la red fallaba.
Por tanto, desarrollamos el cálculo en forma de un control "Try / Except". Si la conexión remota OSRM es un éxito, el sistema decodifica las polilíneas de las calles verdaderas. Si se produce un error y el servidor cae, se detona un **"Plan Logístico de Emergencia"**. El plan de emergencia acude a la fórmula de Haversine pura, tendiendo un vector directo imaginario desde la puerta A hasta la B y aplicándole una penalización sintética de aumento de distancia del 30% (`* 1.3`) como compensación al hecho de que el camino real habría contenido curvas u obstáculos peatonales.

```python
# Plan Logístico de Compensación de Fallas y Emergencia Cartográfica (configuracion.py)
except Exception as e:
    # Si las peticiones web fracasan irremediablemente, creamos vectores matemáticos directos
    # Le añadimos al resultado métrico un factor limitante y punitivo extra del 30% por curvas
    distancia_kilos = calcular_distancia_directa(origen, destino) * 1.3
    
    # Reconstrucción forzosa de variables físicas a partir de velocidad base ficticia de 20km/h
    tiempo_minutos = (distancia_kilos / 20.0) * 60
    
    # Unión de vértices A - B para que el renderizador no tenga nulos
    puntos_ruta = [origen, destino]
    
    return distancia_kilos, tiempo_minutos, puntos_ruta
```

### 11. Los modos de transporte, cómo los implementamos e instalamos
Dentro de las jerarquías de movimiento, implementamos 3 modalidades intermodales físicas para el usuario:
- Transporte a Pie (Movimiento libre multidireccional por aceras y calzadas).
- Transporte Privado en Taxi (Desplazamientos vehiculares rápidos sujetos al tráfico, con recojo personalizado origen a destino).
- Transporte Público en Microbuses (Rutas de circulación bloqueadas que demandan que el pasajero haga recorridos de a pie hasta sus vectores de intersección).

Dichos mecanismos están amarrados directamente en los controles de la Interfaz Visual y controlan booleanos algorítmicos. La implementación visual recae en botones de activación (Checkboxes) configurados por el usuario antes del motor, determinando y filtrando qué rutinas matemáticas debe ignorar la IA al momento de buscar sus grafos.

```python
# Controles de activación de sub-árboles de modos de transporte en Interfaz (ui_ventana.py)
self.check_pie = QCheckBox("Pie")
self.check_pie.setChecked(True)

self.check_taxi = QCheckBox("Taxi")
self.check_taxi.setChecked(True)

self.check_micro = QCheckBox("Micro")
self.check_micro.setChecked(True)

# Captura de inyecciones binarias a los Algoritmos del Buscador Supremo
permitir_pie = self.check_pie.isChecked()
permitir_taxi = self.check_taxi.isChecked()
permitir_micro = self.check_micro.isChecked()
```

### 12. Cómo creamos el caché para optimizar las operaciones de macrooperadores
El funcionamiento matemático puro del intermodalismo peatón-autobús-peatón genera que se tengan que fabricar tres recorridos de manera espontánea (la caminata, el viaje y el retorno a la puerta). Generar estas tres acciones en línea requeriría triplicar el retraso computacional en cada exploración combinatoria de los millones de posibles cruces.
Para arreglar este cuello de botella algorítmico, implementamos el archivo `precalcular_rutas.py`. Este módulo automatizado tiene la tarea de cruzar obligatoriamente los vértices de todos los 23 museos entre sí antes siquiera de que el software sea utilizado comercialmente. Al forzar a que el servidor analice todos los escenarios del grafo, este script logra el rellenado artificial exhaustivo del "Caché Local Peatonal".
Luego, el Macrooperador que ensambla el recorrido del bus, simplemente extrae su componente peatonal del disco duro de la computadora en velocidad ultrarrápida, eliminando por completo cualquier consulta redondante online de peatonización durante el análisis profundo.

```python
# Módulo de Automatización de Forzado Estructural del Caché Inicial (precalcular_rutas.py)
def generar_caches():
    nombres = list(MUSEOS.keys())
    total_museos = len(nombres)
    
    # Complejidad cuadrática cruzando todos contra todos (O(N^2))
    for i in range(total_museos):
        for j in range(total_museos):
            if i == j: continue
            origen = MUSEOS[nombres[i]]
            destino = MUSEOS[nombres[j]]
            
            # Detonamos y forzamos activamente que OSRM empaquete todas las calles y retenga la respuesta en Disco
            obtener_ruta_vehiculo(origen, destino, perfil="peaton")
            obtener_ruta_vehiculo(origen, destino, perfil="driving")
```

### 13. Instalación e Implementación de Motores de Búsqueda
La joya algorítmica del proyecto es su IA de selección paramétrica que garantiza obtener el mejor recorrido viable sin exceder jamás el presupuesto. Para buscar dicho sendero a través del grafo combinatorio implementamos el paradigma del **Motor de Búsqueda en Profundidad (Depth-First Search o DFS)**. 
Su diseño arquitectónico se sustenta en expandir progresivamente el recorrido agregando museo tras museo y calculando su acumulador total de costos de minutos y bolivianos. Para garantizar el descenso infinito en todas las opciones posibles de recorridos (y deshacer operaciones para explorar otras ramas si fuera necesario), este sistema fue implantado empleando recursividad. 

```python
# Módulo Recursivo del Buscador Analítico en Profundidad IA (agentes_ia.py)
def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado):
    # Condición recursiva de hoja terminal
    if not museos_faltantes:
        rutas_validas.append({
            'ruta': camino_actual,
            'cantidad_museos': len(camino_actual),
            'dinero_gastado': gasto_acumulado,
            'minutos_gastados': reloj_acumulado
        })
        return

    # Iteración de ensanchamiento horizontal probando el siguiente Museo factible
    for i, museo_destino in enumerate(museos_faltantes):
        nuevo_gasto, nuevo_reloj = computar_nodo(camino_actual, museo_destino)
        
        # Invocación recursiva: El Motor desciende a un nivel más profundo llamándose de nuevo a sí mismo
        explorar_opciones(
            camino_actual + [{'destino': museo_destino}],
            museos_faltantes[:i] + museos_faltantes[i+1:], 
            nuevo_gasto, 
            nuevo_reloj
        )
```

### 14. Instalación e Implementación de Macrooperadores
Al analizar la inserción de un transporte público (Micro o Trufi), se presenta un dilema donde la secuencia de viajar en bús fragmenta enormemente el árbol de grafos, porque un bus es esencialmente un trípode operativo: Caminar de la puerta del museo A a la parada, viajar de parada en parada dentro del autobús, y descender del autobús para caminar hacia el museo destino B. Tratar a estas acciones como eventos desconectados colapsa por completo a un Agente de Utilidad por explosión ramificativa.
Por ello, instalamos e implementamos la figura del **Macrooperador**, una herramienta heurística de programación. El Macrooperador ensambla bajo tierra esos 3 pasos fragmentados y, desde la perspectiva matemática del Motor Buscador, le inyecta directamente el cálculo total como una única macro-pieza atómica unificada inquebrantable, estabilizando el cálculo algorítmico y dándole agilidad al procesamiento.

```python
# Sistema de Inserción Heurística Multimodal mediante Macrooperadores Consolidados (agentes_ia.py)
elif tipo_viaje == 'Micro':
    # La computadora deduce transparentemente los puntos peatonales necesarios a la parada de interés
    
    # Inyección Estructural: 3 eventos subyacentes se anexan y agrupan conformando un sólo Macro-Desplazamiento unificado
    segmentos.extend([
        {'origen': nodo_a, 'destino': f'Parada_Inicio', 'modo': 'Pie', 'geometria': caminata_salida, 'costo': 0.0},
        {'origen': f'Parada_Inicio', 'destino': f'Parada_Fin', 'modo': 'Micro', 'geometria': micro, 'costo': tarifa_estandar},
        {'origen': f'Parada_Fin', 'destino': nodo_b, 'modo': 'Pie', 'geometria': caminata_llegada, 'costo': 0.0}
    ])
```

### 15. Instalación e Implementación de Poda
Durante el funcionamiento del Motor de Búsqueda, evaluar cada museo genera un crecimiento algorítmico exponencial. Por ejemplo, al intentar calcular un orden de viaje para 15 recintos (15 factorial), existen más de 1.3 billones de caminos resultantes. La potencia de procesamiento actual haría que este análisis tome decádas.
Para salvar esto, implementamos rigurosas técnicas de poda combinatoria. A cada paso minúsculo, la computadora interroga los parámetros de la **"Bolsa de Límite Máximo"**. Si un camino consumió ya todo tu dinero o toda la bolsa de tus horas, carece de todo sentido matemático que el Motor continúe profundizando hacia el siguiente museo asumiendo que los que falten por explorar fuesen siquiera alcanzables. En ese punto, el sistema detona la condición de ruptura, aborta y asesina activamente la rama completa ahorrando millones de procesamientos muertos inútiles.

```python
# Sistema de Poda Cuantitativa de Ramas Limitadas por Costos (agentes_ia.py)
def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado):
    
    # Evaluación Axiomática Estricta: Si nos pasamos de cualquier parámetro Límite de Bolsa, cortamos la rama de raíz
    if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
        m = len(museos_faltantes)
        
        # Métrica opcional: Calculamos y contabilizamos exactamente cuántos cientos de miles de ramas basura nos ahorramos
        ramas_asesinadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
        self.contador_exploracion += ramas_asesinadas
        
        # Interrupción Absoluta de Procesamiento, abortando a la IA para forzar su exploración en una rama lateral distinta
        return
```

### 16. Instalación e Implementación de Cálculo de Tiempo por Tramo
Tanto el Agente Físico Animador, como el propio Motor Buscador que mide las restricciones horarias, se ven en la imperiosa necesidad de saber cuántas horas y minutos toma cubrir un tramo vectorial por las calles. Pese a que el servidor de OSRM ya retorna una estimación por sí mismo, implementamos una recategorización basada en la física mecánica fundamental adaptada a los caprichos elegidos por el propio usuario del simulador.
Al multiplicar distancias puras por tasas relativas configuradas (la velocidad en coche fijada a 40km/h y la marcha a pie a 5km/h), aseguramos un sistema unificado y simétrico de medición de tiempos que es independiente de la topografía que decida la ruta.

```python
# Reconfiguración Estricta Mecánica (Leyes Físicas del Tiempo y Velocidad Uniforme) (agentes_ia.py)

# Discriminación referencial de velocidad de acuerdo a la naturaleza semántica de transporte del segmento actual
velocidad_física_actual = self.velocidad_auto if modo == 'Auto' else self.velocidad_pie

# Ley Mecánica Universal de Cuerpos Dinámicos: Tiempo (Horas) = Magnitud Distancia (Km) / Velocidad de Vector (Km/h)
tiempo_horas_crudas = distancia_kilos / velocidad_física_actual

# Ajuste temporal simple de escala temporal decimal horaria hacia escala de conteo sexagesimal minutera
tiempo_minutos_totales = tiempo_horas_crudas * 60
```

### 17. Instalación e Implementación de Filtrado y Despliegue de Resultados
Cuando finalizan el motor de recursión y la Poda de descarte, puede haber cientos de planes o caminos que pasaron el filtro (es decir, decenas de formas en que tu dinero sí te bastó y lograste tu cometido de la noche sin salir del cronómetro). ¿Qué debe desplegarle el simulador al usuario? 
Para decidir el Plan Victorioso, instalamos un bloque de código discriminador de Filtrado de Resultados en forma de Agente de Utilidad (una criba). Este analizador lee todas las propuestas viables encontradas, identifica cuál ruta visitó de forma absoluta el récord mayor del torneo (por ejemplo: la que logró incluir 10 museos), y purga agresiva e indiscriminadamente a toda ruta conformista que haya logrado visitar 9, 8 o menos, presentando solo a la élite suprema en la Pantalla.

```python
# Motor Criba Discriminadora de Utilidad Máxima Optimizada (agentes_ia.py)
if rutas_validas:
    # 1. Búsqueda de récord global sobre el array de atributos de viabilidad para establecer el "Techo de Campeón"
    techo_max_museos = max(ruta['cantidad_museos'] for ruta in rutas_validas)
    
    # 2. Reestructuración de lista comprimida aplicando discriminación y eliminación del resto de entidades menores y conformistas
    mejores_rutas = [ruta for ruta in rutas_validas if ruta['cantidad_museos'] == techo_max_museos]
    
    # 3. Empuje asíncrono y Despliegue directo al visor principal de las rutas ganadoras coronadas y probadas
    self.finalizado_senal.emit(mejores_rutas)
```

### 18. Manual Operativo Completo para el usuario del simulador
Para la ejecución y aprovechamiento eficaz de la "Noche de Museos Cochabamba", el operario del sistema deberá adherirse cautelosamente al siguiente flujograma de mandos:

1. **Punto de Inicio y Capital Semilla:** En el panel maestro de "Origen y Presupuesto" situado a la izquierda, redacte una referencia textual o, en su defecto, posicione un marcador interactivo haciendo un "Clic" preciso sobre cualquier locación del panel cartográfico derecho. Posterior a ello, alimente los campos paramétricos de Presupuesto Disponible (Dinero en Bolivianos) y Tiempo de Ronda (Minutos) que regularán a la máquina IA y definirán dónde ocurrirá la Poda.
2. **Limitaciones Cinemáticas y Multiplicadores de Motor Visual:** Descienda a la sección "Simulación". Defina velocidades (km/h) tanto para auto como pie. Adicionalmente, elija una Tasa Multiplicadora (Ej. x10, x20) en el combo. Este acelerador manipulará directamente la cadencia con la cual el Agente de Animación procesa los FPS en la red HTML, permitiéndole atestiguar movimientos veloces.
3. **Condicionamiento Paramétrico Binario:** ¿Desea prohibir ciertos métodos de recorrido? Deshabilite mediante casillas de verificación (Checkboxes) los rubros Pie, Taxi o Micro. Estos bloqueos inhabilitarán los macrooperadores pertinentes durante el descenso combinatorio de profundidad.
4. **Alimentación del Grafo Objetivo:** Seleccione minuciosamente mediante vistos buenos, todos los museos de la interfaz que formarán parte de la misión global. Procure combinar museos de rutas Peatonales (Cercanos al corazón de la Plaza) y de Múltiples tramos a conveniencia.
5. **Detección Algorítmica y Mapeo:** Pulse firmemente en "Calcular". Permita que los hilos operen en segundo plano y lea la traza en la Consola Log negra. Observe cómo el motor inspecciona y poda activamente iteraciones inválidas a un ritmo frenético hasta determinar la victoria algorítmica.
6. **Ejecución y Visualización Multimodal Físico:** En caso de resolución positiva en la que la matriz validó trayectorias y su dinero fue suficiente, la interfaz de resultados presentará la información comprimida del ganador con su tiempo y su costo. Seleccione la propuesta y proceda seleccionando la instrucción central "Iniciar". El mapa generará y transmutará el marcador del origen forzándolo a recorrer secuencial e interactivo las líneas superpuestas asfálticas de colores correspondientes a su transporte real dictado por la Inteligencia de Objetivos, restando montos y tiempo vivo del panel lateral.
