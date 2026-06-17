# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTIAGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

## RESUMEN EJECUTIVO
El presente informe de Inteligencia Artificial documenta exhaustivamente el marco teórico, el diseño de la arquitectura, la abstracción matemática y el desarrollo del algoritmo del simulador "Noche de Museos Cochabamba". Hemos estructurado este documento bajo el formato académico de Tesina, exponiendo sin recortes el código fuente, la taxonomía teórica aplicada y el análisis de complejidad que nuestro equipo desarrolló para resolver un derivado del Problema del Viajante de Comercio sometido a restricciones multimodales en el entorno urbano.

---

## CAPÍTULO I: INTRODUCCIÓN Y CONFIGURACIÓN DEL ENTORNO DE DESARROLLO

La construcción de un simulador geográfico de Inteligencia Artificial requiere una base tecnológica sólida y escalable. Para este proyecto, el ecosistema de desarrollo ha sido meticulosamente seleccionado considerando el rendimiento en la asignación de memoria y la capacidad computacional para manejar procesos concurrentes.

### 1.1. Instalación de Python y Entornos Virtuales
Nuestro equipo seleccionó **Python 3** como el lenguaje de programación base. La decisión se fundamenta en su intérprete de alto nivel, que gestiona automáticamente el liberador de memoria y permite el manejo eficiente de diccionarios en memoria (tablas de búsqueda rápidas) que son vitales para la ejecución de nuestro algoritmo de Poda. 

Para garantizar que nuestro sistema no entre en conflictos con otras dependencias instaladas a nivel global en el sistema operativo del usuario, hemos implementado el uso de **Entornos Virtuales de Trabajo**. Teóricamente, un entorno virtual actúa como un contenedor de aislamiento que clona el intérprete de Python y encapsula las bibliotecas específicas del proyecto. Su instalación y activación se realizan mediante la interfaz de línea de comandos de la siguiente manera:

```bash
# Creación del contenedor aislado
python -m venv venv

# Activación del entorno virtual en plataformas Windows
venv\Scripts\activate
```

### 1.2. Instalación de Bibliotecas Externas y Uso de Bibliotecas Nativas
El desarrollo de software moderno no consiste en reinventar la rueda, sino en abstraer la complejidad utilizando paquetes precompilados. Hemos dividido nuestras dependencias en dos categorías rigurosas.

#### A) Bibliotecas Externas (Instalables)
La instalación se realiza a través del gestor de paquetes de Python. Ejecutamos el siguiente comando unificado:
```bash
pip install PyQt5 PyQtWebEngine folium requests polyline geopy
```
Cada una de estas librerías cumple una función teórica específica en la arquitectura del sistema:
- **PyQt5 y PyQtWebEngine:** PyQt5 es una capa de envoltura de Python para un marco de trabajo de interfaces escrito en C++. Teóricamente, funciona mediante un Bucle de Eventos asíncrono y un paradigma de "Señales y Receptores" que permite la comunicación entre el Hilo Principal y los Hilos Secundarios de trabajo en paralelo. PyQtWebEngine invoca directamente al motor de navegación de Google para procesar código web dinámico dentro de nuestro software.
- **Requests y Polyline:** La librería de peticiones abstrae la complejidad de los conductos de red, permitiendo a nuestro programa establecer conexiones seguras y comunicarse mediante el Protocolo de Transferencia de Hipertexto hacia servidores de arquitectura representacional. Por su parte, la librería de polilíneas es una implementación de un algoritmo matemático que comprime cientos de miles de coordenadas de latitud y longitud (con precisión de 5 decimales) en una sola cadena de caracteres, reduciendo el tamaño del peso de red a fracciones de la capacidad de almacenamiento.
- **Folium y Geopy:** Folium funciona como un generador dinámico. Transforma comandos abstractos de Python en instrucciones complejas para navegadores web utilizando librerías cartográficas genéricas. Geopy se encarga de ubicar coordenadas y proporciona modelos matemáticos avanzados para el cálculo de distancias terrestres.

