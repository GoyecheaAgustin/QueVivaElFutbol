from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os
# Función para generar el PDF del recibo profesional
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generar_recibo_profesional(alumno, monto, metodo_pago,hora, fecha, mes_a_pagar ):
    carpeta_destino = "comprobantes"  # Nombre de la carpeta donde se guardará el PDF
    if not os.path.exists(carpeta_destino):  # Si la carpeta no existe, la creamos
        os.makedirs(carpeta_destino)
    

    fecha_str = fecha+" "+hora
    # Parsear el string a objeto datetime
    fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")

    # Definir el nombre del archivo con la ruta completa
    fecha_hora = fecha_dt.strftime("%d-%m-%Y_%H-%M-%S")  # Evitar caracteres invalidos como ':'
    fecha_hora1 = fecha_dt.strftime("%d/%m/%Y %H:%M:%S") 
    pdf_filename = os.path.join(carpeta_destino, f"recibo_pago_{alumno}-{fecha_hora}.pdf")

    logo_path = "logo.png"
    
    # Crear el PDF con una página de tamaño ajustado para que el borde negro ocupe toda la página
    c = canvas.Canvas(pdf_filename, pagesize=(420, 595))  # Ajustamos la página a las dimensiones del recuadro
    c.setFont("Helvetica", 10)

    # Fondo blanco
    c.setFillColor(colors.white)
    c.rect(0, 0, 420, 595, fill=1)  # Fondo blanco

    # Recuadro negro en todo el borde de la página
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.rect(0, 0, 420, 595)  # Recuadro negro que ocupa toda la página

    # Encabezado limpio con el nombre de la escuela
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawString(50, 560, "Comprobante de Pago")

    # Logo centrado en la parte inferior
    logo_width, logo_height = 120, 60  # Tamaño del logo
    c.drawImage(logo_path, 150, 40, width=logo_width, height=logo_height, preserveAspectRatio=True)

    # Título del comprobante
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawString(50, 520, "Detalles")

    # Detalles de la transacción
    c.setFont("Helvetica", 10)
    c.drawString(50, 480, f"Alumno: {alumno}")
    c.drawString(50, 465, f"Mes pagado: {mes_a_pagar}")  # 👈 Línea agregada
    c.drawString(50, 445, f"Monto: {monto} Pesos")
    c.drawString(50, 425, f"Fecha y Hora de Pago: {fecha_hora1}")
    c.drawString(50, 405, f"Método de Pago: {metodo_pago}")


    # Línea separadora
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, 400, 370, 400)

    # Resumen del pago
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(50, 370, "¡Gracias por su pago!")
    c.setFont("Helvetica", 10)
    c.drawString(50, 350, "Nos vemos en el próximo entrenamiento - ¡Que Viva El Futbol!")

    # Información adicional de contacto
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(50, 330, "Para más información, contáctenos en:")
    c.drawString(50, 310, "Correo: quevivaelfutbolescuela@gmail.com")
    c.drawString(50, 290, "Teléfono: 3764 187861 [Profe Beto]")

    # Guardar el PDF
    c.save()

    print(f"Comprobante PDF generado: {pdf_filename}")

    return pdf_filename
