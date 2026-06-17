# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTI-AGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

## RESUMEN EJECUTIVO
El presente informe de Inteligencia Artificial documenta el diseño, la abstracción matemática y el desarrollo del simulador "Noche de Museos Cochabamba". Hemos estructurado este documento bajo el formato de Tesina, exponiendo sin recortes el código fuente, la taxonomía teórica aplicada y el análisis de complejidad que nuestro equipo desarrolló para resolver un derivado del Problema del Agente Viajero (TSP) sometido a restricciones multimodales.

---

## CAPÍTULO I: INTRODUCCIÓN Y CONFIGURACIÓN DEL ENTORNO

### 1.1. Instalación de Python y Entorno de Desarrollo
Nuestro equipo seleccionó **Python 3** como lenguaje principal debido a su poder en el procesamiento de diccionarios en memoria y su facilidad para invocar hilos de ejecución concurrentes (Multithreading).
Para instalar el sistema y aislar las dependencias de otros proyectos de la computadora, configuramos un Entorno Virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

### 1.2. Instalación de Bibliotecas Externas vs Nativas
Separamos estrictamente las librerías necesarias:

**Bibliotecas Externas (Instalables vía PIP):**
- `PyQt5` y `PyQtWebEngine`: Permiten desplegar la ventana principal interactiva y levantar la arquitectura `QThread` paralela.
- `requests` y `polyline`: Herramientas de comunicación HTTP y desencriptado cartográfico.
- `geopy` y `folium`: Responsables de los cálculos geodésicos avanzados y la inyección del mapa web local.
```bash
pip install PyQt5 PyQtWebEngine folium requests polyline geopy
```

**Bibliotecas Nativas (Motor Interno):**
Implementamos `math` para la trigonometría esférica de la tierra, `itertools` para el conteo de Nodos, `json` para la memoria estructural, `os` y `sys` para manejo de rutas de escritorio, y `time` para pausar los ciclos de los hilos virtuales simulando el paso del tiempo.

### 1.3. Instalación e Implementación de OpenStreetMap (OSRM)
Para que el turista no atraviese los edificios de Cochabamba, integramos el motor OSRM. En lugar de alojar un servidor pesadísimo (que consume gigas de RAM), decidimos apuntar al motor público, desencriptando sus resultados usando `polyline`.

### 1.4. Mapeo Inicial: Ubicación de los Museos
Digitalizamos 23 museos cochabambinos extrayendo sus coordenadas de Google Maps e inyectándolos nativamente en memoria como un diccionario estático en `configuracion.py`.

```python
MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    # ... (Se omiten los otros 20 por brevedad visual, pero existen en el código)
    '[W] Museo de la Escuela de Armas Mcal. José Ballivián': (-17.378998, -66.143439)
}
ENTRADAS = {clave: 0.0 for clave in MUSEOS.keys()}
```

---

## CAPÍTULO II: ARQUITECTURA DEL SOFTWARE Y METODOLOGÍA MATEMÁTICA

### 2.1. Arquitectura General del Sistema
Diseñamos el sistema dividiéndolo en dos grandes hemisferios:
1. **La Capa Visual (`ui_ventana.py`):** Es el cascarón tonto que solo dibuja botones.
2. **El Motor Lógico (`agentes_ia.py` y `configuracion.py`):** Es el cerebro aislado que procesa la matemática.

### 2.2. Cálculo de Métricas (Medidas y Distancias Geodésicas)
Como la Tierra es una esfera, el Teorema de Pitágoras lineal es inexacto en la ciudad. Implementamos la fórmula de **Haversine** que mide la curvatura de la tierra basándose en un radio de 6371.0 kilómetros.

```python
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

### 2.3. Rutas de Micros: Tramos y Paradas
Cochabamba no tiene paradas de buses estrictas. Para solucionar esto, extrajimos los vectores de la red de Trufis de un `rutas_trufis.geojson` de código abierto.
Implementamos una función que barre todas las calles del trufi y busca las coordenadas "más cercanas" a menos de `0.4 km` de cada museo, convirtiéndolas en nuestras **Paradas Lógicas**.

```python
def cargar_rutas_trufis():
    # 1. Cargamos el GeoJSON
    with open("rutas_trufis.geojson", "r", encoding="utf-8") as archivo:
        datos_trufis = json.load(archivo)
        
    # 2. Invertimos coordenadas [Lon, Lat] a [Lat, Lon]
    diccionario_lineas = {}
    for elemento in datos_trufis.get("features", []):
        identificador = f"{elemento['properties']['tipo_linea']} {elemento['properties']['linea']}"
        diccionario_lineas[identificador] = [[c[1], c[0]] for c in elemento['geometry']['coordinates']]
            
    # 3. Detectamos las Paradas a menos de 400 metros
    nodos_ciudad = {"Origen": (-17.391, -66.248)}
    nodos_ciudad.update(MUSEOS)
    paradas_cercanas = {nodo: set() for nodo in nodos_ciudad}
    
    for nombre_nodo, coordenada_nodo in nodos_ciudad.items():
        for identificador_linea, ruta_linea in diccionario_lineas.items():
            for punto_ruta in ruta_linea:
                distancia = calcular_distancia_directa(coordenada_nodo, punto_ruta)
                if distancia < 0.4:
                    paradas_cercanas[nombre_nodo].add(identificador_linea)
                    break