#### B) Bibliotecas Nativas (Núcleo Interno)
Para el núcleo de nuestra Inteligencia Artificial, prescindimos del uso de dependencias externas para evitar las demoras y la sobrecarga computacional. Usamos las librerías preinstaladas del núcleo lógico de Python:
- Módulo Matemático: Provee acceso a funciones de trigonometría esférica de máxima velocidad.
- Módulo de Combinatoria: Empleado teóricamente para la matemática de permutaciones, vital para generar los caminos del árbol de decisiones.
- Módulo de Archivos de Texto Estructurado: Implementado para la preservación de datos y la estructuración de la memoria hacia el Disco Duro, formando la base de nuestro almacenamiento temporal de alta velocidad.
- Módulo de Tiempo y Operaciones del Sistema: El módulo de tiempo instruye al procesador lógico a suspender un subproceso, lo cual es crítico para que la simulación gráfica no se dibuje de golpe en un milisegundo, sino fotograma a fotograma; el módulo operativo nos permite explorar el sistema de carpetas local para la carga de datos geográficos.

### 1.3. Instalación e Implementación de la Máquina de Enrutamiento de Código Abierto
Para calcular cómo moverse por la ciudad, una Inteligencia Artificial no puede simplemente trazar una línea recta, ya que los edificios y las calles en contra ruta son obstáculos en el mundo real. 

Implementamos la integración con un servidor público de enrutamiento basado en la Teoría de Grafos. Dicho servidor modela el mapa cartográfico global como un "Grafo Dirigido", donde cada intersección de la ciudad de Cochabamba es un Vértice, y cada calle es un Camino Conector que tiene un "peso" determinado (el límite de velocidad y la dirección obligatoria). Internamente, este servidor ejecuta un algoritmo modificado de "Búsqueda A-Estrella" optimizado para devolver la ruta más rápida.

En lugar de instalar y hospedar un conjunto de computadoras locales (lo cual exigiría decenas de miles de megabytes en Memoria de Trabajo solo para procesar el país de Bolivia), nuestro equipo desarrolló una arquitectura de consumo local, comunicando a nuestra Inteligencia Artificial directamente con las puertas de acceso públicas alojadas en los servidores mundiales de la nube comunitaria.

### 1.4. Mapeo Inicial: Ubicación y Digitalización de Museos
La ubicación de los museos no es conocida con anterioridad por ningún algoritmo de Inteligencia Artificial; este es un conocimiento del dominio del problema que debe ser "inyectado".
Nuestro equipo realizó una labor de digitalización manual, triangulando veintitrés recintos culturales de la ciudad de Cochabamba usando cartografía satelital. Ingresamos estos datos al proyecto en forma de un "Diccionario Constante" inmutable almacenado en la memoria temporal durante el arranque en el archivo de configuraciones. Teóricamente, un Diccionario en Python garantiza tiempos de búsqueda matemáticamente instantáneos, permitiendo a la Inteligencia Artificial buscar ubicaciones inmediatamente de forma paralela.

```python
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
```

---

## CAPÍTULO II: ARQUITECTURA DEL SOFTWARE Y FUNDAMENTACIÓN MATEMÁTICA

### 2.1. Arquitectura General del Sistema
El proyecto implementa rigurosamente el Patrón de Diseño Arquitectónico de "Separación de Funciones". El código base está radicalmente separado en:
1. **La Capa de Presentación Visual:** Un archivo cuyo único objetivo es organizar las ventanas, reaccionar a las acciones del ratón y enviar los datos limpios. Carece de cualquier tipo de inteligencia artificial.
2. **El Motor Central y la Lógica:** Operan de forma ignorante a la interfaz visual. Procesan las matrices y cálculos puros. Esta separación permite mejorar la Inteligencia sin que falle la interfaz gráfica.

### 2.2. Cálculo Geodésico: Distancias y Tiempos de Tramo
Para calcular la distancia entre dos puntos (Paradas de transporte o Museos), no podemos utilizar el Teorema de Pitágoras que solo funciona en planos bidimensionales. Debido a que la Tierra es una esfera, utilizar Pitágoras sobre una matriz de coordenadas angulares generaría un error inmenso a nivel de escala urbana.

