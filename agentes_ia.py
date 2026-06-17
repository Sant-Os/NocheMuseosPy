import time
import math
import itertools
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from configuracion import calcular_distancia_directa, obtener_ruta_vehiculo, ENTRADAS, MUSEOS, MATRIZ_TRANSPORTE, LINEAS_TRUFIS

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
            coordenadas = {'Origen': self.coordenada_origen}
            for museo in self.lista_museos: 
                coordenadas[museo] = MUSEOS[museo]

            def abreviar(nombre):
                return nombre[:3] if nombre.startswith('[') else nombre

            rutas_encontradas = []
            cantidad_museos = len(self.lista_museos)
            total_combinaciones = sum(math.factorial(cantidad_museos) // math.factorial(cantidad_museos - k) for k in range(1, cantidad_museos + 1))
            self.contador_exploracion = 0

            def calcular_segmento(nodo_a, nodo_b, coord_a, coord_b, tipo_viaje, distancia_lineal):
                segmentos = []
                

                if tipo_viaje == 'Pie':
                    distancia_total_tramo = distancia_lineal * 1.1 
                    tiempo_total_tramo = distancia_total_tramo / self.velocidad_caminando
                    _, _, geom_p = obtener_ruta_vehiculo(coord_a, coord_b, perfil="peaton")
                    geom = geom_p if geom_p else [coord_a, coord_b]
                    precio_pasaje = 0.0
                    impresion_modo = "Pie"
                    segmentos.append({'origen': nodo_a, 'destino': nodo_b, 'modo': 'Pie', 'distancia': distancia_total_tramo, 'tiempo': tiempo_total_tramo, 'geometria': geom, 'costo': precio_pasaje})
                

                elif tipo_viaje == 'Auto':
                    d_vehiculo, t_vehiculo, geom_vehiculo = obtener_ruta_vehiculo(coord_a, coord_b, perfil="driving")
                    if geom_vehiculo is None:
                        distancia_total_tramo = distancia_lineal * 1.3
                        geom = [coord_a, coord_b]
                        tiempo_total_tramo = distancia_total_tramo / self.velocidad_coche
                    else:
                        distancia_total_tramo = d_vehiculo
                        geom = geom_vehiculo
                        tiempo_total_tramo = t_vehiculo
                    precio_pasaje = self.costo_coche * distancia_total_tramo
                    impresion_modo = "Auto"
                    segmentos.append({'origen': nodo_a, 'destino': nodo_b, 'modo': 'Auto', 'distancia': distancia_total_tramo, 'tiempo': tiempo_total_tramo, 'geometria': geom, 'costo': precio_pasaje})
                

                elif tipo_viaje == 'Micro':
                    info_ruta = MATRIZ_TRANSPORTE[nodo_a][nodo_b]
                    id_linea = info_ruta['linea']
                    ruta_fisica = LINEAS_TRUFIS.get(id_linea)
                    
                    if ruta_fisica:
                        def proyectar_punto(punto):
                            mejor_idx, min_d = -1, float('inf')
                            for k, p_ruta in enumerate(ruta_fisica):
                                d = calcular_distancia_directa(punto, p_ruta)
                                if d < min_d: min_d, mejor_idx = d, k
                            return ruta_fisica[mejor_idx], mejor_idx, min_d
                            
                        def ubicar_paradas(punto_inicio, punto_fin, coordenadas_ruta):
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
                        
                        tiempo_total_tramo = tiempo_w1 + tiempo_micro + tiempo_w2
                        distancia_total_tramo = dist_w1 + dist_micro + dist_w2
                        impresion_modo = f"Micro ({id_linea})"
                        
                        segmentos.extend([
                            {'origen': nodo_a, 'destino': f'Parada({abreviar(nodo_a)})', 'modo': 'Pie', 'distancia': dist_w1, 'tiempo': tiempo_w1, 'geometria': geom_caminata_1, 'costo': 0.0},
                            {'origen': f'Parada({abreviar(nodo_a)})', 'destino': f'Parada({abreviar(nodo_b)})', 'modo': 'Micro', 'distancia': dist_micro, 'tiempo': tiempo_micro, 'geometria': geom_micro, 'costo': precio_pasaje},
                            {'origen': f'Parada({abreviar(nodo_b)})', 'destino': nodo_b, 'modo': 'Pie', 'distancia': dist_w2, 'tiempo': tiempo_w2, 'geometria': geom_caminata_2, 'costo': 0.0}
                        ])
                    else:
                        precio_pasaje = info_ruta['costo_pasaje']
                        _, _, geom_vehicular = obtener_ruta_vehiculo(coord_a, coord_b, perfil="driving")
                        geom = geom_vehicular if geom_vehicular else [coord_a, coord_b]
                        distancia_total_tramo = distancia_lineal * 1.3
                        tiempo_total_tramo = distancia_total_tramo / (20.0 / 60.0)
                        impresion_modo = "Micro"
                        segmentos.append({'origen': nodo_a, 'destino': nodo_b, 'modo': 'Micro', 'distancia': distancia_total_tramo, 'tiempo': tiempo_total_tramo, 'geometria': geom, 'costo': precio_pasaje})
                
                return segmentos, precio_pasaje, tiempo_total_tramo, distancia_total_tramo, impresion_modo

            def explorar_opciones(camino_actual, museos_faltantes, gasto_acumulado, reloj_acumulado, trazos_ruta, lineas_registro, modo_fijo):
                if gasto_acumulado > self.presupuesto_maximo or reloj_acumulado > self.tiempo_maximo:
                    m = len(museos_faltantes)
                    ramas_cortadas = sum(math.factorial(m) // math.factorial(m - k) for k in range(1, m + 1)) + 1 if m > 0 else 1
                    self.contador_exploracion += ramas_cortadas
                    
                    texto_camino = [abreviar(x) for x in camino_actual] + [abreviar(m) for m in museos_faltantes] + ['Origen']
                    cabecera = f"\nOpcion [{self.contador_exploracion}/{total_combinaciones}]: [{' -> '.join(texto_camino)}]"
                    registro_final = [cabecera, "-" * 65] + list(lineas_registro)
                    registro_final.append(f"└─ PODA: Costo={gasto_acumulado:.1f} Bs | Tiempo={reloj_acumulado:.1f} min | Omitidas: {ramas_cortadas}")
                    self.progreso_senal.emit("\n".join(registro_final))
                    return

                if len(camino_actual) > 1:
                    origen_tramo = camino_actual[-1]
                    destino_tramo = 'Origen'
                    coord_origen_tramo, coord_destino_tramo = coordenadas[origen_tramo], coordenadas['Origen']
                    distancia_recta = calcular_distancia_directa(coord_origen_tramo, coord_destino_tramo)
                    
                    opciones_transporte = []
                    if modo_fijo == 'Pie': opciones_transporte.append('Pie')
                    elif modo_fijo == 'Auto': opciones_transporte.append('Auto')
                    elif modo_fijo == 'Micro':
                        if origen_tramo in MATRIZ_TRANSPORTE and destino_tramo in MATRIZ_TRANSPORTE[origen_tramo] and MATRIZ_TRANSPORTE[origen_tramo][destino_tramo]['costo_pasaje'] < float('inf'):
                            opciones_transporte.append('Micro')
                        
                    for tipo_transporte in opciones_transporte:
                        self.contador_exploracion += 1
                        
                        nuevos_segmentos, costo_tramo, tiempo_tramo, distancia_km, texto_modo = calcular_segmento(origen_tramo, destino_tramo, coord_origen_tramo, coord_destino_tramo, tipo_transporte, distancia_recta)

                        costo_total_evaluado = gasto_acumulado + costo_tramo
                        tiempo_total_evaluado = reloj_acumulado + tiempo_tramo
                        
                        texto_camino = [abreviar(x) for x in camino_actual] + ['Origen']
                        cabecera = f"\nOpcion [{self.contador_exploracion}/{total_combinaciones}]: [{' -> '.join(texto_camino)}] usando {texto_modo}"
                        registro_final = [cabecera, "-" * 65] + list(lineas_registro)
                        registro_final.append(f"|  -> {abreviar(destino_tramo):<15} | {distancia_km:>6.2f} km | {tiempo_tramo:>5.1f} min | {texto_modo} ({costo_tramo:.1f} Bs)")
                        
                        if costo_total_evaluado <= self.presupuesto_maximo and tiempo_total_evaluado <= self.tiempo_maximo:
                            registro_final.append(f"└─ TOTALES: {costo_total_evaluado:.1f} Bs | {tiempo_total_evaluado:.1f} min | ✔ CORRECTA ({len(camino_actual)-1} Museos)")
                            self.progreso_senal.emit("\n".join(registro_final))
                            
                            ruta_definitiva = camino_actual + ['Origen']
                            trazos_definitivos = trazos_ruta + nuevos_segmentos
                            lista_modos = [segmento['modo'] for segmento in trazos_definitivos]
                            rutas_encontradas.append({
                                'nombre_ruta': " -> ".join([abreviar(x) for x in camino_actual[1:]]),
                                'cantidad_museos': len(camino_actual) - 1,
                                'secuencia': ruta_definitiva, 'vehiculos_usados': lista_modos, 'dinero_gastado': costo_total_evaluado,
                                'minutos_gastados': tiempo_total_evaluado, 'geometrias': trazos_definitivos, 'museos_objetivo': self.lista_museos
                            })
                        else:
                            if not museos_faltantes:
                                registro_final.append(f"└─ TOTALES: {costo_total_evaluado:.1f} Bs | {tiempo_total_evaluado:.1f} min | ✘ DESCARTADA")
                                self.progreso_senal.emit("\n".join(registro_final))

                if not museos_faltantes:
                    return

                for siguiente_museo in museos_faltantes:
                    origen_tramo = camino_actual[-1]
                    destino_tramo = siguiente_museo
                    coord_origen_tramo, coord_destino_tramo = coordenadas[origen_tramo], coordenadas[destino_tramo]
                    distancia_recta = calcular_distancia_directa(coord_origen_tramo, coord_destino_tramo)
                    
                    opciones_transporte = []
                    if modo_fijo == 'Pie': opciones_transporte.append('Pie')
                    elif modo_fijo == 'Auto': opciones_transporte.append('Auto')
                    elif modo_fijo == 'Micro':
                        if origen_tramo in MATRIZ_TRANSPORTE and destino_tramo in MATRIZ_TRANSPORTE[origen_tramo] and MATRIZ_TRANSPORTE[origen_tramo][destino_tramo]['costo_pasaje'] < float('inf'):
                            opciones_transporte.append('Micro')

                    for tipo_transporte in opciones_transporte:
                        nuevos_segmentos, costo_tramo, tiempo_tramo, distancia_km, texto_modo = calcular_segmento(origen_tramo, destino_tramo, coord_origen_tramo, coord_destino_tramo, tipo_transporte, distancia_recta)

                        costo_calculado = gasto_acumulado + ENTRADAS[destino_tramo] + costo_tramo
                        tiempo_calculado = reloj_acumulado + self.duracion_visita + tiempo_tramo
                        
                        linea_texto = f"|  -> {abreviar(destino_tramo):<15} | {distancia_km:>6.2f} km | {tiempo_tramo:>5.1f} min | {texto_modo} ({costo_tramo:.1f} Bs)"
                        trazos_combinados = trazos_ruta + nuevos_segmentos
                        
                        sobrantes = [m for m in museos_faltantes if m != siguiente_museo]
                        explorar_opciones(camino_actual + [siguiente_museo], sobrantes, costo_calculado, tiempo_calculado, trazos_combinados, lineas_registro + [linea_texto], modo_fijo)

            if self.permitir_pie:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Pie')
            if self.permitir_taxi:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Auto')
            if self.permitir_micro:
                explorar_opciones(['Origen'], self.lista_museos, 0.0, 0.0, [], [], 'Micro')
                
            if rutas_encontradas:
                max_museos = max(r['cantidad_museos'] for r in rutas_encontradas)
                rutas_encontradas = [r for r in rutas_encontradas if r['cantidad_museos'] == max_museos]
                rutas_encontradas.sort(key=lambda x: (x['dinero_gastado'], x['minutos_gastados']))
                
            self.finalizado_senal.emit(rutas_encontradas)
        except Exception as error_capturado:
            self.error_senal.emit(str(error_capturado))

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
        self.imprimir(f"Iniciando trayecto en x{acelerador}")
        self.siguiente_movimiento(velocidad_coche, velocidad_caminando, acelerador)
        
    def siguiente_movimiento(self, velocidad_coche=None, velocidad_caminando=None, acelerador=None):
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
            self.imprimir("Destino final alcanzado.")

    def refrescar_pantalla(self, latitud, longitud, transporte):
        color_icono = 'red' if transporte == 'Auto' else 'orange' if transporte == 'Pie' else 'purple'
        self.visor_mapa.page().runJavaScript(f"if(window.updateMovingMarker) updateMovingMarker({latitud}, {longitud}, '{color_icono}');")

    def aterrizaje(self, nombre_destino):
        self.imprimir(f"Vehículo aparcado en {nombre_destino}.")
        self.indice_tramo += 1
        self.evento_llegada(nombre_destino, lambda: self.siguiente_movimiento(self.velocidad_coche, self.velocidad_caminando, self.acelerador))

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