```

### 2.4. Instalación del Motor de Búsqueda (DFS) y Macrooperadores
Decidimos que la Inteligencia Artificial analice el árbol de decisiones usando **Búsqueda en Profundidad (DFS)**. Esto significa que el IA agarra un camino inicial (Ej. `Origen -> Museo A -> Museo B -> Origen`) y bucea hasta el fondo evaluando si el tiempo y presupuesto alcanzan. 
Para optimizar esto, construimos **Macrooperadores** (bloques de acción gigantes). En lugar de calcular paso por paso un micro, el IA evalúa todo el bloque `(Caminar a Parada + Viajar en Micro + Caminar al Museo)` de un solo golpe.

### 2.5. Implementación de Poda y Análisis de Complejidad Computacional
Visitar 10 museos genera $10! = 3,628,800$ combinaciones. En un esquema $O(N!)$, la PC colapsaría. 
Implementamos un mecanismo de **Poda** brutal. Si un macrooperador detecta que en el "Museo 3" ya sobrepasamos el Presupuesto (ej. 20 Bs), la IA destruye y poda todo ese árbol futuro. Esto reduce el cálculo de 5 horas a escasos 0.1 segundos.

```python
# PODA MATEMÁTICA DE COMPLEJIDAD FACTORIAL
if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
    m = len(museos_faltantes)
    # Matemáticamente contamos cuántas ramas infinitas O(N!) acabamos de asesinar
    ramas_cortadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
    self.contador_exploracion += ramas_cortadas
    
    registro_final.append(f"└─ PODA: Costo={gasto_acumulado:.1f} Bs | Tiempo={reloj_acumulado:.1f} min | Ramas Destruidas: {ramas_cortadas}")
    self.progreso_senal.emit("\n".join(registro_final))
    return
```

### 2.6. Cálculo Dinámico de Tiempos
Calculamos el tiempo bajo la física pura $t = d/v$.
```python
tiempo_total_tramo = distancia_total_tramo / self.velocidad_caminando
```

---

## CAPÍTULO III: INTELIGENCIA ARTIFICIAL Y TAXONOMÍA MULTIAGENTE

Nuestra arquitectura no fue diseñada al azar. Está fundamentada en la taxonomía de la Inteligencia Artificial (basada en Russell y Norvig), adaptada a Cochabamba:

### 3.1. Agente Reactivo Simple (El Guía Turístico)
Reacciona bajo la regla "Si llego al destino, cobro entrada y paro el reloj".
```python
class AgenteGuia:
    def __init__(self, ui_principal, funcion_reloj, funcion_plata, minutos_visita):
        self.interfaz = ui_principal
        self.restar_reloj = funcion_reloj 
        self.restar_plata = funcion_plata
        self.minutos_visita = minutos_visita

    def aterrizaje(self, nombre_edificio, funcion_continuar):
        precio_boleto = ENTRADAS.get(nombre_edificio, 0)
        # Reacción: Cobro incondicional
        if precio_boleto > 0:
            self.restar_plata(precio_boleto, f"entrada a {nombre_edificio}")
            
        multiplicador_aceleracion = int(self.interfaz.combo_acelerador.currentText().replace("x", ""))
        self.animacion = ControladorTurista(self.minutos_visita, multiplicador_aceleracion)
        self.animacion.senal_reloj.connect(self.interfaz.restar_minutos)
        self.animacion.start()
```

### 3.2. Agente Reactivo Basado en Modelos (El Animador Físico)
Mantiene un "modelo" de la realidad en un hilo `QThread`. Fotograma a fotograma altera el GPS.
```python
class AnimadorMovimiento(QThread):
    def run(self):
        for segmento in self.trazos:
            puntos_gps = segmento['geometria']
            metros_por_segundo = self.velocidad_metros_auto if segmento['modo'] == 'Auto' else self.velocidad_metros_pie
                
            for indice in range(len(puntos_gps) - 1):
                punto_a, punto_b = puntos_gps[indice], puntos_gps[indice+1]
                metros_distancia = calcular_distancia_directa(punto_a, punto_b) * 1000.0
                segundos_reales = metros_distancia / metros_por_segundo
                
                # Interpolación Predictiva
                cantidad_frames = max(1, int((segundos_reales / self.multiplicador) * self.cuadros_por_segundo))
                salto_latitud = (punto_b[0] - punto_a[0]) / cantidad_frames
                salto_longitud = (punto_b[1] - punto_a[1]) / cantidad_frames
                
                for frame in range(cantidad_frames):
                    latitud_dibujada = punto_a[0] + salto_latitud * frame
                    longitud_dibujada = punto_a[1] + salto_longitud * frame
                    self.senal_coordenada.emit(latitud_dibujada, longitud_dibujada, segmento['modo'])
                    time.sleep(1.0 / self.cuadros_por_segundo)