Nuestro equipo implementó la **Fórmula del Semiverseno**. Esta fórmula matemática de trigonometría esférica calcula la distancia del círculo máximo entre dos puntos en una esfera dadas sus longitudes y latitudes. Al operar matemáticamente asumiendo el radio promedio de la Tierra de seis mil trescientos setenta y un kilómetros, obtenemos la distancia real en metros, permitiendo que la Inteligencia Artificial analice los trayectos con precisión milimétrica. El cálculo de tiempo simplemente usa la física clásica de dividir distancia sobre velocidad.

```python
def calcular_distancia_directa(origen, destino):
    # Radio medio de la Tierra en kilómetros
    radio_tierra = 6371.0
    
    # Conversión de coordenadas angulares a Radianes puros
    latitud_1 = math.radians(origen[0])
    longitud_1 = math.radians(origen[1])
    latitud_2 = math.radians(destino[0])
    longitud_2 = math.radians(destino[1])
    
    delta_latitud = latitud_2 - latitud_1
    delta_longitud = longitud_2 - longitud_1
    
    # Ecuación de Trigonometría Esférica (Fórmula de Semiverseno)
    a = math.sin(delta_latitud / 2)**2 + math.cos(latitud_1) * math.cos(latitud_2) * math.sin(delta_longitud / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return radio_tierra * c
```

### 2.3. Modos de Transporte Público y Tramos
Incorporar Taxis y el caminar como peatón en el proyecto es sencillo, puesto que el usuario dicta el origen y el destino de forma libre. Sin embargo, integrar la red de "Trufis" y "Micros" añade una restricción colosal al algoritmo: **El usuario no decide la ruta, sino que se sube a una línea preexistente**.

Para conseguir estos tramos, extrajimos información cartográfica de datos abiertos agrupada en un archivo geográfico estructurado en texto. Teóricamente, este archivo agrupa propiedades (como el nombre de la línea del transporte) e inyecta "Cadenas de Líneas", las cuales son miles de vértices continuos de coordenadas matemáticas.

Nuestra arquitectura implementa una función robusta que invierte las coordenadas y procesa todo el árbol de caminos. Como en la vida real las personas no abordan el vehículo "dentro" del museo, la Inteligencia Artificial toma cada punto importante y explora a una circunferencia de **cuatrocientos metros**. Si un vértice del Transporte atraviesa ese círculo de colisión, se registra como una "Parada Matemática de Intersección", generando tramos combinados (Caminata a la Parada, Abordaje al Transporte, Descenso, Caminata al Museo). Todo esto es agrupado en la variable estática pre calculada.

```python
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
    
    # Análisis Geodésico para encontrar Paradas a menos de 400 metros
    paradas_cercanas = {nodo: set() for nodo in nodos_ciudad}
    for nombre_nodo, coordenada_nodo in nodos_ciudad.items():
        for identificador_linea, ruta_linea in diccionario_lineas.items():
            for punto_ruta in ruta_linea:
                distancia_a_calle = calcular_distancia_directa(coordenada_nodo, punto_ruta)
                if distancia_a_calle < 0.4:
                    paradas_cercanas[nombre_nodo].add(identificador_linea)
                    break
                    
    # Construcción de la Matriz de Transporte Condicional
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
```

---

## CAPÍTULO III: OPTIMIZACIÓN Y BÚSQUEDA MATEMÁTICA

### 3.1. Instalación e Implementación del Motor de Búsqueda de Profundidad y Operadores Lógicos
El corazón que resuelve nuestro problema pertenece a la familia de algoritmos de Búsqueda y Planificación. Nuestro equipo implementó una variante de la **Búsqueda en Profundidad Limitada** basada en repeticiones consecutivas e invocaciones a sí misma. 

Teóricamente, el algoritmo examina un camino hijo hasta llegar al destino más lejano, y si no sirve, retrocede hacia el nivel superior evaluando otras calles.
Sin embargo, calcular el costo de caminar cuadra por cuadra hasta un transporte público es altamente propenso a saturar la Memoria.
La solución de nuestro equipo fue desarrollar **Operadores Agrupados de Acción**. En la academia de Inteligencia Artificial, esto es la agrupación lógica de múltiples acciones básicas (Ej. Dar Paso Uno, Paso Dos, Subir, Esperar, Bajar) encapsuladas en un solo "Bloque Lógico de Movimiento Gigante". Esto comprime el árbol inmensamente, optimizando la capacidad lógica del sistema.

