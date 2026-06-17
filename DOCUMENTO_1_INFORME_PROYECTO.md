# INFORME TÉCNICO COMPLETO: SIMULADOR DE INTELIGENCIA ARTIFICIAL PARA LA NOCHE DE MUSEOS EN COCHABAMBA

## CAPÍTULO 1: INTRODUCCIÓN Y PLANTEAMIENTO DEL PROBLEMA

### 1.1 Contexto del Proyecto
La "Noche de Museos" es uno de los eventos culturales más importantes de la ciudad de Cochabamba, Bolivia. Durante esta jornada, decenas de espacios culturales, galerías y museos abren sus puertas al público en horarios nocturnos. Sin embargo, la amplia distribución geográfica de estos recintos en el entorno urbano (abarcando desde el centro histórico hasta zonas periféricas) representa un problema logístico significativo para los asistentes. 

Los visitantes enfrentan tres limitantes críticas:
1. **El Tiempo:** El evento dura un periodo finito (generalmente entre 4 a 6 horas). Visitar todos los museos es físicamente imposible.
2. **El Presupuesto:** Los ciudadanos disponen de una cantidad finita de recursos económicos. Este dinero debe dividirse entre el pago del transporte público/privado y las entradas a los recintos.
3. **El Transporte:** Desplazarse de un punto a otro en Cochabamba involucra tomar decisiones dinámicas: caminar, tomar un taxi directo, o caminar hacia una avenida para interceptar una línea de transporte público (Trufi o Micro) y luego caminar hacia el destino final.

### 1.2 Formulación del Problema
Este problema se clasifica dentro de las Ciencias de la Computación como una variante del **Problema del Agente Viajero (Travelling Salesperson Problem - TSP)** con la adición de restricciones severas (Constrained TSP) y una red de transporte multimodal. 
Dado un conjunto de $n$ museos, existen $\sum_{k=1}^{n} \frac{n!}{(n-k)!}$ posibles permutaciones de visita. Para un conjunto de 10 museos, el número de permutaciones supera los 9 millones. Analizar cada una para encontrar el camino más barato y rápido es imposible para el cerebro humano, y sin optimización algorítmica, también resulta costoso para los computadores.

### 1.3 Objetivos
**Objetivo General:**
Desarrollar un sistema de Inteligencia Artificial basado en Arquitectura Multi-Agente en Python que planifique, optimice y simule interactivamente las rutas turísticas para la Noche de Museos en Cochabamba, respetando restricciones de tiempo y presupuesto.

**Objetivos Específicos:**
- Integrar servicios de geolocalización global (OSRM y OpenStreetMap) para trazar rutas precisas en el mapa vial de Cochabamba.
- Incorporar una red lógica de transporte público que evalúe cruces entre peatones y líneas de micros/trufis.
- Diseñar un sistema de almacenamiento caché dinámico para mitigar las latencias de red.
- Desarrollar una interfaz gráfica asíncrona que renderice la física de los traslados y administre las métricas en tiempo real.

---

## CAPÍTULO 2: MARCO TEÓRICO Y TECNOLÓGICO

### 2.1 Inteligencia Artificial y Agentes
Un agente inteligente es una entidad computacional autónoma capaz de percibir su entorno y tomar decisiones para maximizar sus posibilidades de éxito. En este proyecto se utilizó un paradigma Multi-Agente donde distintas piezas de software controlan el cálculo algorítmico, el movimiento cinemático y la lógica financiera del turista.

### 2.2 Tecnologías y Librerías Utilizadas
El ecosistema de la aplicación se construyó íntegramente en Python 3, apalancándose en las siguientes tecnologías:
- **PyQt5:** Framework robusto para la construcción de la Interfaz Gráfica de Usuario (GUI) mediante ventanas, botones y listas.
- **PyQtWebEngine:** Permite instanciar un navegador web embebido dentro de la ventana de Python. Esto es vital para procesar HTML y JavaScript dinámico.
- **Folium y Leaflet.js:** Herramientas que permiten dibujar un mapa satelital/vectorial interactivo e inyectar figuras geométricas (marcadores, polilíneas).
- **API OSRM (Open Source Routing Machine):** Servicio web que, dadas dos coordenadas, retorna por cuáles calles debe transitar un vehículo respetando los sentidos de circulación (calles de una sola vía) de Cochabamba.
- **Geopy (Nominatim):** Motor que convierte texto (Ej. "Plaza Principal Cochabamba") a variables de tipo `float` (Latitud y Longitud).
- **Matemática Esférica (Haversine):** Debido a que la tierra es una esfera, no se puede usar el Teorema de Pitágoras para calcular la distancia entre dos coordenadas geográficas. Se utiliza la fórmula de Haversine para encontrar la distancia ortodrómica real en kilómetros.

