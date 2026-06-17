# INFORME TÉCNICO COMPLETO: SIMULADOR DE INTELIGENCIA ARTIFICIAL PARA LA NOCHE DE MUSEOS EN COCHABAMBA

## CAPÍTULO 1: INTRODUCCIÓN Y PLANTEAMIENTO DEL PROBLEMA

### 1.1 Contexto del Proyecto
La "Noche de Museos" es uno de los eventos culturales más importantes de la ciudad de Cochabamba, Bolivia. Durante esta jornada, decenas de espacios culturales, galerías y museos abren sus puertas al público en horarios nocturnos. Sin embargo, la amplia distribución geográfica de estos recintos en el entorno urbano (abarcando desde el centro histórico hasta zonas periféricas) representa un problema logístico significativo para los asistentes. 

Los visitantes enfrentan tres limitantes críticas:
1. **El Tiempo:** El evento dura un periodo finito (generalmente entre 4 a 6 horas). Visitar todos los museos es físicamente imposible.
2. **El Presupuesto:** Los ciudadanos disponen de una cantidad finita de recursos económicos. Este dinero debe dividirse entre el pago del transporte público o privado y las entradas a los recintos.
3. **El Transporte:** Desplazarse de un punto a otro en Cochabamba involucra tomar decisiones dinámicas: caminar, tomar un taxi directo, o caminar hacia una avenida para interceptar una línea de transporte público (Trufi o Micro) y luego caminar hacia el destino final.

### 1.2 Formulación del Problema
Este problema se clasifica dentro de las Ciencias de la Computación como una variante del **Problema del Agente Viajero con Restricciones**, con la adición de una red de transporte multimodal. 
Dado un conjunto de $n$ museos, el número de combinaciones de rutas explota matemáticamente. Analizar cada una para encontrar el camino más barato y rápido es imposible para el cerebro humano, y sin optimización algorítmica, también resulta muy pesado para las computadoras modernas.

### 1.3 Objetivos
**Objetivo General:**
Desarrollar un sistema de Inteligencia Artificial basado en Arquitectura Multi-Agente en lenguaje Python que planifique, optimice y simule interactivamente las rutas turísticas para la Noche de Museos en Cochabamba, respetando restricciones de tiempo y presupuesto.

---

## CAPÍTULO 2: MARCO TEÓRICO Y TECNOLÓGICO

### 2.1 Inteligencia Artificial y Taxonomía de Agentes
Un agente inteligente es una entidad computacional autónoma capaz de percibir su entorno y tomar decisiones para maximizar sus posibilidades de éxito. En este proyecto se utilizó un paradigma Multi-Agente donde distintas piezas de código de Python controlan diferentes aspectos lógicos del turista en la ciudad de Cochabamba.

Según la literatura clásica de la Inteligencia Artificial (basada en teóricos como Russell y Norvig), los agentes de nuestro proyecto se clasifican estrictamente de la siguiente manera:

1. **Agente Reactivo Simple (`AgenteGuia`):** Toma decisiones basadas únicamente en la percepción del momento actual, sin recordar el pasado. En nuestro programa, cuando el turista llega a la puerta de un recinto cultural en Cochabamba, este agente reacciona inmediatamente: cobra el valor de la entrada del presupuesto e inicia el temporizador de visita, sin importar de qué museo vino el turista ni hacia dónde irá después.
2. **Agente Reactivo Basado en Modelos (`AnimadorMovimiento`):** Este agente mantiene un estado interno sobre cómo es el mundo (las calles de Cochabamba) y cómo evoluciona la física. Sabe exactamente su coordenada geográfica en el mapa en cada instante y calcula matemáticamente dónde estará su siguiente paso vehicular para lograr un movimiento continuo.
3. **Agente Basado en Objetivos (`AgenteTransporte`):** Posee una meta final: completar el trayecto asignado. Coordina a los otros agentes, indicándoles cuándo dibujar el segmento morado de un Trufi cochabambino y cuándo debe entrar en acción el peaton.
4. **Agente Basado en Utilidad (`AgenteBuscador`):** Es el cerebro central. No se conforma con encontrar "una" ruta cualquiera. Evalúa una función matemática de utilidad para encontrar el camino más óptimo que maximice la recompensa (la mayor cantidad de museos visitados en Cochabamba) gastando la menor cantidad del presupuesto posible.

