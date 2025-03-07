import json
import time
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction  # Importar QAction desde QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QListWidget, QHBoxLayout, QMenu, QMessageBox, QListWidgetItem, QSpacerItem, QSizePolicy, QDateEdit, QGraphicsDropShadowEffect
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QDate

class GestorFinanzas:
    hoy = datetime.now().date()
    # Obtener el mes actual en español
    mes_actual = datetime.now().strftime('%B').capitalize()
    mes_actual_num = datetime.now().strftime('%m')
    # Determinar la quincena actual
    dia_actual = hoy.day
    quincena_actual = 1 if dia_actual <= 15 else 2

    
    def __init__(self, archivo="finanzas.json"):
        self.archivo = archivo
        self.datos = self.cargar_datos()

        from views import VentanaPrincipal
        self.widg = VentanaPrincipal()

    def cargar_datos():
        try:
            with open("finanzas.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "saldo": 0,
                "proximos_pagos": [],
                "historial_ingresos": [],
                "historial_gastos": []
            }

    def guardar_datos(self):
        with open("finanzas.json", "w") as f:
            json.dump(self.datos, f, indent=4)


    def agregar_ingreso(self, monto, descripcion):
        self.datos['saldo'] += monto
        self.datos['historial_ingresos'].append({"descripcion": descripcion, 
                                                "monto": monto,
                                                "timestamp": time.time()
                                                })
        self.guardar_datos()


    def agregar_gasto(self, monto, descripcion):
        self.datos['saldo'] -= monto
        self.datos['historial_gastos'].append({"descripcion": descripcion, 
                                               "monto": monto, 
                                               "timestamp": time.time()
                                                })
        self.guardar_datos()


    def agregar_prox_pago(self, monto, descripcion, fecha):
        self.datos['proximos_pagos'].append({"fecha": fecha, 
                                             "descripcion": descripcion, 
                                             "monto": monto, 
                                             "pagado": 0, 
                                             "estatus": 0
                                             })
        self.guardar_datos()


    def confirmar_borrado_historial(self):
          # Crear un cuadro de confirmación
            mensaje = QMessageBox(self)
            mensaje.setIcon(QMessageBox.Icon.Warning)  # Icono de advertencia
            mensaje.setWindowTitle("Confirmar eliminación")
            mensaje.setText("¿Estás seguro de que deseas borrar todo el historial?")
            mensaje.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mensaje.setDefaultButton(QMessageBox.StandardButton.No)  # Establece "No" como botón predeterminado

         # Aplicar estilo al mensaje
            mensaje.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #28a745;  /* Fondo verde */
                    color: white;
                    font-size: 12px;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #218838;  /* Fondo verde oscuro al pasar el mouse */
                }
                QPushButton:pressed {
                    background-color: #1e7e34;  /* Fondo verde aún más oscuro al hacer clic */
                }
            """)
            # Mostrar el mensaje de confirmación
            respuesta = mensaje.exec()


            # Si el usuario confirma con "Yes"
            if respuesta == QMessageBox.StandardButton.Yes:
                # Borrar los datos
                self.datos['historial_ingresos'] = []
                self.datos['historial_gastos'] = []
                self.guardar_datos()
                self.actualizar_historial()


    def actualizar_historial(self):
        self.widg.historial_movimientos.clear()

        # Fusionar ingresos y gastos en una sola lista
        movimientos = self.datos['historial_ingresos'] + self.datos['historial_gastos']

        # Ordenar la lista por la marca de tiempo
        movimientos.sort(key=lambda x: x['timestamp'], reverse=False)

        # Agregar elementos en el orden correcto con fecha y hora formateadas
        for movimiento in movimientos:

            tipo = "💰" if movimiento in self.datos['historial_ingresos'] else "💸"
            tipo_signo = "+" if movimiento in self.datos['historial_ingresos'] else "-"
            fecha_hora = datetime.fromtimestamp(movimiento['timestamp']).strftime('%d/%m - %H:%M:%S')
            fecha_pago = datetime.fromtimestamp(movimiento['timestamp'])

            # Crear el botón para desactivar/activar el pago
            btn_borrar_movimiento = QPushButton("🗑️")
            btn_borrar_movimiento.setStyleSheet("background-color: transparent; font-size: 12px; border: none; min-width: 24px; min-height: 18px;padding: 2px 4px 4px 4px")
            btn_borrar_movimiento.clicked.connect(lambda _, movimiento=movimiento: borrar_movimiento(movimiento))


            # Función para desactivar/activar pago
            def borrar_movimiento(movimiento):
                descripcion = movimiento["descripcion"]
                timestamp = movimiento["timestamp"]
                monto = movimiento["monto"]
                gasto_a_borrar = None
                gasto_lista = None

                # Buscar el gasto en historial_ingresos o historial_gastos
                for key in ["historial_ingresos", "historial_gastos"]:
                    lista = self.datos[key]
                    gasto_a_borrar = next((p for p in lista if p["descripcion"] == descripcion and p["timestamp"] == timestamp), None)
                    
                    if gasto_a_borrar:
                        gasto_lista = lista
                        break  # Salimos del bucle una vez encontrado el gasto

                if gasto_a_borrar:
                    # Crear un cuadro de confirmación SOLO UNA VEZ
                    mensaje = QMessageBox(self)
                    mensaje.setIcon(QMessageBox.Icon.Warning)  # Icono de advertencia
                    mensaje.setWindowTitle("Confirmar eliminación")
                    mensaje.setText("¿Estás seguro de que deseas borrar este movimiento?")
                    mensaje.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    mensaje.setDefaultButton(QMessageBox.StandardButton.No)  # Establece "No" como botón predeterminado

                    # Aplicar estilo al mensaje
                    mensaje.setStyleSheet("""
                        QLabel {
                            color: white;
                            font-size: 14px;
                            font-weight: bold;
                        }
                        QPushButton {
                            background-color: #28a745;  /* Fondo verde */
                            color: white;
                            font-size: 12px;
                            border-radius: 5px;
                            padding: 5px 10px;
                        }
                        QPushButton:hover {
                            background-color: #218838;  /* Fondo verde oscuro al pasar el mouse */
                        }
                        QPushButton:pressed {
                            background-color: #1e7e34;  /* Fondo verde aún más oscuro al hacer clic */
                        }
                    """)

                    # Mostrar el mensaje de confirmación
                    respuesta = mensaje.exec()

                    # Si el usuario confirma con "Yes"
                    if respuesta == QMessageBox.StandardButton.Yes:
                        gasto_lista.remove(gasto_a_borrar)  # Elimina directamente del historial correcto
                        if key == "historial_gastos":
                            self.datos['saldo'] += monto  # Reintegra el monto al saldo
                        elif key == "historial_ingresos":
                            self.datos['saldo'] -= monto  # Descuenta el monto del saldo si es un ingreso
                        self.actualizar_saldo()  # Actualiza la interfaz
                        self.actualizar_historial()
                        self.actualizar_lista_pagos()
                        self.guardar_json()

            # Solo mostrar los pagos del mes actual 
            if fecha_pago.strftime('%m') == mes_actual_num:

                # Crear un widget para la fila
                item_widget = QWidget()
                layout = QHBoxLayout()

                item_text = f"{tipo} {movimiento['descripcion']}"
                item_monto = f"{tipo_signo} ${movimiento['monto']}"
                item_fecha = f"{fecha_hora}"

                # Labels con estilos
                label_fecha = QLabel(item_fecha)
                label_fecha.setStyleSheet("font-size: 12px; font-weight: bold;")
                label_fecha.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Alinear fecha a la izquierda

                label_pago = QLabel(item_text)
                label_pago.setStyleSheet("font-size: 12px; font-weight: light;")
                label_pago.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Alinear el texto dentro de su espacio a la izquierda

                label_monto = QLabel(item_monto)
                if tipo_signo == "+":
                    label_monto.setStyleSheet("color: green; font-size: 12px; font-weight: bold; padding: 2px 4px 4px 4px")
                else:
                    label_monto.setStyleSheet("color: red; font-size: 12px; font-weight: bold; padding: 2px 4px 4px 4px")
                label_monto.setAlignment(Qt.AlignmentFlag.AlignRight)  # Alinear monto a la derecha

                # Espaciadores para organizar los elementos
                spacer_left = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # Entre fecha y descripción
                spacer_right = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)  # Entre descripción y monto

                # Añadir elementos al layout en orden correcto
                layout.addWidget(label_fecha)   # Fecha alineada a la izquierda
                layout.addItem(spacer_left)     # Espaciador entre fecha y descripción
                layout.addWidget(label_pago)    # Descripción alineada a la izquierda dentro de su espacio
                layout.addItem(spacer_right)    # Espaciador entre descripción y monto
                layout.addWidget(btn_borrar_movimiento)  # Botón de borrar gasto
                layout.addWidget(label_monto)   # Monto alineado a la derecha
                layout.setContentsMargins(5, 2, 5, 2)  # Márgenes mínimos

                item_widget.setLayout(layout)

                # Crear un QListWidgetItem y asignarle el widget
                item = QListWidgetItem(self.widg.historial_movimientos)
                item.setSizeHint(item_widget.sizeHint())  # Ajustar tamaño
                self.widg.historial_movimientos.addItem(item)
                self.widg.historial_movimientos.setItemWidget(item, item_widget)