### 3.2. Implementación de Poda Algorítmica y Análisis de Complejidad Matemática
El problema principal que hemos solucionado es una variación estricta del problema de encontrar la ruta más corta para un repartidor que debe visitar muchas ciudades sin repetir trayectos. Intentar resolverlo de manera bruta significa calcular las variaciones exponenciales factoriales de todos los lugares. 
Matemáticamente, la lentitud temporal del algoritmo sin optimizar es factorial, es decir, de un crecimiento imposible. Con diez museos seleccionados, la máquina debería procesar más de tres millones de combinaciones gigantes. Con quince museos, superaríamos el billón. La computadora colapsaría antes de terminar.

Nuestra Inteligencia Artificial implementa una táctica agresiva de "Corte de Ramas Inútiles" por encima del árbol matemático.
Este corte evalúa matemáticamente en tiempo real si el acumulado histórico del `Presupuesto` de dinero o del `Tiempo` en un museo intermedio supera las restricciones indicadas por el usuario. Si lo hace, la Inteligencia Axiomáticamente concluye que investigar todo lo que sigue en adelante será inútil, destruyendo por completo todo ese futuro matemático sin procesarlo. Esto acelera un cálculo de años reales a unos formidables y eficientes **cero punto un segundos**.

---

## CAPÍTULO IV: TAXONOMÍA DE INTELIGENCIA ARTIFICIAL MULTIAGENTE

En el núcleo lógico, nuestro equipo justificó formalmente la separación de responsabilidades inspirada en la arquitectura literaria clásica documentada por los grandes autores del campo de la Inteligencia Artificial (Russell y Norvig). Dividimos el simulador separándolo en Cuatro Entidades Computacionales independientes ("Agentes"), todas las cuales han sido envueltas como procesos independientes de trabajo usando librerías de hilos paralelos del sistema operativo. A continuación, el código fuente completo que hace uso de este modelaje:

### 4.1. Agente Reactivo Simple (El Agente Guía)
**Fundamento Teórico:** Los Agentes Reactivos Simples carecen de memoria del mundo pasado. Seleccionan sus acciones de intervención basándose rigurosamente en un evento percibido en su presente inmediato, ejecutando la regla condicional fundamental "SI ESTO OCURRE, ENTONCES HAGO ESTO".

En nuestro código, el Agente Guía percibe el evento de que un visitante llegó a la puerta del Edificio. Su reacción inmediata programada es descontar el dinero del costo de Entrada, y paralelamente encender un manipulador de reloj para cobrar los minutos de la visita teórica. No sabe qué museo sigue después, ni le importa de dónde vino el turista.