### 2.2 Tecnologías y Librerías Utilizadas
El ecosistema de la aplicación se construyó íntegramente en Python 3, apalancándose en las siguientes tecnologías de código abierto:
- **Librería de Interfaces Visuales:** Herramienta robusta para la construcción de la Capa Visual mediante ventanas, botones y listas. También inyecta un navegador interno para mostrar el mapa cartográfico local.
- **Motor de Mapas Vectoriales:** Herramienta que permite dibujar un mapa satelital interactivo e inyectar figuras geométricas (paradas de trufi, trazos vehiculares).
- **Servidor de Enrutamiento Abierto:** Sistema remoto que, dadas dos coordenadas, retorna por cuáles calles debe transitar un vehículo respetando los sentidos de circulación en Cochabamba.
- **Matemática Esférica (Haversine):** Debido a que la tierra es una esfera, no se puede usar el Teorema de Pitágoras clásico. Se utiliza esta fórmula para encontrar la distancia real en kilómetros.

---

## CAPÍTULO 3: ARQUITECTURA DEL SISTEMA (EXPLICACIÓN DE ARCHIVOS)

El proyecto se estructuró de manera modular. A continuación, se detalla exhaustivamente qué hace cada archivo siguiendo la regla de tres pasos (Teoría, Terminal y Código).

### 3.1. Archivo Inicializador (`main.py`)
- **Teoría:** Es el punto de entrada al programa. Su función es estrictamente de configuración ambiental. Se encarga de forzar el renderizado por software seguro en computadoras Windows para evitar bloqueos visuales al momento de cargar las calles de Cochabamba.
- **Terminal:** `python main.py`
- **Código:**
```python
from PyQt5.QtWidgets import QApplication
from ui_ventana import VentanaPrincipal
import sys

# Bandera para evitar problemas de tarjeta gráfica
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"

aplicacion = QApplication(sys.argv)
ventana = VentanaPrincipal()
ventana.show()
sys.exit(aplicacion.exec_())
```

### 3.2. Archivo de Base de Datos y Memoria (`configuracion.py`)
- **Teoría:** Es el núcleo de los datos estáticos y peticiones externas. Aquí se aloja el diccionario principal con los 23 museos de Cochabamba. También es el responsable de leer los archivos locales de memoria temporal (cachés peatonales y de vehículos) para evitar bloqueos de red al servidor global.
- **Terminal:** `No se ejecuta directamente, es importado por otros archivos.`
- **Código:**
```python
import json

MUSEOS = {
    '[A] Convento Museo Santa Teresa': (-17.389753, -66.157962),
    '[B] Museo Casa Martín Cárdenas': (-17.392648, -66.160518),
    # ... (Más museos de Cochabamba)
}

def obtener_ruta_vehiculo(origen, destino, perfil="vehiculo"):
    # Busca en el archivo local antes de consultar al internet
    memoria = memoria_peaton if perfil == "peaton" else memoria_taxi
    llave = f"{origen[0]},{origen[1]}_{destino[0]},{destino[1]}"
    
    if llave in memoria:
        return memoria[llave]['distancia'], memoria[llave]['geometria']
```

### 3.3. Motores de Inteligencia Artificial (`agentes_ia.py`)
- **Teoría:** El corazón del proyecto. Aquí habitan las matemáticas pesadas y la asincronía. Las cuatro clases definidas en la taxonomía teórica se programaron aquí usando hilos secundarios de procesamiento para no congelar la pantalla principal de la computadora. Utiliza Búsqueda en Profundidad junto a un modelo de "Poda" para descartar caminos que sobrepasan el presupuesto o el tiempo.
- **Terminal:** `No se ejecuta directamente, actúa en segundo plano.`
- **Código:**
```python
from PyQt5.QtCore import QThread

class AgenteBuscador(QThread):
    def explorar_opciones(camino_actual, gasto_acumulado):
        # PODA LÓGICA: Si supera el dinero máximo del usuario, detiene esta rama.
        if gasto_acumulado > self.presupuesto_maximo:
            return 
            
        # ... Lógica para seguir buscando combinaciones ...
```

### 3.4. Archivo de Capa Visual (`ui_ventana.py`)
- **Teoría:** Este archivo agrupa los botones, las listas desplegables de restricciones (Presupuesto y Tiempo), y recibe la señal matemática de los agentes para graficar físicamente sobre el plano de Cochabamba la trayectoria morada, azul o roja correspondiente al transporte.
- **Terminal:** `No se ejecuta directamente, es el cascarón principal.`
- **Código:**
```python
# Extracto del llenado de resultados en la Capa Visual
for ruta in opciones_validas:
    num_operacion = ruta.get('numero_operacion', '?')
    texto_lista = f"Operación Validada #{num_operacion}\n   ↳ {ruta['nombre_ruta']} | Costo: {ruta['dinero_gastado']} Bs"
    self.lista_resultados.addItem(texto_lista)
```

