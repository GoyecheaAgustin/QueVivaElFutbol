import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication  # Necesario para adjuntar el PDF
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def enviar_comprobante(email_to, alumno, monto, metodo_pago, pdf_path,tutor,mes_a_pagar):
    # Configuración del servidor SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_user = "quevivaelfutbolescuela@gmail.com"
    email_password = "nifk zxuu extq xejb"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg["From"] = email_user
    print(email_to.lower())
    msg["To"] = email_to.lower()
    msg["Subject"] = f"Comprobante de Pago - {alumno}"

    # Obtener la fecha y hora actual
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Cuerpo del mensaje
    body = f"""
    Estimado/a {tutor},  

    Primero, esperamos que este mensaje le encuentre bien.  

    Segundo, Francia.

    Tercero, le confirmamos que hemos registrado correctamente su pago con los siguientes detalles:  

    📌 Detalles del Pago
    --------------------------------  
    💰 Monto: {monto} Pesos  
    🕓 Fecha y Hora: {fecha_hora}  
    📅 Mes Abonado: {mes_a_pagar}
    💳 Método de Pago: {metodo_pago} 
    ✅ Estado: Pagado  

    Agradecemos su puntualidad y confianza en nuestra institución. Si tiene alguna consulta, no dude en comunicarse con nosotros.  

    Atentamente,  

    ⚽ ¡Que viva el fútbol! ⚽
    """  

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(body, "plain"))

    # Adjuntar el comprobante PDF
    with open(pdf_path, "rb") as archivo_pdf:
        adjunto = MIMEApplication(archivo_pdf.read(), _subtype="pdf")
        adjunto.add_header('Content-Disposition', 'attachment', filename="comprobante_pago.pdf")
        msg.attach(adjunto)

    # Enviar el correo
    try:
        # Establecer la conexión con el servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Establecer la conexión segura
        server.login(email_user, email_password)
        server.sendmail(email_user, email_to, msg.as_string())
        server.quit()  # Cerrar la conexión
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", f"✅ Comprobante enviado a {email_to}")
    except Exception as e:
        # Mostrar mensaje de error
        messagebox.showerror("Error pero no es tan malo", f"❌ Se registro el pago pero no se pudo enviar el correo, seguramente este mal escrito o no exista")