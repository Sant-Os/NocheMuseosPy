import sys
import os
sys.dont_write_bytecode = True
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_ventana import VentanaPrincipal

if __name__ == "__main__":
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    aplicacion = QApplication(sys.argv)
    
    aplicacion.setStyle("Fusion")
    fuente_texto = aplicacion.font()
    fuente_texto.setPointSize(10)
    aplicacion.setFont(fuente_texto)

    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(aplicacion.exec_())