---

## CAPÍTULO 4: SOLUCIONES DE INGENIERÍA Y LÓGICA APLICADA

### 4.1. Solución al comportamiento "Volador" de la Caminata
*Problema detectado:* Las versiones preliminares usaban una distancia pura en línea recta. En el mapa, esto hacía parecer que la persona atravesaba las manzanas diagonalmente (volando sobre los techos de las casas de Cochabamba).
*Solución de Ingeniería:* Se aplicó un multiplicador de distorsión urbana (`x 1.2`). Al tomar la distancia perfecta ortodrómica, el código asume que en el entorno de Cochabamba (calles en damero), el peatón tendrá que bordear las cuadras. Artificialmente se extiende la distancia matemática y se reduce la velocidad peatonal.

### 4.2. Trasbordos Automatizados en Transporte Público
Para que la simulación refleje la decisión humana en Cochabamba, el algoritmo fue instruido de la siguiente forma:
1. Al evaluar la opción "Micro", ubica los vectores físicos de la ruta del trufi local.
2. Mide la caminata inicial hacia la parada de abordaje y la caminata final desde la parada de bajada hacia el museo.
3. Evalúa el peso matemático: El costo no solo son los `3 Bs.` del pasaje, sino que se suma la penalidad por caminar hasta las paradas. Si este tiempo es superior a simplemente tomar un taxi directo o ir caminando, la rama del "Micro" es automáticamente descartada y podada.

### 4.3 Eliminación Total de Dependencias en Grafos Interactivos
Al comienzo, se planteó mapear visualmente todas las combinaciones generadas por la Inteligencia Artificial forzando la creación de cientos de miles de puntos de dibujo interactivos. Esto sobrecargaba el Procesador Central al 100% y saturaba la Memoria Principal.
*Solución:* Se adoptó un patrón totalmente abstracto. Los datos y rutas se modelan estrictamente como variables matemáticas dentro del Motor Lógico, logrando que el programa no consuma memoria excesiva y encuentre las rutas en un abrir y cerrar de ojos.

### 4.4 Precisión Peatonal vs. Vehicular
Se implementó una bifurcación en el Servidor de Enrutamiento en dos perfiles: *vehículo* y *peatón*. Gracias a esto, la IA no asigna un sentido vehicular estricto a un humano caminando (evitando que el peatón rodee la plaza principal porque está yendo en contra-ruta).

### 4.5 Historial de Operaciones Validadas
Debido a que el tiempo humano es limitado, el sistema salva el estado en cada rama válida; si el tiempo caduca, el sistema filtra y despliega **un historial exhaustivo** con aquellas rutas que logran visitar la cantidad máxima de museos posibles. Se inyecta su respectivo "Número de Operación Validada" para una revisión rigurosa del desempeño de la IA.

---

## CAPÍTULO 5: PRUEBAS DE ESTRÉS Y RENDIMIENTO
1. **Prueba de Restricción Monetaria Extrema:** Se redujo el presupuesto del usuario a 5 Bolivianos y se asignó un recorrido de 5 museos. La Inteligencia Artificial falló a propósito en encontrar taxis debido al alto costo, forzando de manera exitosa la combinación de rutas exclusivas a pie y un tramo único de micro, validando la lógica de poda del servidor.
2. **Prueba de Latencia:** Gracias a la persistencia en archivos de almacenamiento temporales, la velocidad de cálculo se redujo de 20.0 segundos a `0.1 segundos` al ejecutarse completamente de manera local, mitigando por completo las limitaciones de las peticiones de red externas.

---

## CAPÍTULO 6: CONCLUSIONES DEL PROYECTO
- **Manejo Efectivo de Restricciones:** Se demostró mediante el lenguaje de programación Python que utilizar búsqueda matemática recursiva junto a reglas de "Poda" estrictas es suficiente para abatir la explosión de posibilidades de la Noche de Museos.
- **Arquitectura Fiable:** La separación entre el Motor Lógico (los cuatro Agentes Inteligentes) y la Capa Visual garantiza que la ventana del programa se mantenga interactiva y no se bloquee mientras las matemáticas masivas se resuelven de fondo en paralelo.
- **Escalabilidad Local:** El uso de almacenamiento en disco en formatos de texto estructurado asegura que si mañana la alcaldía de Cochabamba abre más museos o modifica el recorrido del evento, el sistema puede recalcular e ingerir la nueva configuración instantáneamente.