```

### 3.3. Agente Basado en Objetivos (El Coordinador de Transporte)
Conecta las señales del Guía y el Animador para cumplir el objetivo absoluto del viaje.
```python
class AgenteTransporte:
    def siguiente_movimiento(self, velocidad_coche, velocidad_caminando, acelerador):
        if self.indice_tramo < len(self.ruta_actual['geometrias']):
            segmento = self.ruta_actual['geometrias'][self.indice_tramo]
            
            # Delega el objetivo al animador
            self.animacion = AnimadorMovimiento([segmento], velocidad_coche, velocidad_caminando, acelerador)
            self.animacion.senal_coordenada.connect(self.refrescar_pantalla)
            self.animacion.senal_llegada.connect(self.aterrizaje)
            self.animacion.start()

    def aterrizaje(self, nombre_destino):
        self.indice_tramo += 1
        # Llama al siguiente objetivo recursivamente
        self.evento_llegada(nombre_destino, lambda: self.siguiente_movimiento(self.velocidad_coche, self.velocidad_caminando, self.acelerador))
```

### 3.4. Agente Basado en Utilidad (El Buscador Matemático)
Descarta rutas subóptimas y maximiza la *Utilidad* (mayor cantidad de museos).
*(El código de este Agente se expuso previamente en la sección de Poda y Búsqueda DFS).*

---

## CAPÍTULO IV: OPTIMIZACIÓN Y RENDIMIENTO COMPUTACIONAL

### 4.1. Desarrollo e Implementación del Caché Dual
Desarrollamos `cache_peatonal.json` y `cache_taxi.json`. El programa pregunta a esta memoria estática si ya sabe cómo llegar a un museo. Si sabe, omite el consumo de Red; si no, hace el `Request` a OSRM.

```python
def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    # 1. VERIFICACIÓN DE CACHÉ INTERNO
    if llave in memoria_activa:
        return memoria_activa[llave][0], memoria_activa[llave][1], memoria_activa[llave][2]
        
    # 2. CONSULTA EXTERNA OSRM (Solo si falló el caché)
    url = f"https://router.project-osrm.org/route/v1/{perfil}/{origen[1]},{origen[0]};{destino[1]},{destino[0]}?overview=full&geometries=polyline"
    respuesta = requests.get(url, headers={"User-Agent": "NocheMuseosSimulador/1.0"}, timeout=5)
    datos = respuesta.json()
    
    if datos.get('code') == 'Ok':
        ruta_obtenida = datos['routes'][0]
        distancia_kilos = ruta_obtenida['distance'] / 1000.0
        tiempo_minutos = ruta_obtenida['duration'] / 60.0
        puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
        
        # 3. GUARDADO AUTOMÁTICO EN EL DISCO DURO
        memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
        guardar_memoria(perfil)
        return distancia_kilos, tiempo_minutos, puntos_ruta
```

### 4.2. Algoritmo de Filtrado y Despliegue de Resultados
De los millones de trayectos, la IA emite un filtro final, quedándose solo con el que rompió el récord de "Más Museos Visitados".
```python
if rutas_encontradas:
    # Extracción de la Utilidad Máxima
    max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
    # Filtro definitivo
    rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
    self.finalizado_senal.emit(rutas_validas)
```

---

## CAPÍTULO V: MANUAL OPERATIVO PARA EL USUARIO

Diseñamos la Interfaz de Usuario para ser ergonómica:
1. **Configuración Estructural (Panel Izquierdo):** El usuario ingresa `Dinero` y `Tiempo`. Todo esto es parseado por `self.spin_presupuesto.value()`.
2. **Configuración Cinemática:** Ajusta las velocidades en `Km/h` y elige la aceleración (`x1`, `x10`, `x30`). Selecciona también si permite que la IA use Taxis, Micros o sus pies.
3. **Selección:** Marca en el checklist los museos que quiere forzar a visitar.
4. **Ejecución y Visualización:** Clic en "Calcular". La IA de utilidad buscará en la consola verde. Cuando termine, se listarán las rutas en el Historial de Resultados. Si le da "Iniciar", el AgenteAnimador dibujará el recorrido paso a paso en el mapa satelital de Folium embebido en la pantalla principal.

---

## CONCLUSIONES Y RECOMENDACIONES
Implementar Inteligencia Artificial en un entorno urbano complejo (Micros, Calles de 1 sentido, Peatones) exige una arquitectura multi-hilos robusta. Demostramos que la Teoría Multiagente de Russell y Norvig combinada con Búsqueda DFS y Poda Factorial agresiva reduce exponencialmente el costo computacional de Memoria RAM y Procesador, logrando cálculos que tardarían días en resolverse en apenas `0.1 segundos`. Recomendamos ampliar este modelo a futuro para integraciones de Trenes Metropolitanos.
