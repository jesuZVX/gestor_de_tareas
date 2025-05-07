import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.exc import IntegrityError
from backend.database import SessionLocal, Usuario, RolUsuario
from passlib.hash import bcrypt

# Configuración SMTP
USE_LOCAL_SMTP = False
if USE_LOCAL_SMTP:
    SMTP_SERVER   = "localhost"
    SMTP_PORT     = 1025
    SMTP_USER     = None
    SMTP_PASSWORD = None
    EMAIL_SENDER  = "test@local"
else:
    SMTP_SERVER   = "smtp.gmail.com"
    SMTP_PORT     = 587
    SMTP_USER     = "senaproyecto980@gmail.com"  
    SMTP_PASSWORD = "riqf khmk inyc hdxa"         
    EMAIL_SENDER  = SMTP_USER



def enviar_correo(destinatario, asunto, mensaje):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if not USE_LOCAL_SMTP:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print(f"✅ Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

def enviar_correo_asignacion(destinatario, nombre_usuario, nombre_tarea, nombre_proyecto):
    asunto = "Nueva tarea asignada en el Gestor de Tareas"
    mensaje = (
        f"Hola {nombre_usuario},\n\n"
        f"Se te ha asignado una nueva tarea:\n"
        f"📌 Tarea: {nombre_tarea}\n"
        f"📁 Proyecto: {nombre_proyecto}\n\n"
        "Por favor, ingresa al sistema para revisar los detalles.\n\n"
        "Saludos,\nGestor de Tareas"
    )
    return enviar_correo(destinatario, asunto, mensaje)


def crear_usuario(nombre, nombre_usuario, documento, correo, contraseña, rol="colaborador"):
    db = SessionLocal()
    try:
        hashed_pw = bcrypt.hash(contraseña)
        nuevo = Usuario(
            nombre=nombre,
            nombre_usuario=nombre_usuario,
            documento=documento,
            correo=correo,
            contraseña=hashed_pw,
            rol=RolUsuario(rol)
        )
        db.add(nuevo)
        db.commit()
        return True, "Usuario registrado exitosamente."
    except IntegrityError as e:
        db.rollback()
        err = str(e.orig).lower()
        if "uq_usuario_correo" in err:
            return False, "El correo ya está registrado."
        if "uq_usuario_username" in err:
            return False, "El nombre de usuario ya existe."
        if "uq_usuario_documento" in err:
            return False, "El documento ya está registrado."
        return False, "Error al crear usuario: datos duplicados."
    except Exception as e:
        db.rollback()
        return False, f"Error inesperado: {e}"
    finally:
        db.close()

def verificar_login(correo: str, contraseña: str):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == correo, Usuario.activo == 1).first()
        if usuario and bcrypt.verify(contraseña, usuario.contraseña):
            return True, usuario
        return False, None
    except Exception:
        return False, None
    finally:
        db.close()

def resetear_contraseña(correo: str, nueva_contraseña: str):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
        if not usuario:
            return False, "No existe ninguna cuenta con ese correo."

        usuario.contraseña = bcrypt.hash(nueva_contraseña)
        db.commit()
        return True, "Contraseña actualizada exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar la contraseña: {e}"
    finally:
        db.close()
