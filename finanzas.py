import json
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction  # Importar QAction desde QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QLineEdit, QListWidget, QHBoxLayout, QMenu, QMessageBox, QListWidgetItem, QSpacerItem, QSizePolicy, QDateEdit, QGraphicsDropShadowEffect
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QDate
import time
from datetime import datetime
import locale


# Configurar locale para obtener el mes en español
try:
    locale.setlocale(locale.LC_TIME, "es_ES.utf8")  # Linux/macOS
except:
    locale.setlocale(locale.LC_TIME, "es_ES")  # Windows


hoy = datetime.now().date()
# Obtener el mes actual en español
mes_actual = datetime.now().strftime('%B').capitalize()
mes_actual_num = datetime.now().strftime('%m')

# Determinar la quincena actual
dia_actual = hoy.day
quincena_actual = 1 if dia_actual <= 15 else 2

# Función para cargar datos desde un archivo JSON
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


class FinanzasApp(QWidget):
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
        self.datos = cargar_datos()
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
        self.btn_ingreso.clicked.connect(self.agregar_ingreso)
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
        self.btn_gasto.clicked.connect(self.agregar_gasto)
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
        self.btn_prox_pago.clicked.connect(self.agregar_prox_pago)
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
        self.historial_label = QLabel(f"📌 Movimientos Recientes de {mes_actual}:")
        self.historial_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.historial_label)
        
        # lista de historial
        self.historial_movimientos = QListWidget()
        self.actualizar_historial()
        layout.addWidget(self.historial_movimientos)
        

        # Botón para borrar historial
        self.btn_borrar_historial = QPushButton("🗑️ Borrar Historial")
        self.btn_borrar_historial.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.btn_borrar_historial.clicked.connect(self.confirmar_borrado_historial)
        layout.addWidget(self.btn_borrar_historial)

        self.setLayout(layout)
        

        # Llamada a la función para actualizar la lista de pagos al iniciar
        self.actualizar_lista_pagos()
    
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

    def actualizar_lista_pagos(self):
        self.lista_pagos.clear()  # Limpiar lista de pagos
        saldo_proyectado = self.datos['saldo']
        hoy = datetime.today().date()  # Fecha actual

        for pago in self.datos["proximos_pagos"]:
            # Convertir la fecha del pago a un objeto datetime
            fecha_original = pago['fecha']
            fecha_pago = datetime.strptime(fecha_original, "%Y-%m-%d").date()

            # Solo mostrar los pagos del mes actual 
            if fecha_pago.strftime('%m') == mes_actual_num:

                dias_faltantes = (fecha_pago - hoy).days  # Calcular días faltantes

                # Extraer solo el día
                fecha_formateada = fecha_pago.strftime("%d")

                # Determinar el emoji dependiendo de los días faltantes
                if dias_faltantes <= 2:
                    emoji = "🔴"  # Rojo
                elif 3 <= dias_faltantes <= 5:
                    emoji = "🟡"  # Amarillo
                else:
                    emoji = "🟢"  # Verde

                # Crear el texto del pago
                item_text = f"{emoji} {fecha_formateada} - {pago['descripcion']}"

                # Crear el monto del pago
                item_monto = f"${pago['monto']:.2f}"

                # Crear un widget para la fila
                item_widget = QWidget()
                layout = QHBoxLayout()

                # Crear el QLabel con el texto y monto del pago
                label_pago = QLabel(item_text)
                label_pago.setStyleSheet("font-size: 12px; font-weight: bold;")
                label_monto = QLabel(item_monto)
                label_monto.setStyleSheet("font-size: 12px; font-weight: bold;")

                # Aplicar estilos si el pago está desactivado
                if pago["estatus"] == 1:
                    label_pago.setStyleSheet("font-size: 12px; font-weight: bold; color: gray;")


                # Crear el botón y definir su estado según el JSON
                btn_pagado = QPushButton("Cancelar" if pago["pagado"] == 1 else "Pagado")
                if pago["pagado"] == 1 and pago["estatus"] == 0:
                    btn_pagado.setStyleSheet("background-color: red; color: white; font-size: 12px; padding: 4px 8px;")

                elif pago["pagado"] == 0 and pago["estatus"] == 0:
                    btn_pagado.setStyleSheet("background-color: green; color: white; font-size: 12px; padding: 4px 8px;")

                elif pago["estatus"] == 1:
                    btn_pagado.setDisabled(True)  # Desactiva el botón
                    btn_pagado.setStyleSheet("background-color: gray; color: white; font-size: 12px; padding: 4px 8px;")


                # Crear el botón para desactivar/activar el pago
                btn_desactivar = QPushButton("✅" if pago["estatus"] == 1 else "❌")
                btn_desactivar.setStyleSheet("background-color: transparent; font-size: 12px; border: none; min-width: 24px; min-height: 18px;padding: 2px 4px 4px 4px")

                # Crear boton para borrar pago 
                btn_borrar_prox_pago = QPushButton("🗑️")
                btn_borrar_prox_pago.setStyleSheet("background-color: transparent; font-size: 12px; border: none; min-width: 24px; min-height: 18px;padding: 2px 4px 4px 4px")

                # Aplicar tachado si ya está pagado
                if pago["pagado"] == 1:
                    label_pago.setStyleSheet("font-size: 12px; font-weight: bold; text-decoration: line-through; color: gray;")

                # Función para alternar estado de pago
                def alternar_estado(lbl, btn, pago_obj):
                    if pago_obj["pagado"] == 0:
                        lbl.setStyleSheet("text-decoration: line-through; color: gray; font-size: 12px;")
                        btn.setText("Cancelar")
                        btn.setStyleSheet("background-color: red; color: white; font-size: 12px; padding: 4px 8px;")
                        pago_obj["pagado"] = 1
                        self.datos['saldo'] -= pago_obj['monto']  # Restar monto al saldo disponible
                    else:
                        lbl.setStyleSheet("text-decoration: none; color: white; font-size: 12px;")
                        btn.setText("Pagado")
                        btn.setStyleSheet("background-color: green; color: white; font-size: 12px; padding: 4px 8px;")
                        pago_obj["pagado"] = 0
                        self.datos['saldo'] += pago_obj['monto']  # Sumar monto al saldo disponible
                    
                    self.actualizar_saldo()  # Actualizar la UI con el nuevo saldo
                    self.guardar_json()  # Guardar los cambios en el JSON
                    self.actualizar_lista_pagos()

                # Función para desactivar/activar pago
                def desactivar_pago(lbl, btn, pago_obj):
                    if pago_obj["estatus"] == 0:
                        pago_obj["estatus"] = 1
                        lbl.setStyleSheet("color: gray;")
                        btn.setText("✅")
                    else:
                        pago_obj["estatus"] = 0
                        lbl.setStyleSheet("color: black;")
                        btn.setText("❌")
                    
                    self.guardar_json()
                    self.actualizar_lista_pagos()


                # Funcion para borrar proximo pago 
                def borrar_prox_pago(pago_obj):
                    descripcion = pago_obj["descripcion"]
                    pagos = self.datos["proximos_pagos"]

                    # Buscar el pago con la descripción dada
                    pago_a_borrar = next((p for p in pagos if p["descripcion"] == descripcion), None)

                    if pago_a_borrar:
                        pagos.remove(pago_a_borrar)
                        self.guardar_json()  # Guarda los cambios en el archivo JSON
                        self.actualizar_lista_pagos()  # Refresca la interfaz


                # Conectar los botones con sus respectivas funciones
                btn_pagado.clicked.connect(lambda _, lbl=label_pago, btn=btn_pagado, pago_obj=pago: alternar_estado(lbl, btn, pago_obj))
                btn_desactivar.clicked.connect(lambda _, lbl=label_pago, btn=btn_desactivar, pago_obj=pago: desactivar_pago(lbl, btn, pago_obj))
                btn_borrar_prox_pago.clicked.connect(lambda _, pago_obj=pago: borrar_prox_pago(pago_obj))

                # Agregar un espaciador flexible para empujar el botón a la derecha
                spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

                # Agregar widgets al layout
                layout.addWidget(label_pago)  # Texto del pago
                layout.addItem(spacer)        # Espaciador
                layout.addWidget(label_monto)
                if pago["pagado"] == 0 and  ((quincena_actual == 1 and fecha_pago.day <= 15) or (quincena_actual == 2 and fecha_pago.day > 15)):
                    layout.addWidget(btn_desactivar)  # Botón de desactivar/activar
                layout.addWidget(btn_borrar_prox_pago) # Boton de borrar proximo pago
                layout.addWidget(btn_pagado)  # Botón de pagado/cancelar
                layout.setContentsMargins(5, 2, 5, 2)  # Márgenes mínimos
                item_widget.setLayout(layout)

                # Crear un QListWidgetItem y asignarle el widget
                item = QListWidgetItem(self.lista_pagos)
                item.setSizeHint(item_widget.sizeHint())  # Ajustar tamaño
                self.lista_pagos.addItem(item)
                self.lista_pagos.setItemWidget(item, item_widget)

                # Actualizar saldo proyectado
                if pago["pagado"] == 0 and pago["estatus"] == 0:
                    fecha_pago = datetime.strptime(pago["fecha"], "%Y-%m-%d").date()
                    
                    # Verificar si el pago cae en la quincena actual
                    if (quincena_actual == 1 and fecha_pago.day <= 15) or (quincena_actual == 2 and fecha_pago.day > 15):
                        saldo_proyectado -= float(pago['monto'])  # Solo restar si no está pagado y está activado
        
        # Determinar el color del saldo proyectado
        color = "red" if saldo_proyectado <= 0 else "green"

        # Aplicar color solo al número
        self.saldo_proyectado_label.setText(f"💰 Saldo proyectado después de estos pagos: <span style='color:{color}; font-weight:bold;'>${saldo_proyectado:.2f}</span>")



    
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
    


    def agregar_ingreso(self):
        try:
            monto = float(self.ingreso_input.text())
            descripcion = self.ingreso_desc.text().strip()
            if monto > 0 and descripcion:
                self.datos['saldo'] += monto
                self.datos['historial_ingresos'].append({"descripcion": descripcion, 
                                                        "monto": monto,
                                                        "timestamp": time.time() # Agrega la marca de tiempo
                                                        })
                self.ingreso_input.clear()
                self.ingreso_desc.clear()
                self.actualizar_saldo()  # Actualiza el saldo en la interfaz
                self.actualizar_lista_pagos()
                self.actualizar_historial()
                self.guardar_datos()
    
        except ValueError:
                QMessageBox.warning(self, "Error", "Ingresa un monto valido.")
            
    
    def agregar_gasto(self):
        try:
            monto = float(self.gasto_input.text())
            descripcion = self.gasto_desc.text().strip()
            if monto > 0 and descripcion:
                self.datos['saldo'] -= monto
                self.datos['historial_gastos'].append({"descripcion": descripcion, 
                                                    "monto": monto,
                                                    "timestamp": time.time() # Agrega la marca de tiempo
                                                    })
                self.gasto_input.clear()
                self.gasto_desc.clear()
                self.actualizar_saldo()  # Actualiza el saldo en la interfaz
                self.actualizar_lista_pagos()
                self.actualizar_historial()
                self.guardar_datos()

        except ValueError:
                QMessageBox.warning(self, "Error", "Ingresa un monto valido.")


    def agregar_prox_pago(self):
        try:
            monto = float(self.prox_pago_input.text())
            descripcion = self.prox_pago_desc.text().strip()
            fecha = self.prox_pago_fecha.date().toString("yyyy-MM-dd") #fecha convertida a string
            if monto > 0 and descripcion:
                self.datos['proximos_pagos'].append({
                                                    "fecha": fecha,
                                                    "descripcion": descripcion, 
                                                    "monto": monto,
                                                    "pagado": 0,
                                                    "estatus": 0
                                                    })
                self.prox_pago_input.clear()
                self.prox_pago_desc.clear()
                self.actualizar_lista_pagos()
                self.actualizar_historial()
                self.guardar_datos()

        except ValueError:
                QMessageBox.warning(self, "Error", "Ingresa un monto valido.")
            

    def actualizar_historial(self):
        self.historial_movimientos.clear()

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
                item = QListWidgetItem(self.historial_movimientos)
                item.setSizeHint(item_widget.sizeHint())  # Ajustar tamaño
                self.historial_movimientos.addItem(item)
                self.historial_movimientos.setItemWidget(item, item_widget)

        


    def guardar_datos(self):
        with open("finanzas.json", "w") as f:
            json.dump(self.datos, f, indent=4)
    


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


    def guardar_json(self):
        """ Guarda el estado actualizado de los pagos en el archivo JSON """
        try:
            with open("finanzas.json", "w", encoding="utf-8") as archivo:
                json.dump(self.datos, archivo, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")


    def actualizar_saldo(self):
        color = "red" if self.datos['saldo'] <= 0 else "white"

        self.saldo_label.setText(f"\U0001F4B8 Saldo disponible: <span style='color:{color};'>${self.datos['saldo']:.2f}</span>")



if __name__ == "__main__":
    app = QApplication([])
    ventana = FinanzasApp()
    ventana.show()
    app.exec()