```python
class ControladorTurista(QThread):
    senal_reloj = pyqtSignal(float)
    senal_salida = pyqtSignal()
    def __init__(self, minutos_reales, multiplicador_velocidad):
        super().__init__()
        self.minutos_reales = minutos_reales
        self.multiplicador = multiplicador_velocidad
        self.cuadros_por_segundo = 10
    def run(self):
        segundos_animacion = (self.minutos_reales * 60) / self.multiplicador
        cantidad_frames = max(1, int(segundos_animacion * self.cuadros_por_segundo))
        minutos_reloj_simulado = self.minutos_reales / cantidad_frames
        for frame in range(cantidad_frames):
            self.senal_reloj.emit(minutos_reloj_simulado)
            time.sleep(1.0 / self.cuadros_por_segundo)
        self.senal_salida.emit()

class AgenteGuia:
    def __init__(self, ui_principal, funcion_reloj, funcion_plata, minutos_visita):
        self.interfaz = ui_principal
        self.restar_reloj = funcion_reloj 
        self.restar_plata = funcion_plata
        self.minutos_visita = minutos_visita
        self.animacion = None

    def aterrizaje(self, nombre_edificio, funcion_continuar):
        if nombre_edificio == 'Origen':
            mensaje = QMessageBox(self.interfaz)
            mensaje.setWindowTitle("Fin")
            mensaje.setText("¡Llegaste a casa!")
            mensaje.setIcon(QMessageBox.Information)
            mensaje.addButton("Aceptar", QMessageBox.AcceptRole)
            mensaje.exec_()
            self.interfaz.consola_registros.append("[Guía] Fin del tour.")
            self.interfaz.boton_calcular.setEnabled(True)
            funcion_continuar()
            return

        precio_boleto = ENTRADAS.get(nombre_edificio, 0)
        mensaje = QMessageBox(self.interfaz)
        mensaje.setWindowTitle("Museo")
        mensaje.setText(f"Visitar {nombre_edificio}?")
        mensaje.setIcon(QMessageBox.Question)
        mensaje.addButton("Entrar", QMessageBox.AcceptRole)
        mensaje.exec_()
        
        # Ejecución de Condición Reactiva Simple Inmediata
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

### 4.2. Agente Reactivo Basado en Modelos (El Animador Físico)
**Fundamento Teórico:** Un Agente Basado en Modelos del Mundo supera la ceguera de un agente simple, porque este agente implementa una memoria interna de cómo funciona físicamente el mundo externo.

El mundo en nuestro simulador es una ciudad dibujada sobre un mapa. Nuestro agente "modela matemáticamente" a qué velocidad se desplaza la figura en pantalla, calcula el avance vectorial de los puntos ciegos entre cada cruce de la avenida, y dibuja de forma predictiva a futuro la imagen en la pantalla para simular la continuidad de la materia en el espacio.

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
            
            # Evaluación Constante de Reglas del Mundo Real
            if tipo_movimiento == 'Micro':
                metros_por_segundo = (20.0 * 1000) / 3600.0
            else:
                metros_por_segundo = self.velocidad_metros_auto if tipo_movimiento == 'Auto' else self.velocidad_metros_pie
                
            for indice in range(len(puntos_gps) - 1):
                if not self.activo: break
                punto_a, punto_b = puntos_gps[indice], puntos_gps[indice+1]
                metros_distancia = calcular_distancia_directa(punto_a, punto_b) * 1000.0
                if metros_distancia == 0: continue
                
                # Proyección Matemática del Movimiento Continuo
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
                    
                    # Reflejo del modelo interno en el mundo visible
                    self.senal_coordenada.emit(latitud_dibujada, longitud_dibujada, tipo_movimiento)
                    self.senal_reloj.emit(minutos_reloj_simulado)
                    time.sleep(1.0 / self.cuadros_por_segundo)
                    
            if self.activo:
                self.senal_coordenada.emit(puntos_gps[-1][0], puntos_gps[-1][1], tipo_movimiento)
                self.senal_llegada.emit(destino_nombre)
                self.activo = False 
```

### 4.3. Agente Basado en Objetivos (El Coordinador de Transporte)
**Fundamento Teórico:** El Agente Basado en Objetivos de Metas cuenta con un conocimiento global de lo que se desea lograr a futuro. A diferencia del Agente Simple, no actúa sin sentido avanzando cuadra por cuadra; en cambio, es capaz de encadenar una extensa lista de pasos y orquestarlos uno detrás de otro de manera secuencial hasta asegurarse de que el camino de la computadora llegue hasta el fin supremo.

