from PyQt6.QtWidgets import QApplication
from views import VentanaPrincipal

if __name__ == "__main__":
    app = QApplication([])
    ventana = VentanaPrincipal()
    ventana.show()
    app.exec()