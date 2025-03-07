import json
import locale
import time
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction  # Importar QAction desde QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QListWidget, QHBoxLayout, QMenu, QMessageBox, QListWidgetItem, QSpacerItem, QSizePolicy, QDateEdit, QGraphicsDropShadowEffect
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QDate
from datetime import datetime
from logic import GestorFinanzas

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión Financiera")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
                        (screen.width() - 450) // 2,  # Centra en X
                        (screen.height() - 550) // 2,  # Centra en Y
                        550, 750  # Tamaño de la ventana
                        )
        self.setStyleSheet(open("styles.qss", "r").read())
        self.setWindowIcon(QIcon("icon.png"))
        self.gestor = GestorFinanzas
        self.datos = self.gestor.cargar_datos()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Saldo disponible
        self.saldo_label = QLabel(f"\U0001F4B8 Saldo disponible: ${self.datos['saldo']:.2f}")
        self.saldo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.saldo_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.saldo_label)
        
        # Botón de menú con engranaje
        self.menu_button = QPushButton("⚙️ Opciones")
        self.menu_button.setMenu(self.crear_menu())
        layout.addWidget(self.menu_button)

        # Stacked widget para mostrar formularios de ingresos y gastos
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setVisible(False)
        layout.addWidget(self.stacked_widget)
        
         # Widget para ingresar ingresos
        self.ingreso_widget = QWidget()
        ingreso_layout = QVBoxLayout()
        self.ingreso_input = QLineEdit()
        self.ingreso_input.setPlaceholderText("Monto del ingreso")
        self.ingreso_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        ingreso_layout.addWidget(self.ingreso_input)
        self.ingreso_desc = QLineEdit()
        self.ingreso_desc.setPlaceholderText("Descripción del ingreso")
        ingreso_layout.addWidget(self.ingreso_desc)
        self.btn_ingreso = QPushButton("💵 Agregar Ingreso")
        self.btn_ingreso.clicked.connect(self.gestor.agregar_ingreso)
        ingreso_layout.addWidget(self.btn_ingreso)
        self.ingreso_widget.setLayout(ingreso_layout)

        # Widget para ingresar gastos
        self.gasto_widget = QWidget()
        gasto_layout = QVBoxLayout()
        self.gasto_input = QLineEdit()
        self.gasto_input.setPlaceholderText("Monto del gasto")
        self.gasto_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        gasto_layout.addWidget(self.gasto_input)
        self.gasto_desc = QLineEdit()
        self.gasto_desc.setPlaceholderText("Descripción del gasto")
        gasto_layout.addWidget(self.gasto_desc)
        self.btn_gasto = QPushButton("💸 Agregar Gasto")
        self.btn_gasto.clicked.connect(self.gestor.agregar_gasto)
        gasto_layout.addWidget(self.btn_gasto)
        self.gasto_widget.setLayout(gasto_layout)
        

        # Widget para ingresar proximo pago importante
        self.prox_pago_widget = QWidget()
        prox_pago_layout = QVBoxLayout()
        self.prox_pago_input = QLineEdit()
        self.prox_pago_input.setPlaceholderText("Monto del pago")
        self.prox_pago_input.setValidator(QDoubleValidator(0.01, 1000000.00, 2))
        prox_pago_layout.addWidget(self.prox_pago_input)
        self.prox_pago_desc = QLineEdit()
        self.prox_pago_desc.setPlaceholderText("Descripción del pago")
        prox_pago_layout.addWidget(self.prox_pago_desc)
        self.prox_pago_fecha = QDateEdit()
        self.prox_pago_fecha.setCalendarPopup(True)  # Activa el calendario emergente
        self.prox_pago_fecha.setDate(QDate.currentDate())  # Establece la fecha actual
        self.prox_pago_fecha.setDisplayFormat("yyyy-MM-dd")  # Configura el formato de visualización
        # Aplicar estilos al QDateEdit
        
        prox_pago_layout.addWidget(self.prox_pago_fecha)
        self.btn_prox_pago = QPushButton("📅 Agregar Proximo Pago")
        self.btn_prox_pago.clicked.connect(self.gestor.agregar_prox_pago)
        prox_pago_layout.addWidget(self.btn_prox_pago)
        self.prox_pago_widget.setLayout(prox_pago_layout)
        

        #widgets agregados
        self.stacked_widget.addWidget(self.ingreso_widget)
        self.stacked_widget.addWidget(self.gasto_widget)
        self.stacked_widget.addWidget(self.prox_pago_widget)


        # Título de "Próximos Pagos Importantes"
        self.lista_pagos_label = QLabel("📌 Próximos Pagos Importantes:")
        self.lista_pagos_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lista_pagos_label)

        # Lista de pagos
        self.lista_pagos = QListWidget()
        layout.addWidget(self.lista_pagos)
        

        # Crear y agregar la etiqueta de saldo proyectado
        self.saldo_proyectado_label = QLabel("💰 Saldo proyectado después de estos pagos: $0.00")
        self.saldo_proyectado_label.setStyleSheet("font-size: 14px; color: white; font-weight: bold;")
        layout.addWidget(self.saldo_proyectado_label)
        
        # titulo de Movimientos Recientes
        self.historial_label = QLabel(f"📌 Movimientos Recientes de {self.gestor.mes_actual}:")
        self.historial_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.historial_label)
        
        # lista de historial
        self.historial_movimientos = QListWidget()
        self.gestor.actualizar_historial(self)
        layout.addWidget(self.historial_movimientos)
        

        # Botón para borrar historial
        self.btn_borrar_historial = QPushButton("🗑️ Borrar Historial")
        self.btn_borrar_historial.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.btn_borrar_historial.clicked.connect(self.gestor.confirmar_borrado_historial)
        layout.addWidget(self.btn_borrar_historial)

        self.setLayout(layout)
        

        # Llamada a la función para actualizar la lista de pagos al iniciar
        self.actualizar_lista_pagos()

    def actualizar_saldo(self):
        self.saldo_label.setText(f"Saldo disponible: ${self.datos['saldo']:.2f}")

    def crear_menu(self):
        menu = QMenu(self)

        # Aplicar sombra al menú
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(Qt.GlobalColor.black)  # Color de la sombra
        menu.setGraphicsEffect(shadow)  # Aplica el efecto al menú
        
        # Acción para "Ingresos"
        ingresos_action = QAction("💰 Ingresos", self)
        ingresos_action.triggered.connect(self.mostrar_ingresos)
        menu.addAction(ingresos_action)

        # Acción para "Gastos"
        gastos_action = QAction("💸 Gastos", self)
        gastos_action.triggered.connect(self.mostrar_gastos)
        menu.addAction(gastos_action)

        prox_pago_action = QAction("📅 Prox Pago", self)
        prox_pago_action.triggered.connect(self.mostrar_prox_pago)
        menu.addAction(prox_pago_action)

        return menu


    def mostrar_ingresos(self):
        if self.stacked_widget.isVisible() and self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setVisible(False)  # Oculta el widget si ya está en ingresos
        else:
            self.stacked_widget.setVisible(True)
            self.stacked_widget.setCurrentIndex(0)



    def mostrar_gastos(self):
        if self.stacked_widget.isVisible() and self.stacked_widget.currentIndex() == 1:
            self.stacked_widget.setVisible(False)  # Oculta el widget si ya está en gastos
        else:
            self.stacked_widget.setVisible(True)
            self.stacked_widget.setCurrentIndex(1)


    def mostrar_prox_pago(self):
        if self.stacked_widget.isVisible() and self.stacked_widget.currentIndex() == 2:
            self.stacked_widget.setVisible(False)  # Oculta el widget si ya está en gastos
        else:
            self.stacked_widget.setVisible(True)
            self.stacked_widget.setCurrentIndex(2)