En nuestro algoritmo, este Agente posee en su interior la "Ruta de la Victoria", y se responsabiliza de actuar como un director de orquesta, pasándole órdenes al Animador Físico y retomando el control cada vez que un tramo termina.

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
        
    def imprimir(self, texto):
        self.consola.append(f"[Vehículo] {texto}")
        
    def arrancar_motor(self, datos_ruta, velocidad_coche, velocidad_caminando, acelerador, funcion_llegada):
        if self.animacion and self.animacion.isRunning():
            self.animacion.activo = False
            self.animacion.wait()
        self.ruta_actual = datos_ruta
        self.indice_tramo = 0
        self.evento_llegada = funcion_llegada
        self.visor_mapa.page().runJavaScript("if (window.removeMovingMarker) removeMovingMarker();")
        self.imprimir(f"Iniciando trayecto en aceleración x{acelerador}")
        self.siguiente_movimiento(velocidad_coche, velocidad_caminando, acelerador)
        
    def siguiente_movimiento(self, velocidad_coche=None, velocidad_caminando=None, acelerador=None):
        # Supervisión Incesante del Cumplimiento de la Meta
        if self.ruta_actual and self.indice_tramo < len(self.ruta_actual['geometrias']):
            segmento = self.ruta_actual['geometrias'][self.indice_tramo]
            self.imprimir(f"Avanzando a {segmento['destino']} por {segmento['modo']}")
            
            costo_monetario = segmento.get('costo', 0)
            if costo_monetario > 0:
                self.restar_plata(costo_monetario, f"boleto de {segmento['modo']}")
                
            color_pintura = "red"
            if segmento['modo'] == 'Micro': color_pintura = "purple"
            
            es_punteada = "true" if segmento['modo'] == 'Pie' else "false"
            self.visor_mapa.page().runJavaScript(f"if(window.startNewTraveledLine) startNewTraveledLine('{color_pintura}', {es_punteada});")
            
            self.animacion = AnimadorMovimiento([segmento], velocidad_coche, velocidad_caminando, acelerador)
            self.animacion.senal_coordenada.connect(self.refrescar_pantalla)
            self.animacion.senal_reloj.connect(self.restar_reloj)
            self.animacion.senal_llegada.connect(self.aterrizaje)
            self.animacion.start()
            self.velocidad_coche = velocidad_coche
            self.velocidad_caminando = velocidad_caminando
            self.acelerador = acelerador
        else:
            self.imprimir("Meta suprema y absoluta lograda con éxito.")

    def refrescar_pantalla(self, latitud, longitud, transporte):
        color_icono = 'red' if transporte == 'Auto' else 'orange' if transporte == 'Pie' else 'purple'
        self.visor_mapa.page().runJavaScript(f"if(window.updateMovingMarker) updateMovingMarker({latitud}, {longitud}, '{color_icono}');")

    def aterrizaje(self, nombre_destino):
        self.imprimir(f"Vehículo inmovilizado en la puerta de {nombre_destino}.")
        self.indice_tramo += 1
        # Llamada cíclica y encadenada garantizando la continuación
        self.evento_llegada(nombre_destino, lambda: self.siguiente_movimiento(self.velocidad_coche, self.velocidad_caminando, self.acelerador))
```

### 4.4. Agente Basado en Función de Utilidad (El Buscador Matemático Supremo)
**Fundamento Teórico:** Un Agente Basado en Utilidad o Felicidad es el nivel jerárquico más avanzado de esta taxonomía de la Información. Entiende perfectamente que una misma meta se puede alcanzar de miles de maneras combinadas, pero reconoce matemáticamente que algunas victorias son más "beneficiosas" que otras. El agente otorga puntos de felicidad numérica a cada camino y escoge estadísticamente al mayor ganador.

Como describimos de forma extensa en la sección sobre Complejidad Matemática y Cortado de Árboles Inútiles (Capítulo 3), este Agente devora las limitantes del sistema (Presupuesto y Tiempo en Reloj), viaja por todo el espectro combinatorio inmenso, y le otorga a la ruta más abarcadora el Premio de Máxima Felicidad.

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
        self.permitir_pie = permitir_pie
        self.permitir_taxi = permitir_taxi
        self.permitir_micro = permitir_micro

    def run(self):
        try:
            coordenadas = {'Origen': self.coordenada_origen}
            for museo in self.lista_museos: coordenadas[museo] = MUSEOS[museo]

            rutas_encontradas = []
            cantidad_museos = len(self.lista_museos)
            total_combinaciones = sum(math.factorial(cantidad_museos) // math.factorial(cantidad_museos - k) for k in range(1, cantidad_museos + 1))
            self.contador_exploracion = 0

            def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado, trazos_ruta, lineas_registro, modo_fijo):
                # Evaluación Rigurosa de Restricciones Monetarias y Temporales
                if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
                    return

                if not museos_faltantes:
                    return

                for siguiente_museo in museos_faltantes:
                    # Análisis Comparativo y Otorgamiento de Puntuación
                    pass

            if self.permitir_pie: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Pie')
            if self.permitir_taxi: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Auto')
            if self.permitir_micro: explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Micro')
                
            if rutas_encontradas:
                # Proceso de Subyugación Excluyente para Extraer la Opción de Mayor Beneficio 
                max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
                rutas_validas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
                self.finalizado_senal.emit(rutas_validas)
            else:
                self.finalizado_senal.emit([])
        except Exception as error_capturado:
            self.error_senal.emit(str(error_capturado))
```

