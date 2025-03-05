import tkinter as tk
from tkinter import ttk, messagebox
from inventario import escanear_alumno, agregar_alumno, cargar_alumnos, modificar_alumno, eliminar, guardar_alumno
from ventadiaria import guardar_venta_diaria
from datetime import datetime
#import serial
import os
import sys
import json
from tkcalendar import Calendar
from tkinter import BooleanVar

class InventarioApp:
    def __init__(self, master):
        self.master = master
        master.title("QUE VIVA EL FUTBOL")
        self.ventanaagregar = False
        self.ventanaAlumnos = False
        self.editando_alumno = False
        self.lista_alumnos = []
        self.venta_finalizada = False
        self.ventanacobrar = False
        self.ventanacaja = False
        self.total_con_descuento = 0 
        self.total_con_descuento = 0
        self.restrict_mode = BooleanVar()
        self.restrict_mode.set(self.cargar_estado_restriccion())
        self.alumno_encontrado = None

        nombre_label = tk.Label(self.master, text="Desarrollado por Agustin Goyechea V1.1", font=("Arial", 6))
        nombre_label.pack(side=tk.BOTTOM, pady=10)

        # Cargar imágenes usando rutas relativas
        self.add_icon = tk.PhotoImage(file=self.resource_path("images/agregar_jugador.png"))
        self.sell_icon = tk.PhotoImage(file=self.resource_path("images/cobro.png"))
        self.view_icon = tk.PhotoImage(file=self.resource_path("images/lista.png"))
        self.caja_icon = tk.PhotoImage(file=self.resource_path("images/balance.png"))  # Asegúrate de tener esta imagen
       

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(pady=20)
        

        self.add_button = tk.Button(self.buttons_frame, text="Agregar Alumno", image=self.add_icon, compound=tk.LEFT, command=self.mostrar_ventana_agregar,  state=tk.DISABLED if self.restrict_mode.get() else tk.NORMAL)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.sell_button = tk.Button(self.buttons_frame, text="Cobrar", image=self.sell_icon, compound=tk.LEFT, command=self.mostrar_ventana_cuota)
        self.sell_button.pack(side=tk.LEFT, padx=10)

        self.view_button = tk.Button(self.buttons_frame, text="Lista Alumnos", image=self.view_icon, compound=tk.LEFT, command=self.mostrar_ventana_alumnos)
        self.view_button.pack(side=tk.LEFT, padx=10)

        self.caja_button = tk.Button(self.buttons_frame, text="Balance", image=self.caja_icon, compound=tk.LEFT, command=self.mostrar_ventana_caja)
        self.caja_button.pack(side=tk.LEFT, padx=10)
        # Añadir el switch de restricción
        self.restrict_switch = tk.Checkbutton(self.master, text="Modo Restricción", variable=self.restrict_mode, command=self.toggle_restriccion)
        self.restrict_switch.pack(pady=10)

        # Obtener el tamaño de la pantalla
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 600 # Ajusta según sea necesario
        window_height = 175  # Ajusta según sea necesario

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        master.geometry(f"{window_width}x{window_height}+{x}+{y-280}")
        # Aplicar estado inicial del modo restricción
        #self.toggle_restriccion()
        self.cargar_estado_restriccion()  # Asegurarse de cargar el estado al inicio
        self.actualizar_estado_cuota()

    def guardar_estado_restriccion(self):
        with open("estado_restriccion.json", "w") as file:
            json.dump({"restrict_mode": self.restrict_mode.get()}, file)

    def cargar_estado_restriccion(self):
        if os.path.exists("estado_restriccion.json"):
            with open("estado_restriccion.json", "r") as file:
                data = json.load(file)
                return data.get("restrict_mode", False)
        return False
    
    def toggle_restriccion(self):
        if self.restrict_mode.get():
            self.restrict_mode.set(True)
            self.add_button.config(state=tk.DISABLED)
            self.guardar_estado_restriccion()
        else:
            self.solicitar_contraseña()

    def solicitar_contraseña(self):
        # Crear una ventana emergente para la contraseña
        self.ventana_contraseña = tk.Toplevel(self.master)
        self.ventana_contraseña.title("Ingresar Contraseña")

        label = tk.Label(self.ventana_contraseña, text="Contraseña:", font=("Arial", 14))
        label.pack(pady=10)

        def cerrar_ventana():
            self.restrict_mode.set(True)
            self.restrict_switch.config(state=tk.NORMAL)  # Asegurar que el switch esté en el estado correcto
            self.add_button.config(state=tk.DISABLED)
            self.guardar_estado_restriccion()
            self.ventana_contraseña.destroy()

        self.ventana_contraseña.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        self.entry_contraseña = tk.Entry(self.ventana_contraseña, show="*", font=("Arial", 14))
        self.entry_contraseña.pack(pady=10)

        boton_aceptar = tk.Button(self.ventana_contraseña, text="Aceptar", font=("Arial", 14), command=self.verificar_contraseña)
        boton_aceptar.pack(pady=10)

        # Obtener el tamaño de la pantalla
        screen_width = self.ventana_contraseña.winfo_screenwidth()
        screen_height = self.ventana_contraseña.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 300  # Ajusta el ancho de la ventana
        window_height = 150  # Ajusta la altura de la ventana

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        self.ventana_contraseña.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def verificar_contraseña(self):
        contraseña_correcta = "beto1986"  # Reemplaza esto con la contraseña correcta
        if self.entry_contraseña.get() == contraseña_correcta:
            self.restrict_mode.set(False)
            self.add_button.config(state=tk.NORMAL)
            self.guardar_estado_restriccion()
            messagebox.showinfo("Modo Restricción", "Modo restricción desactivado.")
            self.ventana_contraseña.destroy()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
            self.entry_contraseña.delete(0, tk.END)


    def mostrar_ventana_caja(self):
        if self.ventanacaja is not False:
            return
        self.ventanacaja = True
        def actualizar_ventas():
            # Limpiar el Treeview
            for item in tree.get_children():
                tree.delete(item)
            
            # Obtener la fecha seleccionada y formatearla a dd/mm/aaaa
            fecha_seleccionada = date_entry.get()

            # Filtrar las ventas del día seleccionado
            if fecha_seleccionada in ventas_del_dia:
                ventas_del_dia_seleccionada = ventas_del_dia[fecha_seleccionada]
                mostrar_mensaje("")
            else:
                ventas_del_dia_seleccionada = []
                mostrar_mensaje("No hay ventas para el día seleccionado")

            # Inicializar total de ventas en el día
            total_ventas_dia = 0

            # Iterar sobre las ventas del día seleccionado y agregar los productos al Treeview
            for venta in ventas_del_dia_seleccionada:
                for producto, detalles in venta.items():
                    cantidad_producto = detalles["cantidad"]
                    precio_producto = detalles["precio"]
                    total_producto = cantidad_producto * precio_producto
                    tree.insert("", tk.END, text=producto, values=(cantidad_producto, f"${precio_producto:.2f}", f"${total_producto:.2f}"))
                    total_ventas_dia += total_producto

            # Actualizar el total vendido en el día
            total_label.config(text=f"Total vendido en el día: ${total_ventas_dia:.2f}")

        def mostrar_mensaje(mensaje):
            mensaje_label.config(text=mensaje)

        def imprimir_ventas():
            # Obtener la fecha seleccionada y formatearla a dd/mm/aaaa
            fecha_seleccionada = date_entry.get()
            totalfinal = 0
            # Obtener las ventas del día seleccionado
            if fecha_seleccionada in ventas_del_dia:
                ventas_del_dia_seleccionada = ventas_del_dia[fecha_seleccionada]
            else:
                ventas_del_dia_seleccionada = []

            now = datetime.datetime.now()
            fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
            total_line_length = 40
            
            ticket_text = ""
            ticket_text += "=" * total_line_length + "\n"
            ticket_text += " " * (int((total_line_length-21)/2)) + "S&S Tienda Multirubro" + " " * int(((total_line_length-21)/2)) + "\n"
            ticket_text += " " * (int((total_line_length-28)/2)) + "Chaco 233 - Obera - Misiones" + " " * int(((total_line_length-28)/2)) + "\n"
            ticket_text += "=" * total_line_length + "\n"
            ticket_text += f"Fecha y Hora: {fecha_hora}\n"
            ticket_text += "-" * total_line_length + "\n"        
            
            # Generar el texto del ticket
            max_product_name_length = 20  # Ajusta este valor según tus necesidades

            ticket_text += f"Ventas del dia {fecha_seleccionada}:\n\n"
            ticket_text += f"{'Producto':<20}{'Cantidad':>10}{'Precio':>10}\n"
            ticket_text += "-" * total_line_length + "\n"

            for venta in ventas_del_dia_seleccionada:
                for producto, detalles in venta.items():
                    cantidad_producto = detalles["cantidad"]
                    precio_producto = detalles["precio"]
                    total_producto = cantidad_producto * precio_producto
                    
                    # Truncate product name if it exceeds max length
                    if len(producto) > max_product_name_length:
                        producto = producto[:max_product_name_length - 3] + "..."

                    ticket_text += f"{producto:<20}{cantidad_producto:>7}{'$' + format(precio_producto, '.2f'):>13}\n"
                    totalfinal += total_producto
            
            if totalfinal == 0:
                ticket_text += "No se vendio ningun producto ese dia :(\n"   
                ticket_text += "=" * total_line_length + "\n" + "\n" * 8  
            else:
                ticket_text += "-" * total_line_length + "\n"
                ticket_text += f"MONTO TOTAL VENDIDO: ${totalfinal:.2f}\n"
                ticket_text += "=" * total_line_length + "\n" + "\n" * 8

            # Imprimir el ticket
            print(ticket_text)
            self.impresora(ticket_text)

        # Crear la ventana de caja
        caja_window = tk.Toplevel(self.master)
        caja_window.title("Caja")



        # Obtener el tamaño de la pantalla
        screen_width = caja_window.winfo_screenwidth()
        screen_height = caja_window.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 900  # Ajusta el ancho de la ventana
        window_height = 550 # Ajusta la altura de la ventana

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        caja_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        def cerrar_ventana():
            self.ventanacaja = False
            caja_window.destroy()
        
        caja_window.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Cargar el archivo JSON que contiene las ventas
        try:
            # Intentar cargar el archivo JSON que contiene las ventas
            with open("ventas_diarias.json", "r") as file:
                ventas_del_dia = json.load(file)
        except FileNotFoundError:
            # Si el archivo no se encuentra, crear un diccionario vacío
            ventas_del_dia = {}

        fecha = datetime.datetime.now().strftime("%d/%m/%Y")
        # Mostrar el selector de fecha
        date_entry_label = tk.Label(caja_window, text="Ingrese la fecha (dd/mm/aaaa):", font=("Arial", 12, "bold"))
        date_entry_label.pack(pady=10)

        date_entry = tk.Entry(caja_window, font=("Arial", 14))
        date_entry.insert(0, fecha)  # Insertar la fecha actual en el widget
        date_entry.pack(pady=10)
        

        def validar_fecha():
            fecha = date_entry.get()
            try:
                datetime.datetime.strptime(fecha, "%d/%m/%Y")
                # Si la fecha es válida, llamar a la función para actualizar las ventas
                actualizar_ventas()
            except ValueError:
                # Si hay un error, mostrar un mensaje de error al usuario
                mostrar_mensaje("Por favor, ingrese una fecha válida en formato dd/mm/aaaa")

        # Botón para actualizar las ventas según la fecha ingresada
        actualizar_button = tk.Button(caja_window, text="Mostrar Ventas", command=validar_fecha)
        actualizar_button.pack(pady=10)

        # Botón para imprimir las ventas del día en formato de ticket
        imprimir_button = tk.Button(caja_window, text="Imprimir Ticket", command=imprimir_ventas)
        imprimir_button.pack(pady=10)

        # Crear el Treeview para mostrar los productos vendidos en columnas
        tree = ttk.Treeview(caja_window)
        tree["columns"] = ("Cantidad", "Precio", "Total")
        tree.heading("#0", text="Producto", anchor=tk.W)
        tree.heading("Cantidad", text="Cantidad", anchor=tk.W)
        tree.heading("Precio", text="Precio", anchor=tk.W)
        tree.heading("Total", text="Total", anchor=tk.W)
        tree.pack(padx=20, pady=10)

        # Mostrar el total vendido en el día en negrita
        total_label = tk.Label(caja_window, text="Total vendido en el día: $0.00", font=("Arial", 12, "bold"))
        total_label.pack(pady=10)

        # Etiqueta para mostrar mensajes
        mensaje_label = tk.Label(caja_window, text="", font=("Arial", 12))
        mensaje_label.pack(pady=10)

        caja_window.update_idletasks()
        

    def mostrar_ventana_agregar(self, editar=False, nombre="", apellido="", dni="", categoria="", cuota_estado=""):
        if self.ventanaagregar is not False:
            return

        self.previous_window = self.master.focus_get()
        self.ventanaagregar = True
        self.ventana_agregar = tk.Toplevel(self.master)
        self.ventana_agregar.title("Agregar Nuevo Alumno" if not editar else "Editar Alumno")

        def cerrar_ventana():
            self.toggleAgregar()  # Llama al método toggleAgregar cuando se cierra la ventana
            self.ventana_agregar.destroy()
            self.editando_alumno=False

        self.ventana_agregar.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Crear el frame principal para centrar todos los widgets
        main_frame = tk.Frame(self.ventana_agregar, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Campo Nombre
        tk.Label(main_frame, text="Nombre:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.nombre_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.nombre_entry.focus_set()
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=5)
        self.nombre_entry.insert(tk.END, nombre)

        # Campo Apellido
        tk.Label(main_frame, text="Apellido:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.apellido_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.apellido_entry.grid(row=1, column=1, padx=10, pady=5)
        self.apellido_entry.insert(tk.END, apellido)

        # Campo DNI
        tk.Label(main_frame, text="DNI:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.dni_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.dni_entry.grid(row=2, column=1, padx=10, pady=5)
        self.dni_entry.insert(tk.END, dni)

        # Campo Categoría
        tk.Label(main_frame, text="Categoría:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.categoria_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.categoria_entry.grid(row=3, column=1, padx=10, pady=5)
        self.categoria_entry.insert(tk.END, categoria)

        # Campo Cuota con Combobox
        tk.Label(main_frame, text="Cuota:", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)

        # Variable para almacenar la selección
        self.cuota_estado = tk.StringVar(value="AL DÍA")  # Valor por defecto

        # Combobox en lugar de OptionMenu
        self.cuota_menu = ttk.Combobox(main_frame, textvariable=self.cuota_estado, values=["AL DÍA", "MOROSO"], state="readonly", font=("Arial", 14))
        self.cuota_menu.grid(row=4, column=1, padx=10, pady=5)

        botones_frame = tk.Frame(main_frame)
        botones_frame.grid(row=5, column=0, columnspan=2, pady=10)

        if editar:
            guardar_button = tk.Button(botones_frame, text="Guardar", font=("Arial", 14), command=lambda: self.guardar_alumno_editado(dni))
            guardar_button.pack(side=tk.LEFT, padx=5)
            eliminar_button = tk.Button(botones_frame, text="Eliminar", font=("Arial", 14), command=lambda: self.eliminar_alumno(dni))
            eliminar_button.pack(side=tk.LEFT, padx=5)

        else:
            agregar_button = tk.Button(botones_frame, text="Agregar", font=("Arial", 14), command=self.agregar_alumno)
            agregar_button.pack(side=tk.LEFT, padx=5)

        # Centrar la ventana en la pantalla
        self.ventana_agregar.update_idletasks()
        width = self.ventana_agregar.winfo_width()
        height = self.ventana_agregar.winfo_height()

        x = (self.ventana_agregar.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana_agregar.winfo_screenheight() // 2) - (height // 2)
        self.ventana_agregar.geometry(f"{width}x{height}+{x}+{y-100}")

        return self.ventana_agregar


    def mostrar_ventana_cuota(self):
        if self.ventanacobrar is not False:
            return
        self.venta_finalizada = False
        self.carrito = {}
        self.lista_alumnos = []
        self.total = 0
        self.ventanacobrar = True
        ventana_cobrar = tk.Toplevel(self.master)
        ventana_cobrar.title("Cobrar Cuota")
        
        def cerrar_ventana():
            self.venta_finalizada = False
            self.ventanacobrar = False
            ventana_cobrar.destroy()

        ventana_cobrar.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Frame para la entrada y el botón de búsqueda
        input_frame = tk.Frame(ventana_cobrar)
        input_frame.pack(pady=5)

        # Etiqueta y entrada para el DNI
        label_dni = tk.Label(input_frame, text="Ingrese el DNI del alumno:", font=("Arial", 14))
        label_dni.pack(side=tk.LEFT, padx=5)
        self.entry_dni = tk.Entry(input_frame, font=("Arial", 14), width=20)
        self.entry_dni.pack(side=tk.LEFT, padx=5)

        # Botón para buscar el alumno
        buscar_button = tk.Button(input_frame, text="Buscar Alumno", font=("Arial", 14), command=self.buscar_alumno_cuota)
        buscar_button.pack(side=tk.LEFT, padx=5)

        # Etiqueta para mostrar nombre y apellido
        self.label_nombre_apellido = tk.Label(ventana_cobrar, text="", font=("Arial", 14))
        self.label_nombre_apellido.pack(pady=10, anchor="center")

        # Frame para mostrar historial de pagos
        self.historial_frame = tk.Frame(ventana_cobrar)
        self.historial_frame.pack(pady=10)

        # Etiqueta de historial de pagos
        self.label_historial = tk.Label(self.historial_frame, text="Historial de Pagos:", font=("Arial", 14))
        self.label_historial.pack()

        # Crear Treeview para mostrar historial de pagos
        self.tree = ttk.Treeview(self.historial_frame, columns=('DNI', 'Nombre', 'Categoría', 'Fecha', 'Monto', 'Método de Pago'), show='headings')

        # Configurar columnas
        self.tree.column('DNI', anchor=tk.CENTER, width=100)
        self.tree.column('Nombre', anchor=tk.W, width=150)
        self.tree.column('Categoría', anchor=tk.CENTER, width=100)
        self.tree.column('Fecha', anchor=tk.CENTER, width=100)
        self.tree.column('Monto', anchor=tk.CENTER, width=100)
        self.tree.column('Método de Pago', anchor=tk.W, width=120)

        # Configurar encabezados
        self.tree.heading('DNI', text='DNI', anchor=tk.CENTER)
        self.tree.heading('Nombre', text='Nombre', anchor=tk.W)
        self.tree.heading('Categoría', text='Categoría', anchor=tk.CENTER)
        self.tree.heading('Fecha', text='Fecha', anchor=tk.CENTER)
        self.tree.heading('Monto', text='Monto', anchor=tk.CENTER)
        self.tree.heading('Método de Pago', text='Método de Pago', anchor=tk.W)

        # Empacar el Treeview
        self.tree.pack(pady=10, fill='both', expand=True)


        # Insertar ejemplo de datos, reemplázalo con datos reales


        self.tree.pack(pady=5)

        # Mostrar métodos de pago, monto, recargo y total a pagar
        pago_frame = tk.Frame(ventana_cobrar)
        pago_frame.pack(pady=10)

        # Métodos de pago
        metodo_pago_label = tk.Label(pago_frame, text="Método de pago:", font=("Arial", 14))
        metodo_pago_label.grid(row=0, column=0, padx=10)
        self.var_pago = tk.StringVar()
        self.var_pago.set("Efectivo")  # Valor por defecto
        efectivo_radio = tk.Radiobutton(pago_frame, text="Efectivo", variable=self.var_pago, value="Efectivo", font=("Arial", 14))
        transferencia_radio = tk.Radiobutton(pago_frame, text="Transferencia", variable=self.var_pago, value="Transferencia", font=("Arial", 14))
        efectivo_radio.grid(row=0, column=1, padx=5)
        transferencia_radio.grid(row=0, column=2, padx=5)

        # Fecha de pago
        fecha_pago_label = tk.Label(pago_frame, text="Fecha de pago (dd/mm):", font=("Arial", 14))
        fecha_pago_label.grid(row=1, column=0, padx=10)
        fecha_actual = tk.StringVar()
        fecha_actual.set(self.obtener_fecha_actual())  # Fecha actual
        self.entry_fecha_pago = tk.Entry(pago_frame, textvariable=fecha_actual, font=("Arial", 14), width=10)
        self.entry_fecha_pago.grid(row=1, column=1, padx=5)

        self.entry_fecha_pago.bind("<FocusOut>", self.calcular_monto_pago)

        # Botón para seleccionar la fecha
        calendario_button = tk.Button(pago_frame, text="Seleccionar Fecha", font=("Arial", 14), command=self.mostrar_calendario)
        calendario_button.grid(row=1, column=2, padx=5)

        # Monto y recargo
        # Cuadro de pago
        monto_label = tk.Label(pago_frame, text="Monto de Cuota: $", font=("Arial", 14))
        monto_label.grid(row=2, column=0, padx=10)

        # Mostrar la cuota fija (ejemplo: $20000)
        self.cuota_base = 20000
        self.label_monto = tk.Label(pago_frame, text=f"{self.cuota_base:.2f}", font=("Arial", 14))
        self.label_monto.grid(row=2, column=1, padx=5)

        # Etiqueta de recargo
        recargo_label = tk.Label(pago_frame, text="Recargo: $", font=("Arial", 14))
        recargo_label.grid(row=3, column=0, padx=10)
        self.label_recargo = tk.Label(pago_frame, text="0.0", font=("Arial", 14))
        self.label_recargo.grid(row=3, column=1, padx=5)

        # Total a pagar
        total_label = tk.Label(pago_frame, text="Total a Pagar: $", font=("Arial", 14))
        total_label.grid(row=4, column=0, padx=10)
        self.label_total = tk.Label(pago_frame, text=f"{self.cuota_base:.2f}", font=("Arial", 14))
        self.label_total.grid(row=4, column=1, padx=5)

        # Vincular la fecha para que actualice el total automáticamente
        self.entry_fecha_pago.bind("<KeyRelease>", self.calcular_monto_pago)

        # Botón para registrar pago
        registrar_button = tk.Button(pago_frame, text="Registrar Pago", font=("Arial", 14), command=self.registrar_pago)
        registrar_button.grid(row=5, column=0, columnspan=3, pady=10)


    def mostrar_calendario(self):
        calendario_popup = tk.Toplevel(self.master)
        calendario_popup.title("Seleccionar Fecha")

        # Calendario (puedes usar un widget de calendario aquí)
        calendario = Calendar(calendario_popup, selectmode='day', date_pattern='dd/mm/yyyy')
        calendario.pack(padx=10, pady=10)

        # Función para actualizar la fecha en el entry
        def seleccionar_fecha():
            fecha_seleccionada = calendario.get_date()
            self.entry_fecha_pago.delete(0, tk.END)
            self.entry_fecha_pago.insert(0, fecha_seleccionada)  # Actualizar la entrada con la fecha seleccionada
            self.calcular_monto_pago()
            calendario_popup.destroy()

        # Botón para seleccionar la fecha
        seleccionar_button = tk.Button(calendario_popup, text="Seleccionar Fecha", command=seleccionar_fecha)
        seleccionar_button.pack(pady=10)
        

    def buscar_alumno_cuota(self):
        dni = self.entry_dni.get()
        alumnos = cargar_alumnos()  # Cargar la lista de alumnos
        print("entrada")
        # Buscar el alumno por DNI
        
        for alumno in alumnos:
            if alumno['dni'] == dni:
                self.alumno_encontrado = alumno
               
                break
            else: self.alumno_encontrado=None
            self.mostrar_historial_pagos(dni)  # Mostrar historial de pagos

        if self.alumno_encontrado:
            self.label_nombre_apellido.config(text=f"{self.alumno_encontrado['nombre']} {self.alumno_encontrado['apellido']}")
            self.mostrar_historial_pagos(dni)  # Mostrar historial de pagos
            self.calcular_monto_pago()
        else:
            self.label_nombre_apellido.config(text="Alumno no encontrado")

    def mostrar_historial_pagos(self, dni):
        archivo_historial = "historial_pagos.json"

        # Si el archivo no existe, salir de la función
        if not os.path.exists(archivo_historial):
            return

        # Leer el historial general
        with open(archivo_historial, "r") as file:
            try:
                historial_general = json.load(file)
            except json.JSONDecodeError:
                historial_general = {}

        # Obtener la información del alumno por DNI
        alumno = historial_general.get(dni, None)

        # Si el alumno no existe en el historial, salir de la función
        if not alumno:
            return

        # Obtener la lista de pagos
        historial_pagos = alumno.get("pagos", [])

        # Limpiar el contenido actual del Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar los pagos en el Treeview
        for pago in historial_pagos:
            self.tree.insert('', 'end', values=(
                alumno["dni"], 
                alumno["nombre"], 
                alumno["categoria"], 
                pago["fecha"], 
                pago["monto"], 
                pago["metodo_pago"]  # Se agrega el método de pago
            ))



    def calcular_monto_pago(self, event=None):
        """Calcula el recargo y actualiza el total cuando se ingresa la fecha de pago."""
        fecha_pago = self.entry_fecha_pago.get()

        if fecha_pago:
            try:
                dia_pago = int(fecha_pago.split("/")[0])  # Obtener solo el día
                if dia_pago > 10 and dia_pago<17:
                    monto_adicional = 1000  # Recargo de $1000 por semana de retraso
                elif dia_pago > 16 and dia_pago<24:
                    monto_adicional = 2000 
                elif dia_pago > 23 and dia_pago<32:
                    monto_adicional = 3000
                else:
                    monto_adicional  = 0
            except ValueError:
                monto_adicional = 0  # Si la fecha no es válida, no aplicar recargo
        else:
            monto_adicional = 0

        # Calcular el monto total
        monto_total = self.cuota_base + monto_adicional

        # Actualizar los valores en la interfaz
        self.label_recargo.config(text=f"{monto_adicional:.2f}")
        self.label_total.config(text=f"{monto_total:.2f}")

        # Guardar el monto total en la variable de la clase
        self.monto_a_pagar = monto_total


    def registrar_pago(self):
        dni = self.entry_dni.get()
        metodo_pago = self.var_pago.get()
        fecha_pago = self.entry_fecha_pago.get()

        if not hasattr(self, 'monto_a_pagar'):
            return  # No se puede registrar el pago si no se ha calculado el monto

        # Obtener los detalles del alumno
        

        # Registrar el pago en el historial
        self.registrar_pago_en_historial(dni, self.alumno_encontrado['nombre'], self.alumno_encontrado['categoria'], fecha_pago,self.monto_a_pagar, metodo_pago)

        # Cerrar la ventana después de registrar el pago
        self.venta_finalizada = True
        self.ventanacobrar = False
        print(f"Pago de ${self.monto_a_pagar} registrado para {self.alumno_encontrado['nombre']} ({dni}).")
        self.actualizar_estado_cuota()
        


    def registrar_pago_en_historial(self, dni, nombre, categoria, fecha_pago, monto, metodo_pago):
        archivo_historial = "historial_pagos.json"

        # Cargar historial existente si el archivo ya existe
        if os.path.exists(archivo_historial):
            with open(archivo_historial, "r") as file:
                try:
                    historial_general = json.load(file)
                except json.JSONDecodeError:
                    historial_general = {}
        else:
            historial_general = {}

        # Si el DNI no está en el historial, agregarlo con su información
        if dni not in historial_general:
            historial_general[dni] = {
                "dni": dni,
                "nombre": nombre,
                "categoria": categoria,
                "pagos": []
            }

        # Agregar el nuevo pago al historial del alumno
        historial_general[dni]["pagos"].append({
            "fecha": fecha_pago,
            "monto": monto,
            "metodo_pago": metodo_pago
        })

        # Guardar todo en un solo archivo JSON
        with open(archivo_historial, "w") as file:
            json.dump(historial_general, file, indent=4)

        # Actualizar el Treeview si es necesario
        self.mostrar_historial_pagos(dni)


    def obtener_historial_pago(self, dni):
        # Revisamos si existe el archivo de historial de pagos
        archivo_historial = f"historial_pagos.json"
        if os.path.exists(archivo_historial):
            with open(archivo_historial, "r") as file:
                return json.load(file)
        return []
    def mostrar_ventana_alumnos(self):
        if self.ventanaAlumnos is not False:
            return
        self.previous_window = self.master.focus_get()  # Guardar la ventana activa actual
        self.ventanaAlumnos = True
        self.ventana_alumnos = tk.Toplevel(self.master)
        self.ventana_alumnos.title("Alumnos")
        #self.ventana_alumnos.iconbitmap("images\\boxes.ico") 

        def cerrar_ventana():
            self.toggleAlumnos()
            self.ventana_alumnos.destroy()

        self.ventana_alumnos.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Obtener el tamaño de la pantalla
        screen_width = self.ventana_alumnos.winfo_screenwidth()
        screen_height = self.ventana_alumnos.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 900  # Ajusta el ancho de la ventana
        window_height = 500  # Ajusta la altura de la ventana

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        self.ventana_alumnos.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame para la entrada y el botón de búsqueda
        search_frame = tk.Frame(self.ventana_alumnos)
        search_frame.pack(pady=10)

        label_buscar = tk.Label(search_frame, text="Buscar por nombre o DNI:", font=("Arial", 14))
        label_buscar.pack(pady=5)

        # Entrada de búsqueda
        self.entry_buscar = tk.Entry(search_frame, font=("Arial", 14))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar.bind("<Return>", lambda event: self.buscar_alumno())

        # Botón de búsqueda
        buscar_button = tk.Button(search_frame, text="Buscar", font=("Arial", 14), command=self.buscar_alumno)
        buscar_button.pack(side=tk.LEFT, padx=5)
        

        # Árbol de alumnos
        self.tree = ttk.Treeview(self.ventana_alumnos)
        self.tree['columns'] = ('DNI', 'Nombre', 'Apellido', 'Categoría', 'Cuota')

        # Definir las columnas
        self.tree.column('#0', width=0, stretch=tk.NO)  # Columna invisible
        self.tree.column('DNI', anchor=tk.CENTER, width=150)
        self.tree.column('Nombre', anchor=tk.W, width=200)
        self.tree.column('Apellido', anchor=tk.W, width=200)
        self.tree.column('Categoría', anchor=tk.CENTER, width=100)
        self.tree.column('Cuota', anchor=tk.CENTER, width=150)

        # Definir los encabezados
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('DNI', text='DNI', anchor=tk.CENTER)
        self.tree.heading('Nombre', text='Nombre', anchor=tk.W)
        self.tree.heading('Apellido', text='Apellido', anchor=tk.W)
        self.tree.heading('Categoría', text='Categoría', anchor=tk.CENTER)
        self.tree.heading('Cuota', text='Cuota', anchor=tk.CENTER)

        # Establecer el tamaño de la altura de las filas
        self.tree['height'] = 20

        # Obtener los datos de los alumnos (deberías tener una función que los devuelva)
        alumnos = cargar_alumnos()  # Esta función debería devolver los alumnos en formato adecuado

        for alumno in alumnos:
            self.tree.insert('', tk.END, values=(alumno['dni'], alumno['nombre'], alumno['apellido'], alumno['categoria'], alumno['cuota_estado']))

        # Si no hay modo restrictivo, vincular el evento de doble clic para editar un alumno
        if not self.restrict_mode.get():
            self.tree.bind("<Double-1>", self.editar_alumno)  # Vincular evento de doble clic para editar alumno

        # Empacar el árbol en la ventana
        self.tree.pack(pady=20)

    
    def resource_path(self, relative_path):
        """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para el ejecutable compilado. """
        try:
            # PyInstaller crea una carpeta temporal en _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def impresora(self,texto):
        # Configurar el puerto serie
        puerto = 'COM3'  # Ajusta según el puerto COM de tu impresora en Windows
        baudios = 9600  # Ajusta la velocidad de transmisión según la configuración de tu impresora
        puerto_serie = serial.Serial(puerto, baudios, timeout=1)

        # Comandos de control para la impresora Hasar
        comando_inicial = b'\x1B\x40'  # Inicializar impresora
        comando_tamano_ticket = b'\x1B\x57\x50\x00'  # Establecer ancho del ticket (80mm)
        comando_margenes = b'\x1D\x4C\x20\x00'  # Establecer margen izquierdo (8mm)
        comando_posicion_inicio = b'\x1B\x24\x00\x00'  # Establecer posición de inicio horizontal
        comando_posicion_vertical = b'\x1B\x64\x02'  # Establecer posición de inicio vertical

        try:
            # Enviar comandos de inicialización
            puerto_serie.write(comando_inicial)
            puerto_serie.write(comando_tamano_ticket)
            puerto_serie.write(comando_margenes)
            puerto_serie.write(comando_posicion_inicio)
            puerto_serie.write(comando_posicion_vertical)
            
            # Enviar texto a imprimir
            puerto_serie.write(texto.encode('latin-1'))  # Asegúrate de usar la codificación adecuada

        except Exception as e:
            print("Error al imprimir:", e)
        finally:
            # Cerrar puerto serie
            puerto_serie.close()

    def obtener_fecha_actual(self):
        from datetime import datetime
        return datetime.now().strftime('%d/%m/%Y')


    def agregar_alumno(self):
        # Obtener los valores de los campos de entrada
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        dni = self.dni_entry.get()
        categoria = self.categoria_entry.get()
        cuota_estado = self.cuota_estado.get()

        # Validaciones
        if not nombre or not apellido or not dni or not categoria or not cuota_estado:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Validar que la categoría sea un año de nacimiento válido
        try:
            categoria = int(categoria)
            current_year = datetime.datetime.now().year
            if categoria < 1900 or categoria > current_year:
                raise ValueError("El año de nacimiento debe ser entre 1900 y el año actual.")
        except ValueError as e:
            messagebox.showerror("Error", f"Categoría inválida: {str(e)}")
            return



        if agregar_alumno(dni,nombre,apellido,categoria,cuota_estado):

            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Alumno agregado correctamente.")
            self.ventana_agregar.destroy()
            self.toggleAgregar()
        else: 
            messagebox.showerror("Error", "El alumno con este DNI ya está registrado.")
            return


        # Actualizar la vista de alumnos si es necesario
        if self.ventanaAlumnos:
            self.ventana_alumnos.focus_force()
            self.actualizar_vista_alumnos()
        else:
            self.previous_window.focus_force()



            
    def imprimir_ticket(self):
        now = datetime.datetime.now()
        fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
        total_line_length = 40
        
        ticket_text = ""
        ticket_text += "=" * total_line_length + "\n"
        ticket_text += " " * (int((total_line_length-21)/2)) + "S&S Tienda Multirubro" + " " * int(((total_line_length-21)/2)) + "\n"
        ticket_text += " " * (int((total_line_length-28)/2)) + "Chaco 233 - Obera - Misiones" + " " * int(((total_line_length-28)/2)) + "\n"
        ticket_text += "=" * total_line_length + "\n"
        ticket_text += f"Fecha y Hora: {fecha_hora}\n"
        ticket_text += "-" * total_line_length + "\n"
        ticket_text += f"{'Producto':<20}{'Precio':>10}{'Cantidad':>10}\n"
        ticket_text += "-" * total_line_length + "\n"

        contador = {}

        # Contar las ocurrencias de cada producto
        for item in self.lista_alumnos:
            nombre = item['nombre']
            if nombre in contador:
                contador[nombre]['cantidad'] += 1
            else:
                contador[nombre] = item.copy()  # Crear una copia del diccionario para evitar modificar el original
                contador[nombre]['cantidad'] = 1

        # Crear la nueva lista de diccionarios con la cantidad actualizada
        nueva_lista_diccionarios = list(contador.values())

        for producto in nueva_lista_diccionarios:
            nombre = producto['nombre'][:20]  # Limitar el nombre a 20 caracteres
            precio = f"${producto['precio']:.2f}"
            cantidad = producto['cantidad']
            ticket_text += f"{nombre:<20}{precio:>10}{cantidad:>10}\n"

        ticket_text += "-" * total_line_length + "\n"
        ticket_text += f"{'Precio parcial:':<30}{f'${self.total:.2f}':>10}\n"
        ticket_text += f"{'Descuento:':<30}{f'-${self.monto_descuento:.2f}':>10}\n"
        ticket_text += f"{'Precio final:':<30}{f'${self.total_con_descuento:.2f}':>10}\n"
        ticket_text += "=" * total_line_length + "\n"
        ticket_text += " "*(int((total_line_length-19)/2))+ "Gracias por su compra!"+" "*(int((total_line_length-19)/2))+"\n"
        ticket_text += "=" * total_line_length + "\n"+ " "*(int((total_line_length-15)/2)) +"Tel: 3755-822157"+ " "*(int((total_line_length-15)/2)) +"\n"+ "\n"+ "\n"+ "\n"+ "\n"+ "\n"+ "\n"+ "\n"
        
        print(ticket_text)
        self.impresora(ticket_text)




    def calcular_vuelto(self):
        try:
            total = self.total_con_descuento
            monto_cliente = float(self.monto_cliente_entry.get())
            if monto_cliente >= total:
                vuelto = monto_cliente - total
                self.vuelto_label.config(text=f"Vuelto: ${vuelto:.2f}")
            else:
                messagebox.showerror("Error", "El monto recibido es menor que el total a pagar.")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos.")



    def scroll_text(self, *args):
        """Desplaza automáticamente el texto hacia abajo."""
        self.output_text_cobrar.yview(tk.END)
    def cobrar_producto(self):
        if self.venta_finalizada:
            self.output_text_cobrar.insert(tk.END, "\nLa venta ya ha sido finalizada.\nNo se pueden añadir más productos.\n")
            return

        codigo_de_barras = self.entry_cobrar.get()
        if codigo_de_barras:
            producto = escanear_producto(codigo_de_barras)
            if producto:
                self.lista_alumnos.append(producto)
                self.total += producto['precio']
                self.output_text_cobrar.insert(tk.END, f"Producto añadido: {producto['nombre']} - ${producto['precio']:.2f}\n")

                # Agregar el producto al carrito
                if codigo_de_barras in self.carrito:
                    self.carrito[codigo_de_barras]['cantidad'] += 1
                else:
                    self.carrito[codigo_de_barras] = {
                        'producto': producto,
                        'cantidad': 1
                    }

                # Comprobar el stock restante (temporalmente)
                inventario = cargar_inventario()
                stock_restante = inventario[codigo_de_barras]['cantidad'] - self.carrito[codigo_de_barras]['cantidad']
                if stock_restante <= 3:
                    self.output_text_cobrar.tag_config("rojo", foreground="red")
                    self.output_text_cobrar.insert(tk.END, f"Advertencia: Stock bajo de {producto['nombre']}. Quedan {stock_restante} unidades.\n",("rojo"))

                # Actualizar etiquetas de precio
                precio_parcial = sum(item['producto']['precio'] * item['cantidad'] for item in self.carrito.values())
                descuento = float(self.descuento_entry.get()) if self.descuento_entry.get() else 0
                monto_descuento = precio_parcial * (descuento / 100)
                precio_final = precio_parcial - monto_descuento

                self.precio_parcial_label.config(text=f"Precio parcial: ${precio_parcial:.2f}")
                self.descuento_monto_label.config(text=f"Descuento: ${monto_descuento:.2f}")
                self.precio_final_label.config(text=f"Precio final: ${precio_final:.2f}")
                self.total = precio_parcial
                self.total_con_descuento=precio_final
            else:
                self.output_text_cobrar.insert(tk.END, "Producto no encontrado.\n")
            self.output_text_cobrar.insert(tk.END, "-----------------------------------------------------------------------\n")
            self.output_text_cobrar.see(tk.END)
        self.entry_cobrar.delete(0, tk.END)



    def finalizar_venta(self):
        self.venta_finalizada = True
        self.imprimir_ticket_button.config(state=tk.NORMAL)
        self.output_text_cobrar.delete(1.0, tk.END)  # Limpiar el área de texto
        self.output_text_cobrar.insert(tk.END, "Productos vendidos:\n")
        self.finalizar_button.config(state=tk.DISABLED)

        # Para evitar duplicados y mostrar cantidades correctamente
        productos_unicos = {}
        for producto in self.lista_alumnos:
            nombre = producto['nombre']
            if nombre in productos_unicos:
                productos_unicos[nombre]['cantidad'] += 1
            else:
                productos_unicos[nombre] = {
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': 1
                }

        for nombre, datos in productos_unicos.items():
            self.output_text_cobrar.insert(tk.END, f"{datos['nombre']} - ${datos['precio']:.2f} x {datos['cantidad']}\n")

        self.output_text_cobrar.insert(tk.END, f"\nTotal: ${self.total:.2f}")
        self.output_text_cobrar.insert(tk.END, "\nVenta finalizada. \nNo se pueden añadir más productos.\n")
        
        # Guardar la venta diaria

        guardar_venta_diaria(productos_unicos)
        # Actualizar el inventario real
        inventario = cargar_inventario()
        if len(self.carrito) != 0:
            for codigo, datos in self.carrito.items():
                inventario[codigo]['cantidad'] -= datos['cantidad']
        guardar_inventario(inventario)

        if self.imprimir_ticket_button is None:
            # Crear el botón de imprimir ticket
            self.imprimir_ticket_button = tk.Button(self.output_text_cobrar.master, text="Imprimir Ticket", command=self.imprimir_ticket)

            # Calcular las coordenadas relativas para centrar el botón horizontalmente
            button_width = 150  # Ancho del botón
            x = (self.output_text_cobrar.master.winfo_width() - button_width) // 2
            y = self.output_text_cobrar.master.winfo_height() - 50  # Colocar el botón cerca del borde inferior

            # Posicionar el botón utilizando el método place()
            self.imprimir_ticket_button.place(relx=x / self.output_text_cobrar.master.winfo_width(), rely=y / self.output_text_cobrar.master.winfo_height())

                

    def toggleAlumnos(self):
        self.ventanaAlumnos = False

    def toggleAgregar(self):
        self.ventanaagregar = False    


    def editar_alumno(self, event):
        if self.editando_alumno:
            return  # Si ya se está editando otro alumno, salir de la función
        
        item = self.tree.selection()
        if item:
            # Obtener el DNI del alumno seleccionado
            dni_alumno = self.tree.item(item, "values")[0]  # Suponiendo que el DNI está en la primera columna
            alumnos = cargar_alumnos()  # Esto devuelve una lista de alumnos

            # Buscar el alumno en la lista
            alumno = next((a for a in alumnos if a["dni"] == dni_alumno), None)

            if alumno:
                # Mostrar ventana similar a agregar alumno pero con datos del alumno seleccionado
                self.editando_alumno = True
                self.mostrar_ventana_agregar(
                    editar=True, 
                    dni=alumno["dni"], 
                    nombre=alumno["nombre"], 
                    apellido=alumno["apellido"], 
                    categoria=alumno["categoria"], 
                    cuota_estado=alumno["cuota_estado"]
                )
                self.toggleAgregar()


    def eliminar_alumno(self, dni):
        print("entra")
        if eliminar(dni):  # Llamar a la función eliminar con el DNI
            messagebox.showinfo("Éxito", "Alumno eliminado correctamente.")
            self.ventana_agregar.destroy()  # Cierra la ventana de agregar si es necesario
            self.actualizar_vista_alumnos()  # Actualiza la vista de los alumnos
            self.editando_producto = False  # Marca que no está editando un producto
            self.toggleAgregar()  # Alterna el estado de agregar
            if self.ventanaAlumnos:
                self.ventana_alumnos.focus_force()  # Trae al frente la ventana de alumnos
            else:
                self.previous_window.focus_force()  # Trae al frente la ventana anterior
        self.editando_alumno=False


    def guardar_alumno_editado(self, dni):
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        categoria = self.categoria_entry.get()
        cuota_estado = self.cuota_estado.get()
        dni_nuevo = self.dni_entry.get()  # Nuevo DNI en caso de edición

        print(f"Valores ingresados en guardar_alumno_editado: dni={dni}, nombre={nombre}, apellido={apellido}, categoría={categoria}, cuota_estado={cuota_estado}")

        # Validar que los campos no estén vacíos
        if not nombre or not apellido or not categoria or not cuota_estado or not dni_nuevo:
            messagebox.showerror("Error", "Todos los campos deben ser completados.")
            return

        # Validar que el DNI sea numérico
        if not dni.isdigit() or not dni_nuevo.isdigit():
            messagebox.showerror("Error", "El DNI debe contener solo números.")
            return

        # Validar que el nuevo DNI no esté en uso por otro alumno
        alumnos = cargar_alumnos()  # Cargar la lista de alumnos
        if dni_nuevo != dni and any(alumno['dni'] == dni_nuevo for alumno in alumnos):
            messagebox.showerror("Error", "El nuevo DNI ya está registrado por otro alumno.")
            return

        # Llamar a la función para modificar el alumno
        if modificar_alumno(dni, nombre, apellido, categoria, cuota_estado, dni_nuevo):
            messagebox.showinfo("Éxito", "Alumno editado correctamente.")
            self.ventana_agregar.destroy()
            self.actualizar_vista_alumnos()
            self.toggleAgregar()
            self.editando_alumno = False

            # Asegurar que la ventana de alumnos no genere errores
            if hasattr(self, 'ventana_alumnos') and self.ventana_alumnos:
                self.ventana_alumnos.focus_force()
            elif hasattr(self, 'previous_window') and self.previous_window:
                self.previous_window.focus_force()
        else:
            messagebox.showerror("Error", "No se pudo editar el alumno.")
            self.editando_alumno = False

    def buscar_alumno(self):
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener término de búsqueda
        termino_busqueda = self.entry_buscar.get()

        # Buscar por nombre, apellido o DNI
        alumnos = cargar_alumnos()  # Cargar la lista de alumnos

        for alumno in alumnos:
            # Compara el término de búsqueda con el nombre, apellido o DNI
            if (termino_busqueda.lower() in alumno['nombre'].lower() or 
                termino_busqueda.lower() in alumno['apellido'].lower() or 
                termino_busqueda == alumno['dni']):
                # Insertar los datos del alumno en el árbol
                self.tree.insert('', tk.END, values=(alumno['dni'], alumno['nombre'], alumno['apellido'], alumno['categoria'], alumno['cuota_estado']))


    def actualizar_vista_alumnos(self):
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener los alumnos actualizados (deberías tener una función que los devuelva)
        alumnos = cargar_alumnos()  # Esta función debe devolver los alumnos en formato adecuado

        # Mostrar los alumnos en el árbol
        for alumno in alumnos:
            self.tree.insert('', tk.END, values=(alumno['dni'], alumno['nombre'], alumno['apellido'], alumno['categoria'], alumno['cuota_estado']))

    def actualizar_estado_cuota(self):
        alumnos_path='alumnos.json'
        historial_path='historial_pagos.json'
        # Cargar los archivos JSON
        with open(alumnos_path, 'r') as f:
            alumnos = json.load(f)

        # Verificar si el archivo historial_pagos.json existe
        if os.path.exists(historial_path):
            with open(historial_path, 'r') as f:
                historial_pagos = json.load(f)
        else:
            historial_pagos = {}  # Si no existe, inicializamos un diccionario vacío

        # Fecha actual
        fecha_actual = datetime.now()

        for alumno in alumnos:
            dni = alumno["dni"]
            # Inicializamos el estado de cuota como "AL DIA"
            alumno["cuota_estado"] = "AL DIA"

            # Verificar si el alumno tiene historial de pagos
            if dni in historial_pagos:
                pagos = historial_pagos[dni]["pagos"]
                
                # Si el alumno tiene pagos
                if pagos:
                    # Obtener la última fecha de pago
                    ultima_fecha_pago = pagos[-1]["fecha"]
                    ultima_fecha_pago = datetime.strptime(ultima_fecha_pago, "%d/%m/%Y")

                    # Calcular la diferencia en días entre la fecha actual y la última fecha de pago
                    dias_diferencia = (fecha_actual - ultima_fecha_pago).days

                    # Si han pasado más de 29 días, actualizar el estado a "MOROSO"
                    if dias_diferencia > 29:
                        alumno["cuota_estado"] = "MOROSO"
                else:
                    # Si no hay pagos, mantener el estado como "AL DIA"
                    alumno["cuota_estado"] = "AL DIA"
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")                 
        # Guardar los cambios en el archivo alumnos.json
        with open(alumnos_path, 'w') as f:
            json.dump(alumnos, f, indent=4)




# Crear la ventana principal de la aplicación
root = tk.Tk()
app = InventarioApp(root)
root.mainloop()
