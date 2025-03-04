import tkinter as tk
from tkinter import ttk, messagebox
from inventario import escanear_producto, agregar_producto, cargar_inventario, modificar_producto, eliminar, guardar_inventario
from ventadiaria import guardar_venta_diaria
import datetime
import serial
import os
import sys
import json
from tkcalendar import DateEntry
from tkinter import BooleanVar

class InventarioApp:
    def __init__(self, master):
        self.master = master
        master.title("SATO APP")
        self.ventanaagregar = False
        self.ventanaInventario = False
        self.editando_producto = False
        self.lista_productos = []
        self.venta_finalizada = False
        self.ventanavender = False
        self.ventanacaja = False
        self.total_con_descuento = 0 
        self.total_con_descuento = 0
        self.restrict_mode = BooleanVar()
        self.restrict_mode.set(self.cargar_estado_restriccion())

        nombre_label = tk.Label(self.master, text="Desarrollado por Agustin Goyechea V1.1", font=("Arial", 6))
        nombre_label.pack(side=tk.BOTTOM, pady=10)

        # Cargar imágenes usando rutas relativas
        self.add_icon = tk.PhotoImage(file=self.resource_path("images/agregar.png"))
        self.sell_icon = tk.PhotoImage(file=self.resource_path("images/venta.png"))
        self.view_icon = tk.PhotoImage(file=self.resource_path("images/inventario.png"))
        self.caja_icon = tk.PhotoImage(file=self.resource_path("images/caja.png"))  # Asegúrate de tener esta imagen

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(pady=20)
        self.caja_icon = self.caja_icon.subsample(10,10)

        self.add_button = tk.Button(self.buttons_frame, text="Agregar Nuevo Producto", image=self.add_icon, compound=tk.LEFT, command=self.mostrar_ventana_agregar,  state=tk.DISABLED if self.restrict_mode.get() else tk.NORMAL)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.sell_button = tk.Button(self.buttons_frame, text="Vender", image=self.sell_icon, compound=tk.LEFT, command=self.mostrar_ventana_cobrar)
        self.sell_button.pack(side=tk.LEFT, padx=10)

        self.view_button = tk.Button(self.buttons_frame, text="Ver Inventario", image=self.view_icon, compound=tk.LEFT, command=self.mostrar_ventana_inventario)
        self.view_button.pack(side=tk.LEFT, padx=10)

        self.caja_button = tk.Button(self.buttons_frame, text="Caja", image=self.caja_icon, compound=tk.LEFT, command=self.mostrar_ventana_caja)
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
        contraseña_correcta = "satomultirubro"  # Reemplaza esto con la contraseña correcta
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
        


    def mostrar_ventana_agregar(self, editar=False, nombre="", codigo="", cantidad="", precio=""):
        if self.ventanaagregar is not False:
            return
        
        self.previous_window = self.master.focus_get()
        self.ventanaagregar = True
        self.ventana_agregar = tk.Toplevel(self.master)
        self.ventana_agregar.title("Agregar Nuevo Producto" if not editar else "Editar Producto")
        #self.ventana_agregar.iconbitmap("images\\add.ico") 

        def cerrar_ventana():
            self.toggleAgregar()  # Llama al método toggleAgregar cuando se cierra la ventana
            self.ventana_agregar.destroy()
            self.editando_producto=False
        
        self.ventana_agregar.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Crear el frame principal para centrar todos los widgets
        main_frame = tk.Frame(self.ventana_agregar, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(main_frame, text="Nombre:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.nombre_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.nombre_entry.focus_set()
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=5)
        self.nombre_entry.insert(tk.END, nombre)

        tk.Label(main_frame, text="Código de Barras:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.codigo_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.codigo_entry.grid(row=1, column=1, padx=10, pady=5)
        if codigo:
            self.codigo_entry.insert(tk.END, codigo)

        tk.Label(main_frame, text="Cantidad:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.cantidad_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.cantidad_entry.grid(row=2, column=1, padx=10, pady=5)
        self.cantidad_entry.insert(tk.END, cantidad)

        tk.Label(main_frame, text="Precio:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.precio_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.precio_entry.grid(row=3, column=1, padx=10, pady=5)
        self.precio_entry.insert(tk.END, precio)

        botones_frame = tk.Frame(main_frame)
        botones_frame.grid(row=4, column=0, columnspan=2, pady=10)

        if editar:
            guardar_button = tk.Button(botones_frame, text="Guardar", font=("Arial", 14), command=lambda: self.guardar_producto_editado(codigo))
            guardar_button.pack(side=tk.LEFT, padx=5)
            eliminar_button = tk.Button(botones_frame, text="Eliminar", font=("Arial", 14), command=lambda: self.eliminar_producto(codigo))
            eliminar_button.pack(side=tk.LEFT, padx=5)
            
        else:
            agregar_button = tk.Button(botones_frame, text="Agregar", font=("Arial", 14), command=self.agregar_producto)
            agregar_button.pack(side=tk.LEFT, padx=5)
            

        # Centrar la ventana en la pantalla
        self.ventana_agregar.update_idletasks()
        width = self.ventana_agregar.winfo_width()
        height = self.ventana_agregar.winfo_height()
        
        x = (self.ventana_agregar.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana_agregar.winfo_screenheight() // 2) - (height // 2)
        self.ventana_agregar.geometry(f"{width}x{height}+{x}+{y-100}")

        return self.ventana_agregar





    def mostrar_ventana_cobrar(self):
        if self.ventanavender is not False:
            return
        self.venta_finalizada = False
        self.carrito = {}  # Reiniciar el carrito aquí
        self.lista_productos = []
        self.total = 0
        self.ventanavender = True
        ventana_cobrar = tk.Toplevel(self.master)
        ventana_cobrar.title("Vender")

        def cerrar_ventana():
            self.venta_finalizada = False
            self.ventanavender = False
            ventana_cobrar.destroy()

        ventana_cobrar.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Frame para la entrada y el botón de cobrar
        input_frame = tk.Frame(ventana_cobrar)
        input_frame.pack(pady=5)

        # Etiqueta y entrada para el código de barras
        label = tk.Label(input_frame, text="Ingrese el código de barras:", font=("Arial", 14))
        label.pack(side=tk.LEFT, padx=5)
        self.entry_cobrar = tk.Entry(input_frame, font=("Arial", 14), width=30)
        self.entry_cobrar.pack(side=tk.LEFT, padx=5)

        # Asignar la función cobrar_producto al evento Return (Enter)
        self.entry_cobrar.bind("<Return>", lambda event: self.cobrar_producto())
        self.entry_cobrar.focus_set()

        # Botón para añadir al carrito
        cobrar_button = tk.Button(input_frame, text="Añadir al carrito", font=("Arial", 14), command=self.cobrar_producto)
        cobrar_button.pack(side=tk.LEFT, padx=5)

        # Botón para finalizar venta
        self.finalizar_button = tk.Button(input_frame, text="Finalizar venta", font=("Arial", 14), command=self.finalizar_venta)
        self.finalizar_button.pack(side=tk.LEFT, padx=5)
        self.finalizar_button.config(state=tk.NORMAL)


        # Frame para el área de texto y la barra de desplazamiento
        text_frame = tk.Frame(ventana_cobrar)
        text_frame.pack(pady=10, fill=tk.BOTH, expand=False)

        # Usar grid para organizar el text_frame
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Área de texto para mostrar los productos y el total
        self.output_text_cobrar = tk.Text(text_frame, height=11, width=60, font=("Arial", 14))
        self.output_text_cobrar.grid(row=0, column=0, sticky="nsew")

        # Añadir una barra de desplazamiento
        scrollbar = tk.Scrollbar(text_frame, command=self.output_text_cobrar.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text_cobrar.config(yscrollcommand=scrollbar.set)

        # Frame para los detalles del precio
        detalles_precio_frame = tk.Frame(ventana_cobrar)
        detalles_precio_frame.pack(side=tk.RIGHT, padx=20, pady=10, anchor="se")

        self.precio_parcial_label = tk.Label(detalles_precio_frame, text="Precio parcial: $0.0", font=("Arial", 14), foreground="blue")
        self.precio_parcial_label.pack(anchor="e")

        self.descuento_monto_label = tk.Label(detalles_precio_frame, text="Descuento: $0.0", font=("Arial", 14), foreground="green")
        self.descuento_monto_label.pack(anchor="e")

        self.precio_final_label = tk.Label(detalles_precio_frame, text="Precio final: $0.0", font=("Arial", 14, "bold"), foreground="red")
        self.precio_final_label.pack(anchor="e")

        self.vuelto_label = tk.Label(detalles_precio_frame, text="Vuelto: $0.0", font=("Arial", 14, "bold"), foreground="purple")
        self.vuelto_label.pack(anchor="e")

        

        screen_width = ventana_cobrar.winfo_screenwidth()
        screen_height = ventana_cobrar.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 950  # Establecer el ancho de la ventana
        window_height = 550  # Establecer la altura de la ventana

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        ventana_cobrar.geometry(f"{window_width}x{window_height}+{x}+{y+60}")

        # Frame para el monto recibido y los botones "Calcular Vuelto" e "Imprimir Ticket"
        monto_y_botones_frame = tk.Frame(ventana_cobrar)
        monto_y_botones_frame.place(relx=0.5, rely=0.9, anchor="s")
 
        # Etiqueta y entrada para el descuento
        descuento_label = tk.Label(monto_y_botones_frame, text="Descuento (%):", font=("Arial", 14))
        descuento_label.grid(row=2, column=0, padx=5, pady=5)

        monto_cliente_label = tk.Label(monto_y_botones_frame, text="Monto recibido del cliente:", font=("Arial", 14))
        monto_cliente_label.grid(row=3, column=0, padx=5, pady=5)
        self.monto_cliente_entry = tk.Entry(monto_y_botones_frame, font=("Arial", 14))
        self.monto_cliente_entry.grid(row=3, column=1, padx=5, pady=5)

        calcular_button = tk.Button(monto_y_botones_frame, text="Calcular Vuelto", font=("Arial", 14), command=self.calcular_vuelto)
        calcular_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.imprimir_ticket_button = tk.Button(monto_y_botones_frame, text="Imprimir Ticket", font=("Arial", 14), command=self.imprimir_ticket, state=tk.DISABLED)
        self.imprimir_ticket_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        # Inicializar la entrada del descuento a 0
        self.descuento_entry = tk.Entry(monto_y_botones_frame, font=("Arial", 14))
        self.descuento_entry.grid(row=2, column=1, padx=5, pady=5)
        self.descuento_entry.insert(0, "0")  # Inicializar con 0
        descuento = float(self.descuento_entry.get()) if self.descuento_entry.get() else 0.0
        self.monto_descuento = self.total * (descuento / 100)
        self.total_con_descuento = self.total - self.monto_descuento
        print(self.total)
  
        def calcular_total_con_descuento():
            try:
                descuento = float(self.descuento_entry.get()) if self.descuento_entry.get() else 0.0
                if descuento < 0 or descuento > 100:
                    raise ValueError
            except ValueError:
                self.precio_final_label.config(text="Precio final: $0.0")
                return

            self.monto_descuento = self.total * (descuento / 100)
            self.total_con_descuento = self.total - self.monto_descuento

            self.precio_parcial_label.config(text=f"Precio parcial: ${self.total:.2f}")
            self.descuento_monto_label.config(text=f"Descuento: - ${self.monto_descuento:.2f}")
            self.precio_final_label.config(text=f"Precio final: ${self.total_con_descuento:.2f}")

        self.descuento_entry.bind("<KeyRelease>", lambda event: calcular_total_con_descuento())



    def mostrar_ventana_inventario(self):
        if self.ventanaInventario is not False:
            return
        self.previous_window = self.master.focus_get()  # Guardar la ventana activa actual
        self.ventanaInventario = True
        self.ventana_inventario = tk.Toplevel(self.master)
        self.ventana_inventario.title("Ver Inventario")
        #self.ventana_inventario.iconbitmap("images\\boxes.ico") 

        def cerrar_ventana():
            self.toggleInventario()
            self.ventana_inventario.destroy()

        self.ventana_inventario.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Obtener el tamaño de la pantalla
        screen_width = self.ventana_inventario.winfo_screenwidth()
        screen_height = self.ventana_inventario.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 900  # Ajusta el ancho de la ventana
        window_height = 500  # Ajusta la altura de la ventana

        # Calcular las coordenadas para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana para que aparezca en el centro
        self.ventana_inventario.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame para la entrada y el botón de búsqueda
        search_frame = tk.Frame(self.ventana_inventario)
        search_frame.pack(pady=10)

        label_buscar = tk.Label(search_frame, text="Buscar por nombre o por código de barras:", font=("Arial", 14))
        label_buscar.pack(pady=5)

        # Entrada de búsqueda
        self.entry_buscar = tk.Entry(search_frame, font=("Arial", 14))
        self.entry_buscar.pack(side=tk.LEFT, padx=5)

        self.entry_buscar.bind("<Return>", lambda event: self.buscar_producto())

        # Botón de búsqueda
        buscar_button = tk.Button(search_frame, text="Buscar", font=("Arial", 14), command=self.buscar_producto)
        buscar_button.pack(side=tk.LEFT, padx=5)
        

        # Árbol de productos
        self.tree = ttk.Treeview(self.ventana_inventario)
        self.tree['columns'] = ('Cantidad', 'Nombre', 'Código de Barras', 'Precio')

        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('Cantidad', anchor=tk.CENTER, width=200)
        self.tree.column('Nombre', anchor=tk.W, width=250)
        self.tree.column('Código de Barras', anchor=tk.CENTER, width=200)
        self.tree.column('Precio', anchor=tk.CENTER, width=200)

        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('Cantidad', text='Cantidad', anchor=tk.CENTER)
        self.tree.heading('Nombre', text='Nombre', anchor=tk.W)
        self.tree.heading('Código de Barras', text='Código de Barras', anchor=tk.CENTER)
        self.tree.heading('Precio', text='Precio', anchor=tk.CENTER)
        self.tree['height'] = 20

        productos = cargar_inventario()
        for codigo, datos in productos.items():
            self.tree.insert('', tk.END, values=(datos['cantidad'], datos['nombre'], codigo, datos['precio']))


        if not self.restrict_mode.get():
            self.tree.bind("<Double-1>", self.editar_producto)  # Vincular evento de doble clic para editar producto


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



    def agregar_producto(self):
        codigo_de_barras = self.codigo_entry.get()
        nombre = self.nombre_entry.get()
        nombre= nombre.upper()
        try:
            precio = float(self.precio_entry.get())
            cantidad = int(self.cantidad_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Precio y cantidad deben ser números.")
            return

        if agregar_producto(codigo_de_barras, nombre, precio, cantidad):
            messagebox.showinfo("Éxito", "Producto agregado al inventario.")
            self.ventana_agregar.destroy()
            self.toggleAgregar()
            if self.ventanaInventario:
                self.ventana_inventario.focus_force()
                self.actualizar_vista_inventario()
            else:
                self.previous_window.focus_force()
        else:
            messagebox.showerror("Error", "El producto ya existe en el inventario.")
            
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
        for item in self.lista_productos:
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
                self.lista_productos.append(producto)
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
        for producto in self.lista_productos:
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

                





       

    def toggleInventario(self):
        self.ventanaInventario = False

    def toggleAgregar(self):
        self.ventanaagregar = False    


    def editar_producto(self, event):
        if self.editando_producto:
            return  # Si ya se está editando otro producto, salir de la función
        item = self.tree.selection()
        if item:
            # Obtener el código de barras del producto seleccionado
            codigo_de_barras = self.tree.item(item, "values")[2]  # El índice 2 indica la columna del código de barras
            producto = cargar_inventario().get(codigo_de_barras)

            if producto:
                # Mostrar ventana similar a agregar producto pero con datos del producto seleccionado
                self.editando_producto = True
                self.mostrar_ventana_agregar(editar=True, codigo=codigo_de_barras, nombre=producto['nombre'], cantidad=producto['cantidad'], precio=producto['precio'])
                self.toggleAgregar()
            else:
                messagebox.showerror("Error", "El producto seleccionado no existe en el inventario.")


    def eliminar_producto(self, codigo):

        if eliminar(codigo):
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            self.ventana_agregar.destroy()
            self.actualizar_vista_inventario()
            self.editando_producto = False
            self.toggleAgregar()
            if self.ventanaInventario:
                self.ventana_inventario.focus_force()
            else:
                self.previous_window.focus_force()


    def guardar_producto_editado(self, codigo):
        nombre = self.nombre_entry.get()
        cantidad = self.cantidad_entry.get()
        precio = self.precio_entry.get()
        codigonuevo = self.codigo_entry.get()
    


        print(f"Valores ingresados en guardar_producto_editado: nombre={nombre}, cantidad={cantidad}, precio={precio}, codigo={codigo}")

        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un entero y precio debe ser un número.")
            return

        print(f"Valores convertidos en guardar_producto_editado: nombre={nombre}, cantidad={cantidad}, precio={precio}, codigo={codigo}")

        if modificar_producto(codigo, nombre, precio, cantidad, codigonuevo):
            messagebox.showinfo("Éxito", "Producto editado correctamente.")
            self.ventana_agregar.destroy()
            self.actualizar_vista_inventario()
            self.toggleAgregar()
            self.editando_producto = False
            if self.ventanaInventario:
                self.ventana_inventario.focus_force()
            else:
                self.previous_window.focus_force()
        else:
            messagebox.showerror("Error", "No se pudo editar el producto.")
            self.ventanaagregar = False
            self.editando_producto = False


    def buscar_producto(self):
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener término de búsqueda
        termino_busqueda = self.entry_buscar.get()

        # Buscar por nombre o código de barras
        productos = cargar_inventario()
        for codigo, datos in productos.items():
            if termino_busqueda.lower() in datos['nombre'].lower() or termino_busqueda == codigo:
                self.tree.insert('', tk.END, values=(datos['cantidad'], datos['nombre'], codigo, datos['precio']))
        

    def actualizar_vista_inventario(self):
            # Limpiar árbol
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Obtener los productos del inventario actualizado
            productos = cargar_inventario()

            # Mostrar los productos en el árbol
            for codigo, datos in productos.items():
                self.tree.insert('', tk.END, values=(datos['cantidad'], datos['nombre'], codigo, datos['precio']))


# Crear la ventana principal de la aplicación
root = tk.Tk()
app = InventarioApp(root)
root.mainloop()