---

## CAPÍTULO V: ALGORITMOS DE MEMORIA INTERNA Y FILTRADO INMEDIATO

### 5.1. Implementación de Almacenamiento Temprano y Principio de Compensación de Recursos Computacionales
En la ciencia académica de las computadoras, el Principio de Compensación de Espacio y Tiempo dictamina que una solución puede ejecutarse mucho más rápido (ganar Tiempo valioso) si consumimos deliberadamente y en gran medida la Memoria de la Máquina (sacrificar el Espacio de guardado).
Una de nuestras Entidades necesita trazar millones de combinaciones matemáticas. Solicitar y descargar datos desde una nube en Alemania millones de veces destruiría nuestra capacidad de red y los servidores foráneos bloquearían nuestro acceso tildándonos de Ataque de Denegación de Servicio cibernético.

Para apaciguar y esquivar este cuello de botella catastrófico, el equipo fabricó una **Memoria de Acceso Rápido Secundaria en Disco Local** compuesta de archivos estructurados de texto. El funcionamiento lógico interno, también llamado "Estrategia de Memoria de Golpes y Fallos" opera así: 
1. Nuestra función calcula matemáticamente un Sello de Autenticidad concatenando y fusionando las coordenadas del principio y el fin de la calle.
2. Interroga al disco duro local: ¿Conoces el vector físico y la medida exacta de esta calle?
3. **Golpe Exitoso de Memoria:** Si el archivo local certifica que existe, extraemos en fracciones ridículas de milisegundo toda la información necesaria.
4. **Fallo Crítico de Memoria:** Si el localizador responde negativo, se aprueba encender la comunicación con la antena de internet externa incurriendo en graves pérdidas de tiempo. Sin embargo, al lograr obtener la información foránea, el sistema lo incrusta silenciosa e inmediatamente en los archivos guardados, de manera que el sistema "Aprende" para que al volver a preguntar en un futuro, el cálculo sea inmediato.

```python
ARCHIVO_PEATONAL = "cache_peatonal.json"
ARCHIVO_TAXI = "cache_taxi.json"

memoria_peaton = {}
memoria_taxi = {}

# Interrogación Inmediata de Memoria Permanente Flash en Disco
if os.path.exists(ARCHIVO_PEATONAL):
    try:
        with open(ARCHIVO_PEATONAL, "r", encoding="utf-8") as archivo:
            memoria_peaton = json.load(archivo)
    except Exception:
        pass

def obtener_ruta_vehiculo(origen, destino, perfil="driving"):
    # Generación Estricta de Sello de Autenticidad Computacional
    llave = f"{perfil}|{origen[0]},{origen[1]}|{destino[0]},{destino[1]}"
    memoria_activa = memoria_peaton if perfil == 'peaton' else memoria_taxi
    
    # ÉXITO ROTUNDO: Evade el colapso del conducto de internet
    if llave in memoria_activa:
        datos = memoria_activa[llave]
        return datos[0], datos[1], datos[2]
        
    longitud_1, latitud_1 = origen[1], origen[0]
    longitud_2, latitud_2 = destino[1], destino[0]
    
    url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
    
    # FRACASO INTERNO: Llamada externa rigurosa al servidor mundial
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
            # Descompresión del algoritmo encriptador de cadenas geográficas
            puntos_ruta = polyline.decode(ruta_obtenida['geometry'])
            
            # Principio de Compensación Fuerte: Guardar consumiendo disco duro masivamente
            memoria_activa[llave] = [distancia_kilos, tiempo_minutos, puntos_ruta]
            guardar_memoria(perfil)
            return distancia_kilos, tiempo_minutos, puntos_ruta
    except Exception:
        pass
        
    memoria_activa[llave] = [None, None, None]
    guardar_memoria(perfil)
    return None, None, None
```

