# MANUAL TÉCNICO Y DE USUARIO: OPTIMIZACIÓN MULTIAGENTE PARA RUTAS DE MUSEOS
## Proyecto: Noche de Museos en Cochabamba
**Materia:** Inteligencia Artificial  
**Desarrollado por:** Estudiante 1, Estudiante 2, Estudiante 3, Estudiante 4.

---

## CAPÍTULO I: INSTALACIONES Y CONFIGURACIONES BÁSICAS

### Instalación de Python
Para este proyecto decidimos usar Python 3 porque es un lenguaje fácil de entender y muy bueno para trabajar con datos y cálculos rápidos. 
Para que el proyecto funcione sin dañar otros programas de la computadora, creamos un "Entorno Virtual". Un entorno virtual es como una caja separada donde instalamos todo lo que el proyecto necesita sin mezclarlo con el resto de la computadora.
Se instala y activa en la consola así:
```bash
python -m venv venv
venv\Scripts\activate
```

### Instalación y Ejecución de Bibliotecas Externas como Nativas
Nuestro proyecto usa herramientas adicionales (bibliotecas) para no tener que programar todo desde cero. Las dividimos en dos tipos:

**Bibliotecas Externas:** Son las que tuvimos que descargar de internet usando el comando `pip install`.
- `PyQt5` y `PyQtWebEngine`: Las usamos para crear la ventana visual del programa y para poder mostrar el mapa de internet adentro de nuestra ventana.
- `requests` y `polyline`: Sirven para conectarnos a internet a pedir rutas y para descomprimir esas rutas que llegan codificadas.
- `folium` y `geopy`: Las usamos para dibujar las líneas y marcadores en el mapa, y para ubicar coordenadas.

**Bibliotecas Nativas:** Son las que ya vienen instaladas con Python por defecto.
- `math`: Para hacer cálculos de distancias.
- `itertools`: Para combinar las listas de los museos.
- `json`: Para guardar y leer nuestros archivos de rutas guardadas.
- `time` y `os`: Para pausar la animación de los autitos y para leer carpetas de la computadora.

### Ubicación de todos los Museos, cómo los ingresamos en el proyecto
Para saber dónde están los museos, buscamos manualmente las coordenadas (latitud y longitud) de los 23 museos de Cochabamba usando mapas por satélite. 
Una vez que tuvimos todas las coordenadas, las ingresamos directamente en el código del proyecto creando un "Diccionario". Un diccionario en Python nos permite guardar el nombre del museo y sus coordenadas exactas para que el programa las encuentre al instante.

```python
MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    '[C] Casona de Santiváñez': (-17.394425, -66.159162),
    # ... (23 museos en total)
}
```

---

## CAPÍTULO II: ARQUITECTURA DEL SISTEMA Y METRICAS

### Arquitectura del Sistema o Software
La arquitectura de nuestro programa está separada en dos partes principales para que funcione mejor:
1. **La Interfaz Visual:** Es el código que dibuja los botones, las listas y el mapa interactivo. Solo se encarga de mostrar cosas al usuario.
2. **El Motor Lógico:** Es el código que procesa los cálculos matemáticos, las rutas y la inteligencia artificial. Funciona separado de la pantalla para que el programa no se congele mientras piensa.

### Cómo se consigue las métricas de medida y distancia, y cómo se calcula
Para saber la distancia real entre un museo y una parada de micro, no podemos medir una línea recta plana, porque la tierra es redonda. 
Por eso usamos una fórmula matemática especial llamada **Fórmula de Haversine**. Esta fórmula toma las coordenadas GPS (latitud y longitud) y calcula la distancia tomando en cuenta la curva de la Tierra (usando el radio de la tierra de 6371 kilómetros). Así conseguimos la medida exacta en metros.

