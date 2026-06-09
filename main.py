import sys
sys.dont_write_bytecode = True
from PyQt5.QtWidgets import QApplication
from ui_ventana import VentanaPrincipal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentanaPrincipal()
    window.show()
    sys.exit(app.exec_())