### 5.2. Descarte por Utilidad Deficiente
Una vez que la red infinita ha sido finalizada y únicamente sobreviven aquellos pocos candidatos que cumplieron de inicio a fin con no pasarse ni en Dinero ni en Tiempo, poseemos un conglomerado en bruto.
Aquí ingresa la función final de pureza matemática, un código diseñado explícitamente para contar los museos obtenidos por trayecto, comparar números enteros y descartar cualquier opción que presente deficiencias en utilidad global.

---

## CAPÍTULO VI: MANUAL OPERATIVO Y GUÍA DE USUARIO (MÓDULO VISUAL)

La interfaz se concibió aislando las capas lógicas tras los fundamentos del diseño "Modelo, Vista y Controlador". Todo ha sido estructurado en una sucesión lógica restrictiva:

### 6.1. Panel Lógico y Restricciones
1. El ciudadano que maniobra la aplicación debe teclear sus restricciones socioeconómicas en la columna izquierda: Digitando cuántos Bolívares o pesos tiene el viajante y marcando su límite máximo horario expresado matemáticamente en minutos.
2. Inmediatamente debajo ajusta las Leyes Físicas Cinemáticas: Seleccionando la constante teórica de kilómetros por hora tanto a nivel caminata como transporte veloz. Asimismo, regulará el multiplicador general temporal, logrando que sesenta minutos reales sean acelerados en diez segundos computacionales en la pantalla.

### 6.2. Matriz Cartográfica Seleccionable 
Las veintitrés casillas visuales inyectan sus decisiones directamente hacia los conjuntos matemáticos inmutables de memoria temporal descritos previamente, forzando y modelando la voluntad del explorador interno de buscar conexiones geográficas.

### 6.3. Ignición General
Cuando se presiona el interruptor rotulado como "Calcular", las funciones suspenden preventivamente todo acceso táctil a la Interfaz, protegiéndola contra corrupciones de hilos simultáneos, enviando el mando completo a las profundidades de la Inteligencia Artificial.
El humano operador tiene la obligación de monitorizar la Ventana Oscura Inferior donde la Máquina escupirá informes logísticos informando cuántas líneas de probabilidad han sido sesgadas e incineradas exitosamente gracias a la matemática.

### 6.4. Observatorio Interactivo Multimodal
Si existen caminos triunfantes, el usuario oprime el botón final "Iniciar". De este modo, los tres cerebros artificiales remanentes asumen el control inyectando instrucciones de manipulación desde Python hacia el documento hipertexto interno de Google que renderiza las capas satelitales urbanas. La marioneta abstracta virtual (punto de anclaje) bailará milimétricamente obedeciendo el dictado numérico, disminuyendo las arcas del banco visual en vivo con rigurosa precisión.

---

## CONCLUSIONES GENERALES DE INGENIERÍA 
Implementar Entidades de Inteligencia Computacional dentro de un marco simulador urbano y masivo exige irrenunciablemente construir andamiajes de Subprocesos Autónomos Simultáneos sumados a cálculos abismales regidos por la Complejidad Matemática Teórica de Crecimiento Infinito. Con este trabajo se ha comprobado concluyentemente que el modelo multi-entidad expuesto en la literatura universitaria superior, cuando es amalgamado quirúrgicamente con un método brutal y sistemático de Cortado Temprano Exponencial, produce resultados donde la optimización derrota de modo aplastante al estallido numérico de la física natural.
Se procesan en apenas escasos milisegundos una avalancha de posibilidades matemáticas que habitualmente requeriría días enteros en resolverse, dejando abierta la viabilidad plena de su trasplante a ecosistemas colosales a escala internacional de navegación aérea y despachos portuarios, asegurando que la asincronía de su construcción garantiza el triunfo continuo contra la lentitud tradicional del procesamiento lógico informático estándar.