---

## CAPÍTULO 3: ARQUITECTURA DEL SISTEMA (EXPLICACIÓN DE ARCHIVOS)

El proyecto se estructuró modularmente bajo el patrón Modelo-Vista-Controlador. A continuación, se detalla exhaustivamente qué hace cada archivo y cómo lo logra.

### 3.1. Archivo `main.py` (El Inicializador)
Es el punto de entrada al programa. Su función es estrictamente de configuración ambiental.
- **Para qué sirve:** Arranca el bucle de eventos (`QApplication`). 
- **Qué soluciona:** En sistemas Windows, el motor `WebEngine` a veces falla al cargar mapas si las tarjetas gráficas OpenGL presentan conflictos. `main.py` inyecta banderas al sistema operativo (`QTWEBENGINE_CHROMIUM_FLAGS = "--disable-gpu --no-sandbox"`) para forzar un renderizado por software seguro. También escala las fuentes e íconos para monitores modernos (High DPI).

### 3.2. Archivo `ui_ventana.py` (La Interfaz Gráfica - Frontend)
Contiene la clase `VentanaPrincipal`. Este archivo tiene más de 300 líneas dedicadas a dibujar botones, recolectar datos y construir el puente entre Python y JavaScript.
- **Estructura UI:** Agrupa elementos en áreas lógicas ("Origen y Presupuesto", "Física y Simulación", "Selección de Museos"). 
- **El Puente Bidireccional:** Crea un mapa estático inicial con Folium y lo guarda en `mapa_museos.html`. Luego usa `runJavaScript()` para inyectar código dinámico y mover los íconos del auto, micro o peatón sobre el mapa *sin necesidad de recargar la página*.
- **Manejo de Señales:** Conecta los botones de "Calcular" e "Iniciar" con el backend lógico, recogiendo primero los datos como el multiplicador de velocidad, el origen y el tiempo de visita a museos.

### 3.3. Archivo `configuracion.py` (Base de Datos, Red y Memoria)
Es el núcleo de los datos estáticos y peticiones externas.
- **El Diccionario `MUSEOS`:** Almacena 23 museos emblemáticos de Cochabamba con sus coordenadas absolutas.
- **El Sistema de Caché (`cache_peatonal.json` y `cache_taxi.json`):** 
  - *¿Cómo funciona?* Cuando la IA necesita ir del Museo A al Museo B en auto, llama a la función `obtener_ruta_vehiculo()`. Esta función revisa si el trayecto ya está guardado en los archivos temporales respectivos. 
  - *¿Por qué es fundamental?* Si hiciéramos 5000 peticiones a internet para averiguar la calle, el servidor nos banearía (bloquearía la IP) y el proceso tardaría minutos. Al guardar cada respuesta exitosa en el disco duro (el archivo json), la próxima vez que se requiera ese trayecto, la lectura es inmediata, permitiendo a la IA probar miles de rutas combinadas en un milisegundo.
- **Carga de Transporte Público (Trufis):** Carga un archivo `GeoJSON` que contiene los vectores del trayecto real de las líneas de micros de la ciudad. Calcula qué museos tienen paradas cercanas a menos de 400 metros usando matemática directa, y construye una *Matriz de Costos* (Ej. de Santiváñez al mARTadero cuesta 3 Bs).

### 3.4. Archivo `agentes_ia.py` (Inteligencia Artificial y Motores de Física)
El corazón del proyecto, donde habitan las matemáticas pesadas y la asincronía.
Se divide en cuatro grandes clases que heredan de `QThread`, permitiendo paralelismo computacional.

