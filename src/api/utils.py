from flask import url_for
import os
from email.mime.text import MIMEText                
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from api.models import db, User

class APIException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def generate_sitemap(app):
    links = ['/admin/']
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            if "/admin/" not in url:
                links.append(url)

    links_html = "".join(["<li><a href='" + y + "'>" + y + "</a></li>" for y in links])
    return """
        <div style="text-align: center;">
        <img style="max-height: 80px" src='https://storage.googleapis.com/breathecode/boilerplates/rigo-baby.jpeg' />
        <h1>Rigo welcomes you to your API!!</h1>
        <p>API HOST: <script>document.write('<input style="padding: 5px; width: 300px" type="text" value="'+window.location.href+'" />');</script></p>
        <p>Start working on your project by following the <a href="https://start.4geeksacademy.com/starters/full-stack" target="_blank">Quick Start</a></p>
        <p>Remember to specify a real endpoint path like: </p>
        <ul style="text-align: left;">"""+links_html+"</ul></div>"


# Codigo extra para mandar mensaje.

def send_email(subject, to, body_message):

    # Defino credenciales:
    smtp_address = os.getenv("SMTP_ADDRESS")
    smtp_port = os.getenv("SMTP_PORT")
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")   

    message = MIMEMultipart("alternative")
    message["Subject"] = subject                            
    message["From"] = "correo.electronico@gmail.com"        
    message["To"] = to                                      

    html = """
        <html>
            <body>
                """+ body_message + """
            </body>
        </html>
    """

    html_mime = MIMEText(html, "html")          

    message.attach(html_mime)                   

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context = context) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, to, message.as_string())     
            return True
    except Exception as error:
        print(str(error))
        return False


# ============ FUNCIONES DE ADMINISTRACIÓN DE USUARIOS ============

def make_user_admin(email):
    """
    Convierte un usuario en administrador
    
    Args:
        email (str): Email del usuario a convertir en admin
        
    Returns:
        dict: Resultado de la operación con status y mensaje
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return {
            "success": False,
            "message": f"Usuario con email '{email}' no encontrado"
        }
    
    if user.is_admin == 'admin':
        return {
            "success": True,
            "message": f"El usuario '{email}' ya es administrador"
        }
    
    # Cambiar a admin
    user.is_admin = 'admin'
    
    try:
        db.session.commit()
        return {
            "success": True,
            "message": f"Usuario '{email}' convertido a administrador exitosamente"
        }
    except Exception as error:
        db.session.rollback()
        return {
            "success": False,
            "message": f"Error al actualizar usuario: {error.args}"
        }

def remove_admin_privileges(email):
    """
    Quita privilegios de administrador a un usuario
    
    Args:
        email (str): Email del usuario
        
    Returns:
        dict: Resultado de la operación
    """
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return {
            "success": False,
            "message": f"Usuario con email '{email}' no encontrado"
        }
    
    if user.is_admin == 'user':
        return {
            "success": True,
            "message": f"El usuario '{email}' ya es usuario regular"
        }
    
    # Cambiar a user
    user.is_admin = 'user'
    
    try:
        db.session.commit()
        return {
            "success": True,
            "message": f"Privilegios de admin removidos para '{email}'"
        }
    except Exception as error:
        db.session.rollback()
        return {
            "success": False,
            "message": f"Error al actualizar usuario: {error.args}"
        }

def list_all_users():
    """
    Lista todos los usuarios con su rol
    
    Returns:
        list: Lista de usuarios con su información básica
    """
    users = User.query.all()
    
    return [{
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "role_display": "Administrador" if user.is_admin == 'admin' else "Usuario"
    } for user in users]

def is_user_admin(email):
    """
    Verifica si un usuario es administrador por email
    
    Args:
        email (str): Email del usuario
        
    Returns:
        bool: True si es admin, False si no
    """
    user = User.query.filter_by(email=email).first()
    return user and user.is_admin == 'admin'

def is_user_admin_by_id(user_id):
    """
    Verifica si un usuario es administrador por ID
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        bool: True si es admin, False si no
    """
    user = User.query.get(user_id)
    return user and user.is_admin == 'admin'

def get_admin_users():
    """
    Obtiene todos los usuarios administradores
    
    Returns:
        list: Lista de usuarios administradores
    """
    admins = User.query.filter_by(is_admin='admin').all()
    
    return [{
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
        "role_display": "Administrador"
    } for admin in admins]

def get_regular_users():
    """
    Obtiene todos los usuarios regulares (no admin)
    
    Returns:
        list: Lista de usuarios regulares
    """
    from api.models import User
    
    users = User.query.filter_by(is_admin='user').all()
    
    return [{
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role_display": "Usuario"
    } for user in users]