```python
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
Una vez que calculamos cuántos metros o kilómetros hay en un tramo, calculamos el tiempo usando la regla básica de la física: Tiempo es igual a Distancia dividida entre la Velocidad. 
El usuario elige a qué velocidad camina la persona y a qué velocidad va el auto. Luego el sistema divide los kilómetros del tramo entre esa velocidad para saber exactamente cuántos minutos tardará el viaje.

---

## CAPÍTULO III: MAPAS Y RUTAS DE TRANSPORTE

### Instalación, Ejecución e Implementación de OpenStreetMap
Para saber por qué calles debe ir el auto o la persona caminando, implementamos la base de datos libre **OpenStreetMap**. 
OpenStreetMap funciona como un servidor en internet que tiene registradas todas las calles, direcciones y si una calle es de sentido único. Nuestro proyecto se conecta por internet a este servidor y le envía las coordenadas de inicio y fin. El servidor de OpenStreetMap nos devuelve la ruta dibujada para que el autito no atraviese casas ni vaya en contra ruta.

```python
url = f"https://router.project-osrm.org/route/v1/{perfil}/{longitud_1},{latitud_1};{longitud_2},{latitud_2}?overview=full&geometries=polyline"
respuesta = requests.get(url, headers={"User-Agent": "NocheMuseos/1.0"}, timeout=5)
datos = respuesta.json()
```

### Cómo calculamos todas las rutas de movimiento para autos y el peatón
Cuando el usuario quiere ir del Museo A al Museo B en auto o caminando, el programa toma las coordenadas de ambos museos y hace una petición a OpenStreetMap pidiendo el "perfil peatón" o el "perfil auto". Si hay conexión, guardamos la lista de calles que nos da. Si la conexión falla, el programa une los dos puntos con una línea directa de emergencia usando el cálculo de distancia visto en el paso anterior.

### Los modos de transporte, cómo los implementamos e instalamos
En el simulador tenemos tres modos de transporte: Peatón, Auto/Taxi, y Micros/Trufis.
- **Peatón y Auto:** Los implementamos usando el servidor de OpenStreetMap porque pueden ir desde cualquier puerta hasta cualquier otra puerta directamente.
- **Micros/Trufis:** Es mucho más difícil porque los micros tienen líneas fijas y no te recogen en la puerta. Los implementamos leyendo un archivo lleno de rutas fijas y buscando cuál ruta pasa cerca del origen y del destino.

### Rutas del transporte público y paradas, tramos y paradas (Cómo se instaló y de dónde lo conseguimos)
Para conseguir las rutas de los micros y trufis de Cochabamba, descargamos la información libre de la ciudad en un archivo llamado `rutas_trufis.geojson`. Este archivo tiene dibujado por dónde pasa cada línea.
Para incorporarlo al proyecto, hicimos una función que lee este archivo. Luego, para calcular las "Paradas", el sistema busca qué calles del recorrido del micro están a menos de 400 metros de distancia del museo. Así, se crea un tramo dividido en tres pasos: Caminar a la parada, viajar en el micro, y caminar de la parada al museo.

---

## CAPÍTULO IV: CACHÉ, MACROOPERADORES Y BÚSQUEDA

### Cómo desarrollamos e implementamos el Caché para las rutas del peatón y en taxi
Si pedimos miles de rutas a OpenStreetMap por internet, el programa sería muy lento y nos bloquearían. Para solucionarlo, desarrollamos un "Caché" (memoria guardada).
Lo implementamos creando dos archivos de texto en la computadora (`cache_peatonal.json` y `cache_taxi.json`). Cuando el programa necesita una ruta, primero busca en estos archivos locales. Si la ruta ya está guardada, la saca de ahí y es instantáneo. Solo se conecta a internet si la ruta es completamente nueva, y una vez que la descarga, la guarda en los archivos para el futuro.

### Instalación e Implementación de Macrooperadores
Cuando una persona viaja en micro, hace varias cosas: Camina, sube al micro, viaja, y camina al museo. Si el programa calculara esto como cosas separadas, se confundiría. 
Implementamos un **Macrooperador**, que es una función de código que agrupa estas tres acciones separadas y las convierte en "Un solo gran movimiento matemático" con un costo total y un tiempo total fijo. 

### Cómo creamos el caché para optimizar las operaciones de macrooperadores
Como el Macrooperador de micro necesita saber cómo caminar a las paradas, usa nuestra función de memoria (Caché peatonal) que explicamos arriba. Al tener las caminatas a las paradas ya guardadas en el disco duro, el Macrooperador se arma de manera inmediata sin perder tiempo conectándose a internet, haciendo que armar el viaje en micro sea ultra rápido.

### Instalación e Implementación de Motores de Búsqueda
Para encontrar el mejor recorrido visitando muchos museos, implementamos un Motor de Búsqueda de Inteligencia Artificial llamado **Búsqueda en Profundidad**. 
Este motor funciona explorando una opción de camino hasta el final (Ej. Museo A -> B -> C). Si ese camino no es bueno, retrocede un paso y prueba otra combinación (A -> B -> D). Así revisa las combinaciones hasta encontrar la mejor.

### Instalación e Implementación de Poda
Revisar todas las combinaciones posibles es muy lento. Si elegimos muchos museos, la computadora podría tardar años. Para evitar esto, implementamos la **Poda**. 
La poda es un código que revisa en todo momento si el dinero o el tiempo gastado hasta ahora ya es mayor al que tiene el usuario. Si ya nos pasamos del límite de tiempo, la Poda corta inmediatamente ese camino y la computadora ya no sigue revisando los museos que faltaban en ese recorrido, ahorrando millones de operaciones.

### Instalación e Implementación de Filtrado y Despliegue de Resultados
Después de hacer la Búsqueda y la Poda, pueden quedar varios caminos válidos. Para mostrar el mejor, implementamos un algoritmo de Filtrado. 
El filtrado cuenta cuántos museos logró visitar cada camino válido. Luego descarta los caminos más pobres y se queda únicamente con la ruta que logró visitar la mayor cantidad de museos. Ese resultado ganador es el que se dibuja en la pantalla y en el mapa.

---

## CAPÍTULO V: ARQUITECTURA MULTIAGENTE Y TAXONOMÍA

En Inteligencia Artificial, un "Agente" es un pequeño programa independiente que percibe cosas y toma decisiones. Implementamos 4 tipos diferentes de agentes que trabajan juntos (Arquitectura Multiagente). Se instalaron usando "Hilos" de programación para que trabajen en paralelo.

### 1. Agentes Reactivos Simples (El Agente Guía)
Este tipo de agente solo reacciona a lo que pasa en el momento sin pensar en el futuro ni en el pasado. Su regla es "Si pasa esto, hago esto".
**Cómo funciona en nuestro proyecto:** Es el agente que te recibe en la puerta del museo. Cuando nota que el auto llegó a un museo, su única reacción es cobrar el dinero de la entrada y hacer pasar el tiempo de la visita en el reloj.

### 2. Agentes Reactivos Basados en Modelos (El Agente de Movimiento)
Este agente es más avanzado porque entiende cómo funcionan las reglas físicas del mundo interior.
**Cómo funciona en nuestro proyecto:** Es el encargado de mover el marcador del auto en el mapa. Sabe a qué velocidad va el auto, sabe cuánta distancia hay y calcula en qué coordenada del mapa debería dibujarse el auto cada segundo para simular movimiento continuo.

### 3. Agentes Basados en Objetivos (El Agente de Transporte)
Este agente tiene una meta clara y planifica varios pasos por adelantado para cumplirla, sin importar si los pasos cambian.
**Cómo funciona en nuestro proyecto:** Es el agente que tiene toda la ruta ganadora. Sabe que tiene que ir por varios museos. Le da órdenes al Agente de Movimiento para avanzar al primer museo, espera a que termine, y luego sigue con el siguiente museo hasta cumplir la ruta completa.

### 4. Agentes Basados en Utilidad (El Agente Buscador Supremo)
Este es el agente más inteligente. Sabe que hay muchas formas de lograr la meta, pero busca la que dé mayor felicidad o puntaje útil.
**Cómo funciona en nuestro proyecto:** Es el que ejecuta el Motor de Búsqueda y la Poda. Revisa todos los caminos posibles y le da más "puntaje" a la ruta que visita más museos gastando menos tiempo y dinero.

---

## CAPÍTULO VI: MANUAL OPERATIVO COMPLETO PARA EL USUARIO DEL SIMULADOR

Para utilizar el software "Noche de Museos Cochabamba", siga estos pasos:

1. **Definir el Origen y Recursos:** En la parte izquierda de la pantalla, ingrese el Presupuesto (en dinero) y el Tiempo libre (en minutos) que tiene para todo el recorrido de la noche.
2. **Definir las Velocidades:** En la misma columna, escriba a qué velocidad caminará y a qué velocidad viaja en auto. Elija también un "Acelerador" (Ej. x10) para que la animación del auto en el mapa sea rápida y no tenga que esperar tiempo real.
3. **Seleccionar los Museos:** Marque con un visto bueno las casillas de los museos que le gustaría visitar. Puede seleccionar desde 2 hasta más de 10 museos.
4. **Calcular la Ruta:** Presione el botón azul "Calcular". El sistema mostrará en la caja de texto negra debajo cómo el algoritmo va "Podando" las rutas que son muy caras o tardan mucho.
5. **Iniciar el Recorrido Visual:** Si la computadora encuentra una ruta exitosa, el botón verde "Iniciar" se habilitará. Presiónelo para ver cómo el marcador se mueve por las calles de Cochabamba en el mapa interactivo de la derecha, visitando cada museo paso a paso.
6. **Ver el Resultado:** Podrá ver las líneas rojas (viaje en auto), líneas punteadas (caminata) o líneas moradas (viaje en micro) dibujadas en el mapa, mientras los indicadores de arriba le muestran el dinero y tiempo restante.