**A) El Agente Inteligente: `AgenteBuscador`**
- **El Algoritmo:** Utiliza *Búsqueda Exhaustiva en Profundidad* (DFS) modificada con poda (Branch and Bound). Explora cada permutación de visita museo por museo.
- **La Poda (Pruning):** A medida que explora, va sumando el pasaje y el tiempo gastado en caminar o ir en vehículo. Si de pronto el tiempo acumulado ya sobrepasó el límite dado por el usuario, el algoritmo detiene esa exploración en seco y descarta la rama completa de posibilidades, reportando en la consola como `PODA`.
- **Cálculo Físico por Tramos:** Para cada tramo evalúa:
  - ¿Ir a Pie? Revisa la distancia Haversine. 
  - ¿Ir en Auto? Revisa la red vial de OSRM (vía Caché) y suma la tarifa multiplicando la distancia por 5 Bs/km.
  - ¿Ir en Micro? Calcula la parada más cercana para subirse, mapea el tramo del micro desde el GeoJSON, y calcula la parada para bajarse. 

**B) El Agente Cinemático: `AnimadorMovimiento`**
Es un motor físico en tiempo real. 
- **La Lógica Interpolativa:** Recibe la polilínea de la calle (miles de pequeños puntos GPS). Con base a los Cuadros por Segundo (FPS) y a la velocidad indicada por el usuario (ej. 40 km/h), calcula cuánto tiempo real le tomaría a un auto llegar de una esquina a otra. Luego, reduce ese tiempo aplicando el "Multiplicador de Simulación" (Ej. x10). Finalmente, calcula mediante derivadas los pasos `dLatitud` y `dLongitud` para actualizar la posición en el mapa cuadro a cuadro sin generar saltos visuales bruscos.

**C) El Agente de Tiempo Estático: `AgenteGuia`**
Se encarga de frenar el desplazamiento geográfico. Cuando el auto llega a la puerta del museo, este hilo entra en acción, lanzando ventanas emergentes que cobran dinero del presupuesto y emitiendo señales (ticks) para avanzar el reloj del simulador mientras el usuario visita las salas.

**D) El Gestor de Flujo: `AgenteTransporte`**
Es un director de orquesta que coordina qué agente debe actuar, despachando la animación tramo por tramo y ordenando el pintado dinámico de las líneas en el mapa web (Rojo para Auto, Punteado Azul para Caminata, y Morado para Transporte Público).

---

## CAPÍTULO 4: SOLUCIONES DE INGENIERÍA Y LÓGICA APLICADA

Durante el desarrollo, se atacaron varios problemas de alta complejidad técnica que merecen una explicación profunda:

### 4.1. Solución al comportamiento "Anómalo" o "Volador" de la Caminata
*Problema detectado:* Las versiones preliminares usaban una distancia pura en línea recta para las rutas a pie. En el mapa, esto hacía parecer que la persona atravesaba las manzanas diagonalmente (volando sobre los techos de las casas). Intentar llamar a un servidor web peatonal causaba saturación y caída del sistema por la abrumadora cantidad de curvas pequeñas a calcular.
*Solución de Ingeniería:* Se aplicó un multiplicador de distorsión urbana (`x 1.1` y en versiones estrictas hasta `x 1.3`). Al tomar la distancia perfecta ortodrómica, el software asume que en el entorno de Cochabamba (calles de geometría "Manhattan" o en damero), el peatón tendrá que bordear las cuadras. Por lo tanto, artificialmente se extiende la distancia matemática y se reduce la velocidad peatonal. Además, esto obliga al Agente a buscar **subirse a los micros de manera inteligente**, prefiriendo cruzar a pie la calle hacia el sentido correcto de la vía en vez de tomar la ruta al revés y obligar al trufi a rodear la ciudad para volver.

### 4.2. Trasbordos Automatizados y Optimización Peatonal en Transporte Público
Para que la simulación refleje la toma de decisión humana en Cochabamba, el algoritmo fue instruido de la siguiente forma:
1. Al evaluar la opción "Micro" entre el lugar A y el B, ubica la geometría GPS de las líneas.
2. Extrae las sub-coordenadas. Mide mediante distancias `d1` (caminata inicial) y `d2` (caminata final).
3. Evalúa el peso algorítmico: El costo de tomar el micro no solo son los `3 Bs.`, sino que se le suma la penalidad por caminar hasta las paradas y el tiempo invertido. Si este tiempo es superior a simplemente tomar un taxi directo o caminar, la rama "Micro" es automáticamente descartada en beneficio del usuario.

