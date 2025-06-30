import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def enviar_notificacion_lider(destinatario, asunto, mensaje, archivo_adjunto=None):
    """
    Envía un correo electrónico al líder usando Gmail SMTP.
    destinatario: email del líder
    asunto: asunto del correo
    mensaje: cuerpo del correo (HTML permitido)
    archivo_adjunto: ruta al archivo a adjuntar (opcional)
    """
    # Configuración (usar variables de entorno para seguridad)
    GMAIL_USER = os.environ.get('GMAIL_USER', 'tucorreo@gmail.com')
    GMAIL_PASS = os.environ.get('GMAIL_PASS', 'tu_contraseña_app')
    
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'html'))

    # Adjuntar archivo si se proporciona
    if archivo_adjunto:
        try:
            with open(archivo_adjunto, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(archivo_adjunto)}"')
            msg.attach(part)
        except Exception as e:
            print(f"Error adjuntando archivo: {e}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        print(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
