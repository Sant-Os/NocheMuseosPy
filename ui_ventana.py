import os
import json
import folium
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QPushButton, 
                             QListWidget, QTextEdit, QMessageBox, QGroupBox, 
                             QLineEdit, QListWidgetItem, QComboBox, QApplication,
                             QCheckBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl, pyqtSignal, Qt, QUrlQuery
from geopy.geocoders import Nominatim
from configuracion import MUSEOS
from agentes_ia import AgenteTransporte, AgenteGuia, AgenteBuscador

class InterfazMapaWeb(QWebEnginePage):
    clic_mapa_senal = pyqtSignal(float, float)
    def acceptNavigationRequest(self, url, tipo_navegacion, es_marco_principal):
        if url.scheme() == "pyqt" and url.host() == "mapclick":
            parametros = QUrlQuery(url)
            latitud = float(parametros.queryItemValue("lat"))
            longitud = float(parametros.queryItemValue("lon"))
            self.clic_mapa_senal.emit(latitud, longitud)
            return False
        return super().acceptNavigationRequest(url, tipo_navegacion, es_marco_principal)

    def javaScriptConsoleMessage(self, nivel, mensaje, linea, id_fuente):
        pass

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

    def construir_interfaz(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        diseno_principal = QHBoxLayout(widget_central)
        diseno_izquierdo = QVBoxLayout()
        diseno_izquierdo.setContentsMargins(10, 10, 10, 10)
        
        grupo_entradas = QGroupBox("1. Origen y Presupuesto")
        formulario = QVBoxLayout()
        formulario.addWidget(QLabel("Punto de partida (o HAZ CLIC EN EL MAPA):"))
        caja_origen = QHBoxLayout()
        self.campo_origen = QLineEdit()
        self.campo_origen.setPlaceholderText("Ej. Plaza Cala Cala")
        caja_origen.addWidget(self.campo_origen)
        self.boton_geolocalizar = QPushButton("Origen")
        self.boton_geolocalizar.setStyleSheet("background-color: #607D8B; color: white; padding: 4px 15px; font-weight: bold;")
        self.boton_geolocalizar.clicked.connect(self.establecer_origen)
        caja_origen.addWidget(self.boton_geolocalizar)
        formulario.addLayout(caja_origen)
        
        caja_presupuesto = QHBoxLayout()
        caja_presupuesto.addWidget(QLabel("Presupuesto (Bs):"))
        self.selector_presupuesto = QSpinBox()
        self.selector_presupuesto.setRange(0, 5000)
        self.selector_presupuesto.setValue(0)
        caja_presupuesto.addWidget(self.selector_presupuesto)
        caja_presupuesto.addWidget(QLabel("Tiempo Total (min):"))
        self.selector_tiempo = QSpinBox()
        self.selector_tiempo.setRange(0, 1440)
        self.selector_tiempo.setValue(0)
        caja_presupuesto.addWidget(self.selector_tiempo)
        formulario.addLayout(caja_presupuesto)
        grupo_entradas.setLayout(formulario)
        diseno_izquierdo.addWidget(grupo_entradas)
        
        grupo_fisica = QGroupBox("2. Simulación")
        formulario_fisica = QVBoxLayout()
        fila_1 = QHBoxLayout()
        fila_1.addWidget(QLabel("Velocidad Auto (km/h):"))
        self.selector_vauto = QSpinBox()
        self.selector_vauto.setRange(10, 150)
        self.selector_vauto.setValue(40)
        fila_1.addWidget(self.selector_vauto)
        fila_1.addWidget(QLabel("Vel. a Pie (km/h):"))
        self.selector_vpie = QSpinBox()
        self.selector_vpie.setRange(1, 15)
        self.selector_vpie.setValue(5)
        fila_1.addWidget(self.selector_vpie)
        formulario_fisica.addLayout(fila_1)
        
        fila_2 = QHBoxLayout()
        fila_2.addWidget(QLabel("Visita a Museos (min):"))
        self.selector_vmuseo = QSpinBox()
        self.selector_vmuseo.setRange(0, 120)
        self.selector_vmuseo.setValue(0)
        fila_2.addWidget(self.selector_vmuseo)
        fila_2.addWidget(QLabel("Acelerar Simulación:"))
        self.combo_acelerador = QComboBox()
        self.combo_acelerador.addItems(["x1", "x2", "x5", "x10", "x15", "x20", "x25"])
        self.combo_acelerador.setCurrentIndex(0)
        fila_2.addWidget(self.combo_acelerador)
        formulario_fisica.addLayout(fila_2)
        grupo_fisica.setLayout(formulario_fisica)
        diseno_izquierdo.addWidget(grupo_fisica)
        
        grupo_transporte = QGroupBox("3. Modos de Transporte Permitidos")
        formulario_transporte = QHBoxLayout()
        self.check_pie = QCheckBox("Pie")
        self.check_pie.setChecked(True)
        self.check_taxi = QCheckBox("Taxi")
        self.check_taxi.setChecked(True)
        self.check_micro = QCheckBox("Micro")
        self.check_micro.setChecked(True)
        formulario_transporte.addWidget(self.check_pie)
        formulario_transporte.addWidget(self.check_taxi)
        formulario_transporte.addWidget(self.check_micro)
        grupo_transporte.setLayout(formulario_transporte)
        diseno_izquierdo.addWidget(grupo_transporte)
        
        diseno_izquierdo.addWidget(QLabel("4. Museos:"))
        self.lista_interfaz_museos = QListWidget()
        self.lista_interfaz_museos.setMaximumHeight(200)
        
        item_seccion1 = QListWidgetItem("--- RUTA PEATONAL ---")
        item_seccion1.setFlags(Qt.NoItemFlags)
        fuente = item_seccion1.font()
        fuente.setBold(True)
        item_seccion1.setFont(fuente)
        item_seccion1.setForeground(Qt.blue)
        self.lista_interfaz_museos.addItem(item_seccion1)
        
        nombres_museos = list(MUSEOS.keys())
        for m in nombres_museos[:10]:
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_interfaz_museos.addItem(item)
            
        item_seccion2 = QListWidgetItem("--- RUTA MÓVIL ---")
        item_seccion2.setFlags(Qt.NoItemFlags)
        item_seccion2.setFont(fuente)
        item_seccion2.setForeground(Qt.blue)
        self.lista_interfaz_museos.addItem(item_seccion2)
        
        for m in nombres_museos[10:]:
            item = QListWidgetItem(m)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.lista_interfaz_museos.addItem(item)
            
        self.lista_interfaz_museos.itemChanged.connect(self.actualizar_checkbox_mapa)
        diseno_izquierdo.addWidget(self.lista_interfaz_museos)
        
        caja_botones = QHBoxLayout()
        self.boton_calcular = QPushButton("Calcular")
        self.boton_calcular.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 4px 15px; font-size: 13px;")
        self.boton_calcular.clicked.connect(self.empezar_busqueda)
        caja_botones.addWidget(self.boton_calcular)
        
        self.boton_reiniciar = QPushButton("Reiniciar")
        self.boton_reiniciar.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 4px 15px; font-size: 13px;")
        self.boton_reiniciar.clicked.connect(self.reiniciar_todo)
        caja_botones.addWidget(self.boton_reiniciar)
        diseno_izquierdo.addLayout(caja_botones)

        lista_rutas_layout = QVBoxLayout()
        self.lista_resultados = QListWidget()
        self.lista_resultados.setEnabled(False)
        self.lista_resultados.setMaximumHeight(100)
        self.lista_resultados.itemSelectionChanged.connect(self.dibujar_ruta_previa)
        lista_rutas_layout.addWidget(self.lista_resultados)
        
        self.boton_arrancar = QPushButton("Iniciar")
        self.boton_arrancar.setEnabled(False)
        self.boton_arrancar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 20px; font-size: 14px;")
        self.boton_arrancar.clicked.connect(self.iniciar_simulacion)
        lista_rutas_layout.addWidget(self.boton_arrancar)
        diseno_izquierdo.addLayout(lista_rutas_layout)

        caja_marcadores = QHBoxLayout()
        self.etiqueta_tiempo = QLabel("Tiempo: 0.0 min")
        self.etiqueta_tiempo.setStyleSheet("font-size: 14px; font-weight: bold; color: #E91E63;")
        caja_marcadores.addWidget(self.etiqueta_tiempo)
        self.etiqueta_dinero = QLabel("Presupuesto: 0.0 Bs")
        self.etiqueta_dinero.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        caja_marcadores.addWidget(self.etiqueta_dinero)
        diseno_izquierdo.addLayout(caja_marcadores)

        self.consola_registros = QTextEdit()
        self.consola_registros.setReadOnly(True)
        self.consola_registros.setStyleSheet("background-color: #1E1E1E; color: #4CAF50; font-family: Consolas; font-size: 11px;")
        self.consola_registros.setText("Bienvenido al simulador. Configure y calcule rutas.")
        diseno_izquierdo.addWidget(self.consola_registros)
        
        diseno_izquierdo.setStretch(6, 1)
        diseno_izquierdo.setStretch(8, 2)
        widget_izquierdo = QWidget()
        widget_izquierdo.setLayout(diseno_izquierdo)
        widget_izquierdo.setFixedWidth(450)
        diseno_principal.addWidget(widget_izquierdo)

        self.visor_web = QWebEngineView()
        self.pagina_web = InterfazMapaWeb(self.visor_web)
        self.visor_web.setPage(self.pagina_web)
        self.pagina_web.clic_mapa_senal.connect(self.establecer_coordenadas_mapa)
        diseno_principal.addWidget(self.visor_web)

    def reiniciar_todo(self):
        self.coordenada_origen = None
        self.campo_origen.clear()
        self.selector_presupuesto.setValue(0)
        self.selector_tiempo.setValue(0)
        for i in range(self.lista_interfaz_museos.count()):
            item = self.lista_interfaz_museos.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
        self.lista_resultados.clear()
        self.lista_resultados.setEnabled(False)
        self.boton_arrancar.setEnabled(False)
        self.boton_calcular.setEnabled(True)
        self.etiqueta_tiempo.setText("Tiempo: 0.0 min")
        self.etiqueta_dinero.setText("Presupuesto: 0.0 Bs")
        self.consola_registros.clear()
        self.consola_registros.setText("Simulador reiniciado.")
        self.dibujar_mapa()

    def establecer_origen(self):
        direccion = self.campo_origen.text().strip()
        if not direccion:
            QMessageBox.warning(self, "Error", "Ingresa una dirección o haz clic en el mapa.")
            return
        self.consola_registros.append(f"[Geolocalizador] Buscando: {direccion}...")
        try:
            localizacion = self.geolocalizador.geocode(f"{direccion}, Cochabamba, Bolivia", timeout=10)
            if localizacion:
                self.coordenada_origen = (localizacion.latitude, localizacion.longitude)
                self.consola_registros.append(f"[Geolocalizador] Origen fijado en: {self.coordenada_origen}")
                self.dibujar_mapa()
            else:
                self.consola_registros.append("[Geolocalizador] No se encontró la dirección.")
                QMessageBox.warning(self, "Error", "No se encontró la dirección. Intenta de nuevo o usa el mapa.")
        except Exception as error:
            self.consola_registros.append(f"[Geolocalizador] Error: {error}")

    def establecer_coordenadas_mapa(self, latitud, longitud):
        self.coordenada_origen = (latitud, longitud)
        self.campo_origen.setText(f"{latitud:.5f}, {longitud:.5f}")
        self.consola_registros.append(f"[Mapa] Origen fijado en: {self.coordenada_origen}")
        self.dibujar_mapa()

    def dibujar_mapa(self, ruta_dibujar=None):
        centro_mapa = self.coordenada_origen if self.coordenada_origen else [-17.3895, -66.1568]
        mapa_folium = folium.Map(location=centro_mapa, zoom_start=14, control_scale=True, zoom_control=True, dragging=True)
        
        js_movimiento = """
        <script>
        var movingMarker = null;
        var traveledLines = [];
        var currentTraveledLine = null;
        var mapInstance = null;
        var customIcons = {};

        function getIconHtml(color) {
            return `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 3px rgba(0,0,0,0.5);"></div>`;
        }

        setTimeout(function(){
            for (var key in window) {
                if (key.startsWith('map_') && window[key] instanceof L.Map) {
                    mapInstance = window[key];
                    break;
                }
            }
            mapInstance.on('click', function(e) {
                window.location.href = "pyqt://mapclick?lat=" + e.latlng.lat + "&lon=" + e.latlng.lng;
            });
            
            document.querySelectorAll('.leaflet-marker-icon').forEach(function(icon) {
                if(icon.getAttribute('data-museum-name')) {
                    var title = icon.getAttribute('data-museum-name');
                    if(window.museumColors && window.museumColors[title]) {}
                }
            });
        }, 1000);

        window.startNewTraveledLine = function(color, isDashed) {
            if (!mapInstance) return;
            var options = {color: color, weight: 6, opacity: 0.8};
            if (isDashed) {
                options.dashArray = '10, 10';
            }
            currentTraveledLine = L.polyline([], options).addTo(mapInstance);
            traveledLines.push(currentTraveledLine);
        };

        window.updateMovingMarker = function(lat, lon, color) {
            if (!mapInstance) return;
            var latlng = [lat, lon];
            if (!customIcons[color]) {
                customIcons[color] = L.divIcon({
                    className: 'custom-div-icon',
                    html: getIconHtml(color),
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });
            }
            if (movingMarker) {
                movingMarker.setLatLng(latlng);
                movingMarker.setIcon(customIcons[color]);
            } else {
                movingMarker = L.marker(latlng, {
                    icon: customIcons[color],
                    zIndexOffset: 1000
                }).addTo(mapInstance);
            }
            if (currentTraveledLine) {
                currentTraveledLine.addLatLng(latlng);
            }
        };

        window.removeMovingMarker = function() {
            if (movingMarker && mapInstance) {
                mapInstance.removeLayer(movingMarker);
                movingMarker = null;
            }
            traveledLines.forEach(function(line) {
                if(mapInstance) mapInstance.removeLayer(line);
            });
            traveledLines = [];
            currentTraveledLine = null;
        };

        window.updateMuseumMarker = function(museumName, color) {
            if (!mapInstance) return;
            mapInstance.eachLayer(function(layer) {
                if (layer.options && layer.options.title === museumName) {
                    var newIcon = L.AwesomeMarkers.icon({
                        icon: 'info-sign',
                        markerColor: color,
                        prefix: 'glyphicon'
                    });
                    layer.setIcon(newIcon);
                }
            });
        };
        </script>
        """
        mapa_folium.get_root().html.add_child(folium.Element(js_movimiento))

        if self.coordenada_origen:
            folium.Marker(
                location=self.coordenada_origen,
                popup="Punto de Partida",
                tooltip="Origen",
                icon=folium.Icon(color='black', icon='home')
            ).add_to(mapa_folium)

        museos_seleccionados = []
        for i in range(self.lista_interfaz_museos.count()):
            elemento = self.lista_interfaz_museos.item(i)
            if elemento.flags() & Qt.ItemIsUserCheckable and elemento.checkState() == Qt.Checked:
                museos_seleccionados.append(elemento.text())

        for nombre_museo, coordenadas in MUSEOS.items():
            color_icono = 'green' if nombre_museo in museos_seleccionados else 'red'
            folium.Marker(
                location=coordenadas,
                popup=nombre_museo,
                tooltip=nombre_museo,
                icon=folium.Icon(color=color_icono, icon='info-sign'),
                title=nombre_museo
            ).add_to(mapa_folium)
            
            letra_museo = nombre_museo.split(']')[0] + ']' if ']' in nombre_museo else nombre_museo[:3]
            html_etiqueta = f'<div style="font-size: 11pt; font-weight: bold; color: black; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; white-space: nowrap;">{letra_museo}</div>'
            folium.Marker(
                location=coordenadas,
                icon=folium.DivIcon(html=html_etiqueta, icon_anchor=(-15, 10))
            ).add_to(mapa_folium)

        if ruta_dibujar:
            puntos_encuadre = []
            if self.coordenada_origen: puntos_encuadre.append(self.coordenada_origen)
            
            for segmento in ruta_dibujar['geometrias']:
                geometria_tramo = segmento['geometria']
                modo_transporte = segmento['modo']
                puntos_encuadre.extend(geometria_tramo)
                
                color_pincel = 'red' if modo_transporte == 'Auto' else 'blue'
                estilo_linea = None
                if modo_transporte == 'Pie':
                    color_pincel = 'blue'
                    estilo_linea = '10, 10'
                elif modo_transporte == 'Micro':
                    color_pincel = 'purple'
                elif modo_transporte == 'Micro1':
                    color_pincel = '#800080'
                elif modo_transporte == 'Micro2':
                    color_pincel = '#DA70D6'
                    
                folium.PolyLine(
                    locations=geometria_tramo,
                    color=color_pincel,
                    weight=5 if modo_transporte == 'Pie' else 6,
                    opacity=0.7,
                    dash_array=estilo_linea,
                    tooltip=f"{modo_transporte} a {segmento['destino']}"
                ).add_to(mapa_folium)
                
                if segmento['destino'] in MUSEOS:
                    folium.CircleMarker(
                        location=MUSEOS[segmento['destino']],
                        radius=15,
                        color='orange',
                        fill=True,
                        fill_color='orange',
                        fillOpacity=0.8,
                        tooltip=f"Parada: {segmento['destino']}"
                    ).add_to(mapa_folium)

            if puntos_encuadre:
                mapa_folium.fit_bounds(puntos_encuadre, padding=[40, 40])
        else:
            archivo_rutas_trufis = "rutas_trufis.geojson"
            if os.path.exists(archivo_rutas_trufis):
                folium.GeoJson(
                    archivo_rutas_trufis,
                    name="Rutas de Transporte",
                    style_function=lambda feature: {
                        'color': 'gray',
                        'weight': 2,
                        'opacity': 0.3
                    }
                ).add_to(mapa_folium)
                
                try:
                    with open(archivo_rutas_trufis, "r", encoding="utf-8") as f:
                        datos_json_trufis = json.load(f)
                        for elemento in datos_json_trufis.get("features", []):
                            geometria = elemento.get("geometry", {})
                            if geometria.get("type") == "LineString":
                                coord_puntos = geometria.get("coordinates", [])
                                if len(coord_puntos) >= 2:
                                    inicio_gps = [coord_puntos[0][1], coord_puntos[0][0]]
                                    fin_gps = [coord_puntos[-1][1], coord_puntos[-1][0]]
                                    nombre_linea_bus = elemento.get("properties", {}).get("linea", "Desconocida")
                                    
                                    folium.CircleMarker(
                                        location=inicio_gps, radius=4, color='orange',
                                        fill=True, fill_color='orange', fillOpacity=0.9,
                                        tooltip=f"Parada: {nombre_linea_bus}"
                                    ).add_to(mapa_folium)
                                    
                                    folium.CircleMarker(
                                        location=fin_gps, radius=4, color='orange',
                                        fill=True, fill_color='orange', fillOpacity=0.9,
                                        tooltip=f"Parada: {nombre_linea_bus}"
                                    ).add_to(mapa_folium)
                except Exception:
                    pass

        ruta_html = os.path.abspath("mapa_museos.html")
        mapa_folium.save(ruta_html)
        self.visor_web.load(QUrl.fromLocalFile(ruta_html))
        try:
            self.visor_web.loadFinished.disconnect(self.actualizar_checkbox_mapa)
        except TypeError:
            pass
        self.visor_web.loadFinished.connect(self.actualizar_checkbox_mapa)

    def actualizar_checkbox_mapa(self):
        for i in range(self.lista_interfaz_museos.count()):
            elemento = self.lista_interfaz_museos.item(i)
            nombre_museo = elemento.text()
            if elemento.flags() & Qt.ItemIsUserCheckable:
                color = 'green' if elemento.checkState() == Qt.Checked else 'red'
                script_js = f"if(window.updateMuseumMarker) window.updateMuseumMarker('{nombre_museo}', '{color}');"
                self.visor_web.page().runJavaScript(script_js)

    def empezar_busqueda(self):
        if not self.coordenada_origen:
            QMessageBox.warning(self, "Atención", "Fija un punto de origen (clic en mapa o texto).")
            return
        museos_seleccionados = []
        for i in range(self.lista_interfaz_museos.count()):
            elemento = self.lista_interfaz_museos.item(i)
            if (elemento.flags() & Qt.ItemIsUserCheckable) and elemento.checkState() == Qt.Checked:
                museos_seleccionados.append(elemento.text())
        if not museos_seleccionados: return
        self.boton_calcular.setEnabled(False)
        self.tiempo_disponible = self.selector_tiempo.value()
        self.presupuesto_disponible = self.selector_presupuesto.value()
        self.etiqueta_tiempo.setText(f"Tiempo: {self.tiempo_disponible:.1f} min")
        self.etiqueta_dinero.setText(f"Presupuesto: {self.presupuesto_disponible:.1f} Bs")
        self.consola_registros.clear()
        self.consola_registros.append(f"[Buscador] Buscando rutas para {len(museos_seleccionados)} museos...")
        permitir_pie = self.check_pie.isChecked()
        permitir_taxi = self.check_taxi.isChecked()
        permitir_micro = self.check_micro.isChecked()
        
        self.hilo_buscador = AgenteBuscador(
            self.coordenada_origen, museos_seleccionados, self.presupuesto_disponible,
            self.tiempo_disponible, self.selector_vauto.value(), 
            self.selector_vpie.value(), self.selector_vmuseo.value(),
            permitir_pie, permitir_taxi, permitir_micro
        )
        self.hilo_buscador.progreso_senal.connect(self.consola_registros.append)
        self.hilo_buscador.finalizado_senal.connect(self.rutas_calculadas)
        self.hilo_buscador.error_senal.connect(lambda e: self.consola_registros.append(f"Error: {e}"))
        self.hilo_buscador.start()

    def rutas_calculadas(self, opciones_validas):
        self.boton_calcular.setEnabled(True)
        if not opciones_validas:
            self.consola_registros.append("¡NINGUNA ALTERNATIVA ES VÁLIDA! Falta tiempo o presupuesto máximo.")
            QMessageBox.critical(self, "Ruta Imposible", "No alcanza el dinero o el tiempo para ninguna de las opciones. Modifica tus restricciones.")
            return
            
        self.lista_resultados.clear()
        
        for ruta in opciones_validas:
            num_operacion = ruta.get('numero_operacion', '?')
            texto_lista = f"Operación Validada #{num_operacion} ({ruta['cantidad_museos']} Museos)\n   ↳ {ruta['nombre_ruta']} | Costo: {ruta['dinero_gastado']:.1f} Bs | Tiempo: {ruta['minutos_gastados']:.1f} min"
            elemento = QListWidgetItem(texto_lista)
            elemento.setData(Qt.UserRole, ruta)
            self.lista_resultados.addItem(elemento)
            
        self.lista_resultados.setEnabled(True)
        self.boton_arrancar.setEnabled(True)
        self.consola_registros.append(f"¡Se listaron TODAS las {len(opciones_validas)} opciones viables que visitan el máximo de museos posible en el orden original!")
        self.consola_registros.append("Selecciona una ruta de la lista y presiona Iniciar.")
        
    def dibujar_ruta_previa(self):
        elemento_seleccionado = self.lista_resultados.currentItem()
        if not elemento_seleccionado: return
        datos_ruta_optima = elemento_seleccionado.data(Qt.UserRole)
        self.dibujar_mapa(datos_ruta_optima)
        
    def iniciar_simulacion(self):
        elemento_seleccionado = self.lista_resultados.currentItem()
        if not elemento_seleccionado: return
        datos_ruta_optima = elemento_seleccionado.data(Qt.UserRole)
        self.boton_calcular.setEnabled(False)
        self.boton_arrancar.setEnabled(False)
        self.lista_resultados.setEnabled(False)
        self.consola_registros.append(f"\nOpción seleccionada: {datos_ruta_optima['nombre_ruta']}")
        vehiculos_str = " -> ".join(datos_ruta_optima['vehiculos_usados'])
        self.consola_registros.append(f"Modos de Transporte elegidos: {vehiculos_str}")
        self.dibujar_mapa(datos_ruta_optima)
        self.guia = AgenteGuia(self, self.restar_minutos, self.restar_plata, self.selector_vmuseo.value())
        acelerador = int(self.combo_acelerador.currentText().replace("x", ""))
        self.consola_registros.append("\n--- INICIANDO SIMULACIÓN ANIMADA ---")
        self.transporte.arrancar_motor(
            datos_ruta_optima, 
            self.selector_vauto.value(), 
            self.selector_vpie.value(), 
            acelerador,
            self.guia.aterrizaje
        )

    def restar_plata(self, cantidad, motivo):
        if cantidad > 0:
            self.presupuesto_disponible -= cantidad
            self.etiqueta_dinero.setText(f"Presupuesto: {self.presupuesto_disponible:.1f} Bs")
            self.consola_registros.append(f"[Dinero] -{cantidad} Bs por {motivo}. (Quedan {self.presupuesto_disponible} Bs)")

    def restar_minutos(self, reduccion):
        self.tiempo_disponible -= reduccion
        self.etiqueta_tiempo.setText(f"Tiempo: {self.tiempo_disponible:.1f} min")