### 4.3 Eliminación Total de Dependencias en Grafos Pesados (Optimización de RAM)
Al comienzo del proyecto, se planteó mapear visualmente todas las combinaciones generadas por la IA utilizando `NetworkX` y `PyVis`. Esta estructura forzaba la serialización de cientos de miles de nodos interactivos en HTML, sobrecargando el procesamiento del CPU a un 100% y utilizando un exceso de memoria RAM.
*Solución:* Se adoptó un patrón arquitectónico totalmente abstracto. Los datos y rutas ya no se modelan como nodos y aristas de dibujo, sino estrictamente como variables matriciales y diccionarios dentro del backend de Python, mejorando el rendimiento general en más de un 500% y logrando que la IA obtenga las rutas en escasos segundos.

### 4.4 Precisión Peatonal vs. Vehicular (Perfiles OSRM)
Se implementó una bifurcación de la API OSRM en dos perfiles independientes: `driving` y `foot`. Gracias a esto, el Agente Buscador no asigna una lógica vehicular estricta a un humano caminando (evitando recorridos circulares o bucles a causa de los sentidos únicos en calles vehiculares de Cochabamba). Los peatones ahora tienen rutas lógicas y óptimas a través de veredas directas. Además, esto solucionó el "Efecto Dron" (volar sobre edificios rectamente) al asegurar que la matemática peatonal consulte polilíneas de calles reales.

### 4.5 Filtrado Máximo de Rutas Parciales y Heurística de Opciones
Debido a que el tiempo humano es limitado, se reemplazó la lógica estricta (que forzaba la visita de la totalidad de museos seleccionados o fallaba) por una lógica de "Sub-Rutas Óptimas". El `AgenteBuscador` salva el estado en cada salto a un museo nuevo; si el tiempo y el presupuesto caducan prematuramente, el sistema filtra todas las posibilidades encontradas y despliega **únicamente aquellas rutas que logran visitar la cantidad máxima de museos posibles**, asegurando que el plan del usuario se acerque a su deseo original sin romper las reglas del universo. Adicionalmente se incorporaron filtros (Checkboxes) donde el usuario dicta si el agente puede o no utilizar "Taxi", "Caminar" o "Micro".

---

## CAPÍTULO 5: PRUEBAS DE ESTRÉS Y RENDIMIENTO
Las pruebas se ejecutaron sobre los conjuntos de datos en tiempo real de Cochabamba.
1. **Prueba de Restricción Monetaria Extrema:** Se redujo el presupuesto del usuario a 5 Bs y se asignó un recorrido de 5 museos. La IA falló en encontrar taxis debido al alto costo métrico, forzando la combinación exhaustiva de rutas exclusivas a pie y un tramo de micro. La respuesta de la consola evidenció la poda agresiva con éxito.
2. **Prueba de Latencia:** Gracias a la persistencia en cachés duales formatedados, el primer arranque puede tomar unos minutos evaluando llamadas HTTP. Sin embargo, al recargar la aplicación e invocar rutas previas, la velocidad de cálculo se redujo de ~20.0 segundos a `0.1 segundos` al ejecutarse al 100% desde caché en RAM local.

---

## CAPÍTULO 6: CONCLUSIONES DEL PROYECTO
- **Manejo Efectivo del TSP Restringido:** Se demostró mediante código Python que utilizar búsqueda algorítmica recursiva junto a reglas de poda estrictas (Costo/Tiempo) es suficiente para abatir la explosión factorial de la Noche de Museos, dando viabilidad al proyecto.
- **Arquitectura Fiable e Híbrida:** La separación entre Backend (Motores de Poda y Caching) y Frontend (WebEngine + Folium JS) garantiza que las interfaces en Python se mantengan fluidas mientras las matemáticas se resuelven en los hilos secundarios.
- **Implementación Adaptable y Escalable:** El uso de memorización JSON y cálculos espaciales matemáticos hace que, si mañana Cochabamba abre 100 museos nuevos, el sistema sea capaz de ingerirlos instantáneamente sin reescritura de código o sin sufrir congelamientos masivos por descargas de red.
