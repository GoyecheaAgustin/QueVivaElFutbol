import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

def enviar_comprobante(email_to, alumno, monto, fecha, metodo_pago):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_user = "quevivaelfutbolescuela@gmail.com"
    email_password = "nifk zxuu extq xejb"
    email_to = email_to
        # Crear el mensaje
    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = email_to
    msg["Subject"] = f"Comprobante de Pago - {alumno}"

    # Cuerpo del mensaje
    body = f"""
    Estimado/a {alumno},

    Le informamos que hemos registrado su pago con los siguientes detalles:

    📌 **Comprobante de Pago**
    --------------------------------
    💰 Monto: {monto}
    📅 Fecha: {fecha}
    💳 Método de Pago: {metodo_pago}
    ✅ Estado: Pagado

    Gracias por su confianza.

    ¡Que viva el fútbol!
    """
    msg.attach(MIMEText(body, "plain"))

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, email_to, msg.as_string())
        server.quit()
        print(f"✅ Comprobante enviado a {email_to}")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
