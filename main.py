import tkinter as tk
from tkinter import ttk, messagebox
from inventario import escanear_alumno, agregar_alumno, cargar_alumnos, modificar_alumno, eliminar, guardar_alumno
from datetime import datetime
from sender_mail import enviar_comprobante
import os
import sys
import json
from tkcalendar import Calendar
from tkinter import BooleanVar
from generador_comprobante import generar_recibo_profesional
import webbrowser
import tkinter as tk
from PIL import Image, ImageTk

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
        self.ventana_contraseña = None  # Inicializa la variable
        self.ventanabalance = False
        self.total_con_descuento = 0 
        self.total_con_descuento = 0
        self.cuota_base = 0
        self.restrict_mode = BooleanVar()
        self.restrict_mode.set(self.cargar_estado_restriccion())
        self.alumno_encontrado = None
        self.calendario_icono = tk.PhotoImage(file=self.resource_path("images/calendar.png")).subsample(2,2)    
        self.buscar_icono = tk.PhotoImage(file=self.resource_path("images/buscar.png")).subsample(2,2)    
        nombre_label = tk.Label(self.master, text="Desarrollado por Agustin Goyechea V1.1", font=("Arial", 6))
        nombre_label.pack(side=tk.BOTTOM, pady=10)

        # Cargar imágenes usando rutas relativas
        self.add_icon = tk.PhotoImage(file=self.resource_path("images/agregar_jugador.png"))
        self.sell_icon = tk.PhotoImage(file=self.resource_path("images/cobro.png"))
        self.view_icon = tk.PhotoImage(file=self.resource_path("images/lista.png"))
        self.caja_icon = tk.PhotoImage(file=self.resource_path("images/balance.png"))  # Asegúrate de tener esta imagen
        self.historial_icon = tk.PhotoImage(file=self.resource_path("images/historial.png"))

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(pady=20)
        

        self.add_button = tk.Button(self.buttons_frame, text="Agregar Alumno", image=self.add_icon, compound=tk.LEFT, command=self.mostrar_ventana_agregar,  state=tk.DISABLED if self.restrict_mode.get() else tk.NORMAL)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.sell_button = tk.Button(self.buttons_frame, text="Cobrar", image=self.sell_icon, compound=tk.LEFT, command=self.mostrar_ventana_cuota, state=tk.DISABLED if self.restrict_mode.get() else tk.NORMAL)
        self.sell_button.pack(side=tk.LEFT, padx=10)

        self.view_button = tk.Button(self.buttons_frame, text="Lista Alumnos", image=self.view_icon, compound=tk.LEFT, command=self.mostrar_ventana_alumnos)
        self.view_button.pack(side=tk.LEFT, padx=10)

        self.caja_button = tk.Button(self.buttons_frame, text="Balance", image=self.caja_icon, compound=tk.LEFT, command=self.mostrar_ventana_balance, state=tk.DISABLED if self.restrict_mode.get() else tk.NORMAL)
        self.caja_button.pack(side=tk.LEFT, padx=10)

        self.historial_button = tk.Button(
        self.buttons_frame,
        text="Historial de Pagos",
        image=self.historial_icon,
        compound=tk.LEFT,
        command=self.mostrar_ventana_historial
        )
        self.historial_button.pack(side=tk.LEFT, padx=10)
        # Añadir el switch de restricción
        self.restrict_switch = tk.Checkbutton(self.master, text="Modo Restricción", variable=self.restrict_mode, command=self.toggle_restriccion)
        self.restrict_switch.pack(pady=10)

        # Obtener el tamaño de la pantalla
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Obtener el tamaño de la ventana
        window_width = 750 # Ajusta según sea necesario
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



    def mostrar_ventana_historial(self):
        if getattr(self, "ventanahistorial", False):
            return
        self.ventanahistorial = True

        def cerrar_ventana():
            self.ventanahistorial = False
            historial_window.destroy()

        def actualizar_tabla():
            for item in tree.get_children():
                tree.delete(item)

            año_seleccionado = int(año_combobox.get())
            categoria_seleccionada = categoria_combobox.get()
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

            filas = {}
            try:
                with open("historial_pagos.json", "r", encoding="utf-8") as archivo:
                    historial_pagos = json.load(archivo)
            except FileNotFoundError:
                historial_pagos = {}

            for dni, datos in historial_pagos.items():
                categoria = str(datos.get("categoria", ""))
                if categoria_seleccionada != "Todas" and categoria != categoria_seleccionada:
                    continue

                nombre_completo = f"{datos.get('apellido', '')}, {datos.get('nombre', '')}"
                clave = (categoria, nombre_completo)

                if clave not in filas:
                    filas[clave] = [""] * 12  # Una celda por cada mes

                for pago in datos.get("pagos", []):
                    try:
                        fecha_pago = datetime.strptime(pago["fecha"], "%d/%m/%Y")
                    except (ValueError, KeyError):
                        continue  # Fecha mal formada o inexistente

                    if fecha_pago.year == año_seleccionado:
                        mes = pago.get("mes_pagado")
                        if mes in meses:
                            index = meses.index(mes)
                            filas[clave][index] = "⚽"

            for (categoria, nombre), pagos_mes in sorted(filas.items(), key=lambda x: (x[0][0], x[0][1])):
                tree.insert("", tk.END, values=[categoria, nombre] + pagos_mes)


        # Crear ventana
        historial_window = tk.Toplevel(self.master)
        historial_window.title("Historial de Pagos")
        historial_window.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Establecer tamaño deseado primero
        historial_window.geometry("1250x500")
        historial_window.update_idletasks()

        # Luego centrar
        w = historial_window.winfo_width()
        h = historial_window.winfo_height()
        ws = historial_window.winfo_screenwidth()
        hs = historial_window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        historial_window.geometry(f"1250x500+{x}+{y}")



        # Frame superior con filtros
        top_frame = tk.Frame(historial_window)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Año:").pack(side=tk.LEFT)
        año_actual = datetime.now().year
        años = [str(año_actual - i) for i in range(5)]
        año_combobox = ttk.Combobox(top_frame, values=años, state="readonly", width=5)
        año_combobox.set(str(año_actual))
        año_combobox.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Categoría:").pack(side=tk.LEFT)
        try:
            with open("historial_pagos.json", "r", encoding="utf-8") as archivo:
                historial_pagos = json.load(archivo)
                categorias = sorted({str(datos["categoria"]) for datos in historial_pagos.values()})
        except FileNotFoundError:
            categorias = []

        categorias.insert(0, "Todas")
        categoria_combobox = ttk.Combobox(top_frame, values=categorias, state="readonly", width=10)
        categoria_combobox.set("Todas")
        categoria_combobox.pack(side=tk.LEFT, padx=5)

        actualizar_button = tk.Button(top_frame, text="Actualizar", command=actualizar_tabla)
        actualizar_button.pack(side=tk.LEFT, padx=10)

        # Treeview con columna "Categoría" y "Nombre"
        columns = ["Categoría", "Nombre", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        tree = ttk.Treeview(historial_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80 if col not in ["Categoría", "Nombre"] else 120, anchor="center")
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        actualizar_tabla()  # Mostrar datos iniciales



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
            self.caja_button.config(state=tk.DISABLED)
            self.sell_button.config(state=tk.DISABLED)
            self.guardar_estado_restriccion()
        else:
            self.solicitar_contraseña()

    def solicitar_contraseña(self):
        if self.ventana_contraseña is not None and tk.Toplevel.winfo_exists(self.ventana_contraseña):
            return  # Evita abrir múltiples ventanas
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
        self.entry_contraseña.focus_set()
        boton_aceptar = tk.Button(self.ventana_contraseña, text="Aceptar", font=("Arial", 14), command=self.verificar_contraseña)
        boton_aceptar.pack(pady=10)
        self.ventana_contraseña.bind("<Return>", lambda event: self.verificar_contraseña())

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
            self.caja_button.config(state=tk.NORMAL)
            self.sell_button.config(state=tk.NORMAL)
            self.guardar_estado_restriccion()
            messagebox.showinfo("Modo Restricción", "Modo restricción desactivado.")
            self.ventana_contraseña.destroy()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
            self.entry_contraseña.delete(0, tk.END)
    
    def mostrar_ventana_balance(self):
        if self.ventanabalance:
            return
        self.ventanabalance = True
        def actualizar_balance():
            mostrar_mensaje("")
            for item in tree.get_children():
                tree.delete(item)
            
            fecha_inicio = date_entry_inicio.get()
            fecha_fin = date_entry_fin.get()
            
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d/%m/%Y")
                fecha_fin_dt = datetime.strptime(fecha_fin, "%d/%m/%Y")
                
            except ValueError:
                mostrar_mensaje("Ingrese fechas válidas")
                return
            
            total_efectivo = 0
            total_transferencia = 0
            pagos_realizados = []
            
            for dni, datos in historial_pagos.items():
                for pago in datos["pagos"]:
                    fecha_pago_dt = datetime.strptime(pago["fecha"], "%d/%m/%Y")
                    if fecha_inicio_dt <= fecha_pago_dt <= fecha_fin_dt:
                        pagos_realizados.append((pago["fecha"], datos["nombre"], datos["apellido"], pago["monto"], pago["metodo_pago"]))
                        if pago["metodo_pago"].lower() == "efectivo":
                            total_efectivo += pago["monto"]
                        else:
                            total_transferencia += pago["monto"]
            
            for pago in pagos_realizados:
                tree.insert("", tk.END, values=pago)
            
            efectivo_value_label.config(text=f"${total_efectivo:.2f}")
            transferencia_value_label.config(text=f"${total_transferencia:.2f}")
            abonado_value_label.config(text=f"${total_efectivo + total_transferencia:.2f}")
        balance_window = tk.Toplevel(self.master)
        balance_window.title("Balance de Pagos")
            
           
        mensaje_label = tk.Label(balance_window, text="", font=("Arial", 12), fg="red", width=40)
        mensaje_label.grid(row=5, column=0, columnspan=3, pady=5)

        def mostrar_mensaje(mensaje):
            """Muestra un mensaje en la etiqueta o lo borra si es vacío."""
            mensaje_label.config(text=" " if mensaje == "" else mensaje)
            mensaje_label.update_idletasks()  # Actualiza la interfaz para reflejar el cambio inmediatamente


        screen_width = balance_window.winfo_screenwidth()
        screen_height = balance_window.winfo_screenheight()
        window_width = 850
        window_height = 550
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        balance_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        def cerrar_ventana():
            self.ventanabalance = False
            balance_window.destroy()
        
        balance_window.protocol("WM_DELETE_WINDOW", cerrar_ventana)
        
        try:
            with open("historial_pagos.json", "r") as file:
                historial_pagos = json.load(file)
        except FileNotFoundError:
            historial_pagos = {}
        balance_window.columnconfigure(1, weight=1)
        tk.Label(balance_window, text="Fecha inicio (dd/mm/aaaa):", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, padx=10)
        date_entry_inicio = tk.Entry(balance_window, font=("Arial", 14))
        date_entry_inicio.grid(row=0, column=1, pady=5, padx=1,sticky="ew")
        
      
        # Botón para seleccionar la fecha de inicio
        calendario_button_inicio = tk.Button(balance_window, image=self.calendario_icono, text="Seleccionar Fecha", font=("Arial", 14), command=lambda: self.mostrar_calendario(date_entry_inicio))
        calendario_button_inicio.grid(row=0, column=2, padx=2,sticky="w")
        
        tk.Label(balance_window, text="Fecha fin (dd/mm/aaaa):", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=5, padx=10)
        date_entry_fin = tk.Entry(balance_window, font=("Arial", 14))
        date_entry_fin.grid(row=1, column=1, pady=5, padx=1,sticky="ew")
        
        # Botón para seleccionar la fecha de fin
        calendario_button_fin = tk.Button(balance_window,image=self.calendario_icono, font=("Arial", 14), command=lambda: self.mostrar_calendario(date_entry_fin))
        calendario_button_fin.grid(row=1, column=2, padx=2,sticky="w")
        tk.Button(balance_window, text="Mostrar Balance", command=actualizar_balance).grid(row=2, column=0, columnspan=3, pady=10)
        
        tree = ttk.Treeview(balance_window, columns=("Fecha", "Nombre","Apellido", "Monto", "Método de Pago"), show="headings")
        tree.heading("Fecha", text="Fecha")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Apellido", text="Apellido")
        tree.heading("Monto", text="Monto")
        tree.heading("Método de Pago", text="Método de Pago")
        # Ajustar el ancho de cada columna
        tree.column("Fecha", width=80)  # Ancho en píxeles
        tree.column("Nombre", width=100)
        tree.column("Apellido", width=100)
        tree.column("Monto", width=80, anchor="center")  # Centrar el texto
        tree.column("Método de Pago", width=120)
        tree.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")
        
# Crear un marco para los totales
        totales_frame = tk.Frame(balance_window)
        totales_frame.grid(row=4, column=2, pady=10, sticky="e")

        # Total en efectivo
        total_label_efectivo = tk.Label(totales_frame, text="Total en efectivo:", font=("Arial", 14, "bold"))
        total_label_efectivo.grid(row=0, column=0, sticky="w", padx=5)  # Alineado a la izquierda

        efectivo_value_label = tk.Label(totales_frame, text="$0.00", font=("Arial", 14), anchor="e")
        efectivo_value_label.grid(row=0, column=1, sticky="e", padx=5)  # Alineado a la derecha

        # Total en transferencia
        total_label_transferencia = tk.Label(totales_frame, text="Total en transferencia:", font=("Arial", 14, "bold"))
        total_label_transferencia.grid(row=1, column=0, sticky="w", padx=5)  # Alineado a la izquierda

        transferencia_value_label = tk.Label(totales_frame, text="$0.00", font=("Arial", 14), anchor="e")
        transferencia_value_label.grid(row=1, column=1, sticky="e", padx=5)  # Alineado a la derecha

        # Total abonado
        total_label_abonado = tk.Label(totales_frame, text="Total abonado:", font=("Arial", 14, "bold"))
        total_label_abonado.grid(row=2, column=0, sticky="w", padx=5)  # Alineado a la izquierda

        abonado_value_label = tk.Label(totales_frame, text="$0.00", font=("Arial", 14), anchor="e")
        abonado_value_label.grid(row=2, column=1, sticky="e", padx=5)  # Alineado a la derecha

        balance_window.update_idletasks()

    def mostrar_ventana_agregar(self, editar=False, nombre="", apellido="", dni="", categoria="", cuota_estado="",email="",ficha="", telefono="",tutor=""):
        if self.ventanaagregar is not False:
            return

        self.previous_window = self.master.focus_get()
        self.ventana = True
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

        # Campo Tutor (primero)
        tk.Label(main_frame, text="Tutor:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.tutor_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.tutor_entry.grid(row=0, column=1, padx=10, pady=5)
        self.tutor_entry.focus_set()
        # Campo Nombre
        tk.Label(main_frame, text="Nombre:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.nombre_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.nombre_entry.grid(row=1, column=1, padx=10, pady=5)

        # Campo Apellido
        tk.Label(main_frame, text="Apellido:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.apellido_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.apellido_entry.grid(row=2, column=1, padx=10, pady=5)

        # Campo DNI
        tk.Label(main_frame, text="DNI:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.dni_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.dni_entry.grid(row=3, column=1, padx=10, pady=5)

        # Campo Categoría
        tk.Label(main_frame, text="Categoría:", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)
        self.categoria_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.categoria_entry.grid(row=4, column=1, padx=10, pady=5)

        # Campo Email
        tk.Label(main_frame, text="Email:", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=5, sticky=tk.E)
        self.email_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.email_entry.grid(row=5, column=1, padx=10, pady=5)

        # Campo Teléfono
        tk.Label(main_frame, text="Teléfono:", font=("Arial", 14)).grid(row=6, column=0, padx=10, pady=5, sticky=tk.E)
        self.telefono_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.telefono_entry.grid(row=6, column=1, padx=10, pady=5)

        # Campo Cuota con Combobox
        tk.Label(main_frame, text="Cuota:", font=("Arial", 14)).grid(row=7, column=0, padx=10, pady=5, sticky=tk.E)
        self.cuota_estado = tk.StringVar(value="AL DÍA")
        self.cuota_menu = ttk.Combobox(main_frame, textvariable=self.cuota_estado, values=["AL DÍA", "MOROSO", "BECADO"], state="readonly", font=("Arial", 14))
        self.cuota_menu.grid(row=7, column=1, padx=10, pady=5)

        # Campo Ficha
        tk.Label(main_frame, text="Ficha:", font=("Arial", 14)).grid(row=8, column=0, padx=10, pady=5, sticky=tk.E)
        self.ficha_entry = tk.Entry(main_frame, font=("Arial", 14))
        self.ficha_entry.grid(row=8, column=1, padx=10, pady=5)

        # Frame para los botones (posición corregida)
        botones_frame = tk.Frame(main_frame)
        botones_frame.grid(row=9, column=0, columnspan=2, pady=15)  # Movido a la fila 9 para evitar superposición

        if editar:
            # Si estamos en modo edición, llenar los campos con los valores del alumno
            self.tutor_entry.delete(0, tk.END)
            self.tutor_entry.insert(0, tutor)
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, nombre)                        
            self.apellido_entry.delete(0, tk.END)
            self.apellido_entry.insert(0, apellido)
            self.dni_entry.delete(0, tk.END)
            self.dni_entry.insert(0, dni)
            self.categoria_entry.delete(0, tk.END)
            self.categoria_entry.insert(0, categoria)
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, email)
            self.telefono_entry.delete(0, tk.END)
            self.telefono_entry.insert(0, telefono)
            self.cuota_menu.set(cuota_estado)
            self.ficha_entry.delete(0,tk.END)
            self.ficha_entry.insert(0,ficha)
            
            

        if editar:
            guardar_button = tk.Button(botones_frame, text="Guardar", font=("Arial", 14), command=lambda: self.guardar_alumno_editado(dni))
            guardar_button.grid(row=0, column=0, padx=5)
            eliminar_button = tk.Button(botones_frame, text="Eliminar", font=("Arial", 14), command=lambda: self.eliminar_alumno(dni))
            eliminar_button.grid(row=0, column=1, padx=5)
        else:
            agregar_button = tk.Button(botones_frame, text="Agregar", font=("Arial", 14), command=self.agregar_alumno)
            agregar_button.grid(row=0, column=0, padx=5)

        # Centrar la ventana en la pantalla
        self.ventana_agregar.update_idletasks()
        width = self.ventana_agregar.winfo_width()
        height = self.ventana_agregar.winfo_height()
        x = (self.ventana_agregar.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana_agregar.winfo_screenheight() // 2) - (height // 2)
        self.ventana_agregar.geometry(f"{width}x{height}+{x}+{y-100}")

        return self.ventana_agregar


    def mostrar_ventana_cuota(self):
        if self.ventanacobrar is not False or self.ventanaAlumnos is True:
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
        
        ancho_ventana = 850
        alto_ventana = 650
        ventana_cobrar.geometry(f"{ancho_ventana}x{alto_ventana}")

        # Actualizar la ventana para que tome el tamaño definido
        ventana_cobrar.update_idletasks()

        # Obtener el tamaño de la pantalla
        ancho_pantalla = ventana_cobrar.winfo_screenwidth()
        alto_pantalla = ventana_cobrar.winfo_screenheight()

        # Calcular la posición centrada
        x_pos = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y_pos = (alto_pantalla // 2) - (alto_ventana // 2)

        # Aplicar la posición y tamaño calculado
        ventana_cobrar.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
        # Frame para la entrada y el botón de búsqueda
        input_frame = tk.Frame(ventana_cobrar)
        input_frame.pack(pady=5)

        # Etiqueta y entrada para el DNI
        label_dni = tk.Label(input_frame, text="Ingrese el DNI del alumno:", font=("Arial", 14))
        label_dni.pack(side=tk.LEFT, padx=5)
        self.entry_dni = tk.Entry(input_frame, font=("Arial", 14), width=20)
        self.entry_dni.pack(side=tk.LEFT, padx=5)
        self.entry_dni.bind("<Return>", lambda event: self.buscar_alumno_cuota())

        # Botón para buscar el alumno
        buscar_button = tk.Button(input_frame, image=self.buscar_icono, font=("Arial", 14), command=self.buscar_alumno_cuota)
        buscar_button.pack(side=tk.LEFT, padx=5)

        # Etiqueta para mostrar nombre y apellido
        self.label_nombre_apellido = tk.Label(ventana_cobrar, text="", font=("Arial", 14))
        self.label_nombre_apellido.pack(pady=2, anchor="center")

        # Frame para mostrar historial de pagos
        self.historial_frame = tk.Frame(ventana_cobrar)
        self.historial_frame.pack(pady=1)
        # Contenedor horizontal para la etiqueta y el botón
        self.encabezado_frame = tk.Frame(self.historial_frame)
        self.encabezado_frame.pack(fill="x", pady=1, padx=10)

        # Etiqueta de historial de pagos
        self.label_historial = tk.Label(self.encabezado_frame, text="Historial de Pagos:", font=("Arial", 14))
        self.label_historial.pack(side="left")

        # Icono y botón eliminar
        icono_original = Image.open(self.resource_path("images/delete.png"))
        icono_redimensionado = icono_original.resize((20, 20))  # Ajustá el tamaño a gusto
        self.delete_icon = ImageTk.PhotoImage(icono_redimensionado)

        boton_eliminar_pago = tk.Button(
            self.encabezado_frame,
            image=self.delete_icon,
            command=self.eliminar_pago_seleccionado,
            bd=0,
            width=20,
            height=20
        )
        boton_eliminar_pago.pack(side="right", padx=5)

        # Crear Treeview para mostrar historial de pagos
        self.tree = ttk.Treeview(self.historial_frame, columns=('DNI', 'Nombre', 'Apellido', 'Categoría', 'Fecha','Hora', 'Monto', 'Método de Pago'), show='headings')

        # Configurar columnas
        self.tree.column('DNI', anchor=tk.CENTER, width=100)
        self.tree.column('Nombre', anchor=tk.W, width=150)
        self.tree.column('Apellido', anchor=tk.W, width=150)
        self.tree.column('Categoría', anchor=tk.CENTER, width=100)
        self.tree.column('Fecha', anchor=tk.CENTER, width=100)
        self.tree.column('Hora', anchor=tk.CENTER, width=50)
        self.tree.column('Monto', anchor=tk.CENTER, width=50)
        self.tree.column('Método de Pago', anchor=tk.W, width=100)

        # Configurar encabezados
        self.tree.heading('DNI', text='DNI', anchor=tk.CENTER)
        self.tree.heading('Nombre', text='Nombre', anchor=tk.W)
        self.tree.heading('Apellido', text='Apellido', anchor=tk.W)
        self.tree.heading('Categoría', text='Categoría', anchor=tk.CENTER)
        self.tree.heading('Fecha', text='Fecha', anchor=tk.CENTER)
        self.tree.heading('Hora', text='Hora', anchor=tk.CENTER)
        self.tree.heading('Monto', text='Monto', anchor=tk.CENTER)
        self.tree.heading('Método de Pago', text='Método de Pago', anchor=tk.W)

        # Empacar el Treeview
        self.tree.pack(pady=10, fill='both', expand=True)

        # Insertar ejemplo de datos, reemplázalo con datos reales
        self.tree.pack(pady=5)

        # Mostrar métodos de pago, monto, recargo y total a pagar
        pago_frame = tk.Frame(ventana_cobrar)
        pago_frame.pack(pady=10, fill="both")

        # Sub-frame centrado
        formulario_frame = tk.Frame(pago_frame)
        formulario_frame.pack(anchor="center")  # Centra el formulario en el frame principal

        formulario_frame.columnconfigure(1, weight=1)  # Columna 1 se expande si es necesario

        # Método de pago
        tk.Label(formulario_frame, text="Método de pago:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.var_pago = tk.StringVar()
        self.combo_pago = ttk.Combobox(formulario_frame, textvariable=self.var_pago, values=["Efectivo", "Transferencia"], font=("Arial", 14), state="readonly", width=20)
        self.combo_pago.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_pago.set("Efectivo")
        self.combo_pago.bind("<<ComboboxSelected>>", lambda e: self.calcular_monto_pago())

        # Mes a pagar
        tk.Label(formulario_frame, text="Mes a pagar:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.mes_a_pagar = tk.StringVar()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_mes = ttk.Combobox(formulario_frame, textvariable=self.mes_a_pagar, values=meses, font=("Arial", 14), state="readonly", width=20)
        self.combo_mes.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.combo_mes.set(self.obtener_mes_actual())

        # Fecha de pago
        tk.Label(formulario_frame, text="Fecha de pago (dd/mm):", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        fecha_actual = tk.StringVar()
        fecha_actual.set(self.obtener_fecha_actual())
        self.entry_fecha_pago = tk.Entry(formulario_frame, textvariable=fecha_actual, font=("Arial", 14), width=10)
        self.entry_fecha_pago.grid(row=2, column=1, padx=(5, 0), pady=5, sticky="w")
        self.entry_fecha_pago.bind("<FocusOut>", self.calcular_monto_pago)

        calendario_button = tk.Button(formulario_frame, image=self.calendario_icono, command=lambda: self.mostrar_calendario(self.entry_fecha_pago, self.calcular_monto_pago))
        calendario_button.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Monto
        tk.Label(formulario_frame, text="Monto de Cuota: $", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_monto = tk.Entry(formulario_frame, font=("Arial", 14), width=20)
        self.entry_monto.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.entry_monto.bind("<KeyRelease>", self.calcular_monto_pago)

        # Recargo
        tk.Label(formulario_frame, text="Recargo: $", font=("Arial", 14)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.label_recargo = tk.Label(formulario_frame, text="0.0", font=("Arial", 14))
        self.label_recargo.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Total
        tk.Label(formulario_frame, text="Total a Pagar: $", font=("Arial", 14)).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.label_total = tk.Label(formulario_frame, text="0.00", font=("Arial", 14))
        self.label_total.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Botón registrar centrado
        tk.Button(formulario_frame, text="Registrar Pago", font=("Arial", 14), command=self.registrar_pago)\
            .grid(row=6, column=0, columnspan=3, pady=15, padx=20, sticky="ew")


    def mostrar_factura(self, event):
        # Obtener el item seleccionado del Treeview
        item = self.tree.selection()
        if not item:
            return  # Si no se selecciona ninguna fila, no hacemos nada

        # Obtener los valores de la fila seleccionada
        alumno_nombre = self.tree.item(item, 'values')[1]  # Nombre del alumno (segunda columna)
        print(self.tree.item(item, 'values'))
        alumno_apellido = self.tree.item(item, 'values')[2]  # Apellido del alumno (segunda columna, asumiendo que apellido está en la misma columna, puedes ajustarlo)
        fecha_pago = self.tree.item(item, 'values')[4]  # Fecha de pago (cuarta columna)
        
        # Convertir la fecha en formato "DD-MM-YYYY"
        fecha_formateada = fecha_pago.replace("/", "-")  # Asegurarse que la fecha esté en formato DD-MM-YYYY
        hora_pago = self.tree.item(item, 'values')[5]  # Obtener la hora desde el índice 5
        hora_formateada = datetime.strptime(hora_pago, "%H:%M:%S").strftime("%H-%M-%S")


        # Crear el nombre base del archivo PDF a partir del nombre y apellido del alumno y la fecha
        nombre_base = f"recibo_pago_{alumno_nombre} {alumno_apellido}-{fecha_formateada}_{hora_formateada}"
        print(nombre_base)
        
        # Directorio de los comprobantes
        carpeta_comprobantes = "comprobantes"  # Asegúrate de que esta carpeta esté en la misma ubicación que tu script o cambia la ruta

        # Buscar el archivo en la carpeta
        archivos_en_carpeta = os.listdir(carpeta_comprobantes)
        archivo_comprobante = None

        # Buscar el archivo que coincida con el nombre base y la fecha
        for archivo in archivos_en_carpeta:
            if archivo.startswith(nombre_base) and archivo.endswith(".pdf"):
                archivo_comprobante = archivo
                break

        # Si encontramos el archivo, lo abrimos
        if archivo_comprobante:
            ruta_comprobante = os.path.join(carpeta_comprobantes, archivo_comprobante)
            # Usamos webbrowser para abrir el PDF en el navegador predeterminado
            webbrowser.open(ruta_comprobante)
        else:
            print(f"No se encontró el archivo para {alumno_nombre} {alumno_apellido} con la fecha {fecha_formateada}")
    

    def mostrar_calendario(self, entry_widget,callback=None):
        # Crear la ventana emergente
        calendario_popup = tk.Toplevel(self.master)
        calendario_popup.title("Seleccionar Fecha")

        # Calcular la posición para centrar la ventana en la pantalla
        screen_width = calendario_popup.winfo_screenwidth()
        screen_height = calendario_popup.winfo_screenheight()
        window_width = 300  # Ajusta el ancho para que la ventana sea más pequeña
        window_height = 250  # Ajusta la altura para que la ventana sea más pequeña

        # Calcular la posición X y Y para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        calendario_popup.geometry(f"{window_width}x{window_height}+{x}+{y}")  # Configurar la geometría

        # Calendario
        calendario = Calendar(calendario_popup, selectmode='day', date_pattern='dd/mm/yyyy')
        calendario.pack(padx=10, pady=10)

        # Función para actualizar la fecha en el entry
        def seleccionar_fecha():
            fecha_seleccionada = calendario.get_date()
            entry_widget.delete(0, tk.END)  # Limpiar el campo de entrada
            entry_widget.insert(0, fecha_seleccionada)  # Insertar la fecha seleccionada
            calendario_popup.destroy()  # Cerrar el calendario
            if callback:
                callback()

        
            
        
        # Botón para seleccionar la fecha
        seleccionar_button = tk.Button(calendario_popup, text="Seleccionar Fecha", command=seleccionar_fecha)
        seleccionar_button.pack(pady=10)

        
    def obtener_mes_actual(self):
        import datetime
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_actual = datetime.datetime.now().month
        return meses[mes_actual - 1]

     

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
        self.limpiar_treeview()

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
                alumno["apellido"],  # Agregar apellido aquí
                alumno["categoria"], 
                pago["fecha"], 
                pago["hora"],
                pago["monto"], 
                pago["metodo_pago"]  # Se agrega el método de pago
            ))
    
    def limpiar_treeview(self):
        """Función auxiliar para limpiar el Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def calcular_monto_pago(self, event=None):
        """Calcula el recargo y actualiza el total cuando se ingresa la fecha de pago."""
        fecha_pago = self.entry_fecha_pago.get()
        print("ffddsaadaaadsada")

        if fecha_pago:
            try:
                dia_pago = int(fecha_pago.split("/")[0])  # Obtener solo el día
                print(dia_pago)
                if dia_pago > 10 and dia_pago<17:
                    monto_mora = 1000  # Recargo de $1000 por semana de retraso
                elif dia_pago > 16 and dia_pago<24:
                    monto_mora = 2000 
                elif dia_pago > 23 and dia_pago<32:
                    monto_mora = 3000
                else:
                    monto_mora  = 0
            except ValueError:
                monto_mora = 0  # Si la fecha no es válida, no aplicar recargo
        else:
            monto_mora = 0


        
        try:
            self.cuota_base = float(self.entry_monto.get())
        except ValueError:
            self.label_total.config(text="Monto inválido")
            return

        # Calcular el monto total
        monto_transfe = 0
        
        
        if self.var_pago.get() == "Transferencia":
            monto_transfe = 1000
            print(monto_mora)
        else:
            monto_transfe = 0
        monto_total = self.cuota_base + monto_mora + monto_transfe
        print("total ", monto_total)

        # Actualizar los valores en la interfaz
        self.label_recargo.config(text=f"{monto_mora+monto_transfe:.2f}")
        self.label_total.config(text=f"{monto_total:.2f}")

        # Guardar el monto total en la variable de la clase
        self.monto_a_pagar = monto_total
        
    def registrar_pago(self):
        dni = self.entry_dni.get()
        metodo_pago = self.var_pago.get()
        fecha_pago = self.entry_fecha_pago.get()
        hora_pago = datetime.now().strftime("%H:%M:%S")
        mes_a_pagar = self.mes_a_pagar.get()  # 🔹 Captura el mes seleccionado

        if not hasattr(self, 'monto_a_pagar') or not isinstance(self.monto_a_pagar, (int, float)) or self.monto_a_pagar <= 0:
            print("❌ No se puede registrar el pago: monto inválido.")
            self.label_total.config(text="Monto inválido")
            return

        # Obtener los detalles del alumno
        nombre = self.alumno_encontrado['nombre']
        apellido = self.alumno_encontrado['apellido']
        tutor = self.alumno_encontrado['tutor']
        completo = f"{nombre} {apellido}"
        email_to = self.alumno_encontrado['email']
        print(email_to)

        # Registrar el pago en el historial con el mes a pagar incluido
        self.registrar_pago_en_historial(
            dni,
            nombre,
            apellido,
            self.alumno_encontrado['categoria'],
            fecha_pago,
            hora_pago,
            self.monto_a_pagar,
            metodo_pago,
            email_to,
            mes_a_pagar  # 🔹 Incluido
        )

        # Enviar el comprobante si el alumno tiene correo registrado
        if email_to:
            file = generar_recibo_profesional(completo, self.monto_a_pagar, metodo_pago, hora_pago, fecha_pago, mes_a_pagar)  # 🔹 Podés agregar mes al recibo si tu función lo soporta
            enviar_comprobante(email_to, nombre, self.monto_a_pagar, metodo_pago, file, tutor, mes_a_pagar)
        else:
            print(f"⚠ No se pudo enviar comprobante: {nombre} no tiene correo registrado.")

        # Cerrar la ventana después de registrar el pago
        self.venta_finalizada = True
        self.ventanacobrar = False
        print(f"Pago de ${self.monto_a_pagar} registrado para {nombre} ({dni}), mes: {mes_a_pagar}.")
        self.actualizar_estado_cuota()

        
    def registrar_pago_en_historial(self, dni, nombre, apellido, categoria, fecha_pago,hora_pago, monto, metodo_pago, email,mes_a_pagar):
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
                "apellido": apellido,  # Agregar el apellido
                "categoria": categoria,
                "pagos": []
            }

        # Agregar el nuevo pago al historial del alumno
        historial_general[dni]["pagos"].append({
            "fecha": fecha_pago,
            "hora": hora_pago,
            "monto": monto,
            "metodo_pago": metodo_pago,
            "email": email,
            "mes_pagado": mes_a_pagar
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
        if self.ventanaAlumnos is not False or self.ventanacobrar is not False:
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
        buscar_button = tk.Button(search_frame, image=self.buscar_icono, font=("Arial", 14), command=self.buscar_alumno)
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

        # Diccionario para controlar el estado de ordenamiento
        self.orden_actual = {}

        # Función para ordenar la tabla al hacer clic en los encabezados
        def ordenar_por_columna(columna):
            orden = self.orden_actual.get(columna, "asc")

            # Obtener los datos actuales
            datos = [(self.tree.set(item, columna), item) for item in self.tree.get_children("")]
            
            # Intentar convertir a número si es posible
            try:
                datos.sort(key=lambda x: int(x[0]), reverse=(orden == "desc"))
            except ValueError:
                datos.sort(key=lambda x: x[0], reverse=(orden == "desc"))

            # Alternar el orden para la próxima vez
            self.orden_actual[columna] = "desc" if orden == "asc" else "asc"

            # Reordenar los elementos en el Treeview
            for index, (val, item) in enumerate(datos):
                self.tree.move(item, "", index)

        # Definir los encabezados con opción de ordenar
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('DNI', text='DNI', anchor=tk.CENTER, command=lambda: ordenar_por_columna('DNI'))
        self.tree.heading('Nombre', text='Nombre', anchor=tk.W, command=lambda: ordenar_por_columna('Nombre'))
        self.tree.heading('Apellido', text='Apellido', anchor=tk.W, command=lambda: ordenar_por_columna('Apellido'))
        self.tree.heading('Categoría', text='Categoría', anchor=tk.CENTER, command=lambda: ordenar_por_columna('Categoría'))
        self.tree.heading('Cuota', text='Cuota', anchor=tk.CENTER, command=lambda: ordenar_por_columna('Cuota'))

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
        tutor = self.tutor_entry.get()  # Obtener el valor del campo Tutor
        nombre = self.nombre_entry.get()  # Obtener el valor del campo Nombre
        apellido = self.apellido_entry.get()  # Obtener el valor del campo Apellido
        dni = self.dni_entry.get()  # Obtener el valor del campo DNI
        categoria = self.categoria_entry.get()  # Obtener el valor del campo Categoría
        cuota_estado = self.cuota_estado.get()  # Obtener el valor del campo Cuota
        email = self.email_entry.get() or "None"  # Si el email está vacío, se coloca "None"
        telefono = self.telefono_entry.get() 
        ficha = self.ficha_entry.get()  # Obtener el valor del campo Ficha


        # Validaciones generales
        if not nombre or not apellido or not dni or not categoria or not cuota_estado:
            messagebox.showerror("Error", "Todos los campos excepto el email son obligatorios.")
            return

        # Validar que la categoría sea un año válido o un texto como "Escuelita"
        try:
            current_year = datetime.now().year
            if categoria.isdigit():
                categoria_int = int(categoria)
                if categoria_int < 1900 or categoria_int > current_year:
                    raise ValueError("El año de nacimiento debe estar entre 1900 y el año actual.")
                # Si es un número válido, lo seguimos usando como string para uniformidad
                categoria = str(categoria_int)
            else:
                # Podrías agregar más validaciones si querés limitar qué textos son válidos
                categoria = categoria.strip().title()  # Ej: "escuelita" -> "Escuelita"
        except Exception as e:
            messagebox.showerror("Error", f"Categoría inválida: {str(e)}")
            return



        if agregar_alumno(dni,nombre,apellido,categoria,cuota_estado,email,tutor,ficha,telefono):

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


    def scroll_text(self, *args):
        """Desplaza automáticamente el texto hacia abajo."""
        self.output_text_cobrar.yview(tk.END)
            

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
            print(alumno)

            if alumno:
                # Mostrar ventana similar a agregar alumno pero con datos del alumno seleccionado
                self.editando_alumno = True
                self.mostrar_ventana_agregar(
                    editar=True, 
                    dni=alumno["dni"], 
                    nombre=alumno["nombre"], 
                    apellido=alumno["apellido"], 
                    categoria=alumno["categoria"], 
                    cuota_estado=alumno["cuota_estado"],
                    email=alumno["email"],
                    ficha=alumno["ficha"],
                    telefono=alumno["telefono"],
                    tutor=alumno["tutor"]
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
        tutor = self.tutor_entry.get()  # Obtener el valor del campo Tutor
        nombre = self.nombre_entry.get()  # Obtener el valor del campo Nombre
        apellido = self.apellido_entry.get()  # Obtener el valor del campo Apellido
        dni_nuevo = self.dni_entry.get()  # Obtener el valor del campo DNI
        categoria = self.categoria_entry.get()  # Obtener el valor del campo Categoría
        cuota_estado = self.cuota_estado.get()  # Obtener el valor del campo Cuota
        email = self.email_entry.get() or "None"  # Si el email está vacío, se coloca "None"
        telefono = self.telefono_entry.get() 
        ficha = self.ficha_entry.get()  # Obtener el valor del campo Ficha
        self.actualizar_datos_historial_pago(dni, dni_nuevo, nombre, apellido, categoria)

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
        if modificar_alumno(dni, nombre, apellido, categoria, cuota_estado, dni_nuevo, email,ficha, telefono, tutor):
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
        alumnos_path = 'alumnos.json'
        historial_path = 'historial_pagos.json'

        # Cargar los archivos JSON
        with open(alumnos_path, 'r', encoding='utf-8') as f:
            alumnos = json.load(f)

        # Verificar si el archivo historial_pagos.json existe
        if os.path.exists(historial_path):
            with open(historial_path, 'r', encoding='utf-8') as f:
                historial_pagos = json.load(f)
        else:
            historial_pagos = {}  # Si no existe, inicializamos un diccionario vacío

        # Fecha actual
        fecha_actual = datetime.now()

        for alumno in alumnos:
            dni = alumno["dni"]

            # Si el alumno está becado, no hacemos ningún cambio
            if alumno.get("cuota_estado") == "BECADO":
                continue

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

        # Guardar los cambios en el archivo alumnos.json
        with open(alumnos_path, 'w', encoding='utf-8') as f:
            json.dump(alumnos, f, indent=4, ensure_ascii=False)


    def actualizar_datos_historial_pago(self, dni_original, nuevo_dni, nuevo_nombre, nuevo_apellido, nueva_categoria):
        try:
            with open("historial_pagos.json", "r", encoding="utf-8") as f:
                historial = json.load(f)

            if dni_original in historial:
                datos_actuales = historial[dni_original]
                
                # Actualizar campos
                datos_actuales["dni"] = nuevo_dni
                datos_actuales["nombre"] = nuevo_nombre
                datos_actuales["apellido"] = nuevo_apellido
                datos_actuales["categoria"] = nueva_categoria

                # Si el DNI cambió, mover la entrada al nuevo DNI
                if dni_original != nuevo_dni:
                    historial[nuevo_dni] = datos_actuales
                    del historial[dni_original]
                else:
                    historial[dni_original] = datos_actuales

                with open("historial_pagos.json", "w", encoding="utf-8") as f:
                    json.dump(historial, f, indent=4, ensure_ascii=False)
                    
              
            else:
                messagebox.showwarning("Advertencia", "No se encontró el historial para el DNI especificado para editar el historial de pago, seguramente es aun no realizo su primer pago, no te preocupes.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el historial de pagos: {str(e)}")


    def eliminar_pago_seleccionado(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un pago para eliminar.")
            return

        datos = self.tree.item(seleccionado[0], 'values')
        dni, nombre, apellido, categoria, fecha, hora, monto, metodo = datos

        confirmacion = messagebox.askyesno("Confirmar", f"¿Deseas eliminar el pago del {fecha} a las {hora} por ${monto}?")
        if not confirmacion:
            return

        # Eliminar del JSON
        try:
            with open("historial_pagos.json", "r", encoding="utf-8") as f:
                historial = json.load(f)

            if dni in historial:
                pagos = historial[dni]["pagos"]
                pagos_filtrados = [p for p in pagos if not (p["fecha"] == fecha and p["hora"] == hora and p["monto"] == float(monto) and p["metodo_pago"] == metodo)]
                historial[dni]["pagos"] = pagos_filtrados

                with open("historial_pagos.json", "w", encoding="utf-8") as f:
                    json.dump(historial, f, indent=4, ensure_ascii=False)

            # Construir nombre de archivo PDF
            nombre_completo = nombre+" "+apellido
            fecha_formato = fecha.replace("/", "-")
            hora_formato = hora.replace(":", "-")
            nombre_archivo = f"recibo_pago_{nombre_completo}-{fecha_formato}_{hora_formato}.pdf"
            ruta_archivo = os.path.join("comprobantes", nombre_archivo)

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
                print("Comprobante eliminado:", ruta_archivo)
            else:
                print("No se encontró el comprobante:", ruta_archivo)

            self.tree.delete(seleccionado[0])
            messagebox.showinfo("Éxito", "Pago eliminado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el pago: {str(e)}")


# Crear la ventana principal de la aplicación
root = tk.Tk()
app = InventarioApp(root)
root.mainloop()
