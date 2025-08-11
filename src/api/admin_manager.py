#!/usr/bin/env python3
"""
AgriVision AI - Gestor de Administradores
=========================================

Script para gestionar administradores del sistema AgriVision AI.
Ubicación: src/api/admin_manager.py

Ejecución:
    python src/api/admin_manager.py                    # Modo interactivo
    python src/api/admin_manager.py --list             # Listar usuarios
    python src/api/admin_manager.py admin@test.com     # Hacer admin específico
    python src/api/admin_manager.py --help             # Mostrar ayuda
"""

import sys
import os
from models import db, User
from werkzeug.security import generate_password_hash
from base64 import b64encode
from flask_sqlalchemy import SQLAlchemy
from utils import make_user_admin

# Configurar imports para que funcione desde cualquier ubicación
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # src/
root_dir = os.path.dirname(parent_dir)     # raíz/

# Agregar src/ al path
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Importar la aplicación Flask
from app import app

def mostrar_banner():
    """Mostrar banner del sistema"""
    print("\n" + "="*65)
    print("AGRIVISION AI - GESTOR DE ADMINISTRADORES")
    print("="*65)

def mostrar_menu():
    """Mostrar menú principal interactivo"""
    mostrar_banner()
    print("OPCIONES DISPONIBLES:")
    print("-"*65)
    print("1. Ver todos los usuarios registrados")
    print("2. Ver solo administradores")
    print("3. Hacer administrador a usuario existente")
    print("4. Crear nuevo usuario administrador")
    print("5. Quitar privilegios de administrador")
    print("6. Verificar estado de usuario específico")
    print("7. Salir del sistema")
    print("-"*65)

def listar_usuarios():
    """Mostrar lista completa de usuarios"""
    with app.app_context():
        from utils import list_all_users
        
        users = list_all_users()
        
        if not users:
            print("\n No hay usuarios registrados en el sistema")
            return
        
        print(f"\n USUARIOS DEL SISTEMA ({len(users)} total)")
        print("="*75)
        
        admins_count = 0
        for user in users:
            print(f"{user['role_display']} | {user['email']:<35} | {user['full_name']}")
            if user['is_admin'] == 'admin':
                admins_count += 1
        
        print("="*75)
        print(f"Resumen: {admins_count} administradores | {len(users) - admins_count} usuarios regulares")

def listar_administradores():
    """Mostrar solo administradores del sistema"""
    with app.app_context():
        from utils import get_admin_users
        
        admins = get_admin_users()
        
        if not admins:
            print("\n No hay administradores registrados en el sistema")
            print("Sugerencia: Crea el primer administrador con la opción 4")
            return
        
        print(f"\n ADMINISTRADORES DEL SISTEMA ({len(admins)} total)")
        print("="*65)
        
        for admin in admins:
            print(f"{admin['email']:<35} | {admin['full_name']}")
        
        print("="*65)

def hacer_administrador():
    """Convertir usuario existente en administrador"""
    with app.app_context():
        from utils import make_user_admin
        
        print("\n PROMOCIONAR A ADMINISTRADOR")
        print("="*45)
        
        # Mostrar usuarios actuales para referencia
        print("Usuarios actuales en el sistema:")
        listar_usuarios()
        
        print("\n" + "-"*45)
        email = input("Ingresa el email del usuario a promocionar: ").strip()
        
        if not email:
            print("Error: Debes ingresar un email válido")
            return
        
        if "@" not in email:
            print("Error: Formato de email inválido")
            return
        
        # Confirmar acción
        confirmar = input(f"¿Confirmas hacer administrador a '{email}'? (s/N): ").strip().lower()
        
        if confirmar != 's':
            print("Operación cancelada por el usuario")
            return
        
        print("\nProcesando...")
        result = make_user_admin(email)
        print(f"\n{result['message']}")

def crear_nuevo_administrador():
    """Crear un nuevo usuario administrador desde cero"""
    with app.app_context():
        
        print("\n CREAR NUEVO ADMINISTRADOR")
        print("="*35)
        
        # Recopilar información del nuevo usuario
        email = input("Email del nuevo administrador: ").strip()
        if not email:
            print("Error: Email es obligatorio")
            return
        
        if "@" not in email:
            print("Error: Formato de email inválido")
            return
        
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"⚠️  Ya existe un usuario con email '{email}'")
            
            if existing_user.is_admin == 'admin':
                print("Y ya es administrador")
                return
            else:
                # Ofrecer promocionar al existente
                promocionar = input("¿Quieres promocionarlo a administrador? (s/N): ").strip().lower()
                if promocionar == 's':
                    from utils import make_user_admin
                    result = make_user_admin(email)
                    print(f"\n{result['message']}")
                return
        
        full_name = input("Nombre completo: ").strip()
        if not full_name:
            print("❌ Error: Nombre completo es obligatorio")
            return
        
        phone = input("Teléfono (Enter para usar default): ").strip()
        if not phone:
            phone = "000000000"
        
        password = input("Contraseña (Enter para 'admin123'): ").strip()
        if not password:
            password = "admin123"
        
        # Mostrar resumen antes de crear
        print("\nRESUMEN DEL NUEVO ADMINISTRADOR:")
        print("-"*40)
        print(f"Nombre: {full_name}")
        print(f"Email: {email}")
        print(f"Teléfono: {phone}")
        print(f"Contraseña: {password}")
        print(f"Rol: Administrador")
        print("-"*40)
        
        confirmar = input("¿Crear este administrador? (s/N): ").strip().lower()
        if confirmar != 's':
            print("Creación cancelada")
            return
        
        # Crear salt y hash de contraseña (usando el mismo método que register)
        salt = b64encode(os.urandom(32)).decode("utf-8")
        
        def create_password(password, salt):
            return generate_password_hash(f"{password}{salt}")
        
        password_hash = create_password(password, salt)
        
        # Crear el nuevo usuario administrador
        new_admin = User(
            full_name=full_name,
            email=email,
            phone_number=phone,
            password=password_hash,
            salt=salt,
            is_admin='admin'  # Crear directamente como administrador
        )
        
        try:
            print("\n Creando administrador...")
            db.session.add(new_admin)
            db.session.commit()
            
            print("\n ¡ADMINISTRADOR CREADO EXITOSAMENTE!")
            print("="*50)
            print(f"Nombre: {full_name}")
            print(f"Email: {email}")
            print(f"Teléfono: {phone}")
            print(f"Contraseña: {password}")
            print(f"Rol: Administrador")
            print("="*50)
            print("El administrador ya puede iniciar sesión en el sistema")
            
        except Exception as error:
            db.session.rollback()
            print(f"\n Error al crear el administrador: {error.args}")
            print("Verifica que el email no esté duplicado")

def quitar_privilegios_admin():
    """Degradar administrador a usuario regular"""
    with app.app_context():
        from utils import remove_admin_privileges
        
        print("\n QUITAR PRIVILEGIOS DE ADMINISTRADOR")
        print("="*45)
        
        # Mostrar administradores actuales
        print("Administradores actuales:")
        listar_administradores()
        
        print("\n" + "-"*45)
        email = input("Email del administrador a degradar: ").strip()
        
        if not email:
            print("Error: Debes ingresar un email válido")
            return
        
        # Confirmación con advertencia
        print(f"\n ADVERTENCIA:")
        print(f"   Vas a quitar privilegios de administrador a: {email}")
        print(f"   Esta acción convertirá al usuario en usuario regular")
        
        confirmar = input(f"\n ¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ").strip()
        
        if confirmar != 'CONFIRMAR':
            print(" Operación cancelada (debes escribir exactamente 'CONFIRMAR')")
            return
        
        print("\n Procesando...")
        result = remove_admin_privileges(email)
        print(f"\n{result['message']}")

def verificar_estado_usuario():
    """Verificar información y estado de un usuario específico"""
    with app.app_context():
        from utils import is_user_admin
        from models import User
        
        print("\n VERIFICAR ESTADO DE USUARIO")
        print("="*35)
        
        email = input(" Email del usuario a verificar: ").strip()
        
        if not email:
            print(" Error: Debes ingresar un email válido")
            return
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\n Usuario '{email}' no encontrado en el sistema")
            print("Verifica que el email esté escrito correctamente")
            return
        
        is_admin = is_user_admin(email)
        role = "Administrador" if is_admin else "Usuario regular"
        
        print(f"\n INFORMACIÓN DEL USUARIO")
        print("="*40)
        print(f"Nombre completo: {user.full_name}")
        print(f"Email: {user.email}")
        print(f"Teléfono: {user.phone_number}")
        print(f" Rol actual: {role}")
        print(f"ID en sistema: {user.id}")
        print("="*40)

def crear_administradores_automatico():
    """Crear múltiples administradores automáticamente"""
    with app.app_context():
        from utils import make_user_admin
        
        # Lista de emails predefinidos para hacer administradores
        # Personaliza esta lista según tus necesidades
        emails_admin = [
            "gcruz@agrivision.cl"
            # "admin@agrovision.com",
            # "supervisor@agrovision.com",
            # "gerente@agrovision.com"
        ]
        
        print("\n CREACIÓN AUTOMÁTICA DE ADMINISTRADORES")
        print("="*50)
        print("Emails a procesar:")
        for email in emails_admin:
            print(f"{email}")
        
        confirmar = input(f"\n ¿Procesar {len(emails_admin)} emails? (s/N): ").strip().lower()
        if confirmar != 's':
            print("Proceso automático cancelado")
            return
        
        print("\n Procesando emails...")
        print("-"*50)
        
        exitosos = 0
        for email in emails_admin:
            result = make_user_admin(email)
            status = "✅" if result['success'] else "❌"
            print(f"{status} {email}: {result['message']}")
            if result['success']:
                exitosos += 1
        
        print("-"*50)
        print(f"Resultado: {exitosos}/{len(emails_admin)} procesados exitosamente")

def modo_interactivo():
    """Ejecutar el script en modo interactivo con menú"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("🎯 Selecciona una opción (1-7): ").strip()
            
            if opcion == '1':
                listar_usuarios()
            elif opcion == '2':
                listar_administradores()
            elif opcion == '3':
                hacer_administrador()
            elif opcion == '4':
                crear_nuevo_administrador()
            elif opcion == '5':
                quitar_privilegios_admin()
            elif opcion == '6':
                verificar_estado_usuario()
            elif opcion == '7':
                print("\n¡Gracias por usar AgriVision AI!")
                print("¡Que tengas un excelente día!")
                break
            else:
                print(f"\n❌ Opción '{opcion}' no válida")
                print("💡 Por favor selecciona un número del 1 al 7")
        
        except KeyboardInterrupt:
            print("\n\n👋 Proceso interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
        
        # Pausa antes de volver al menú
        input("\n⏸️  Presiona Enter para continuar...")

def mostrar_ayuda():
    """Mostrar información de ayuda del script"""
    print("""
AGRIVISION AI - GESTOR DE ADMINISTRADORES

Ubicación del script: src/api/admin_manager.py

🚀 FORMAS DE EJECUTAR:
   Desde raíz del proyecto:
   python src/api/admin_manager.py                    # Modo interactivo
   python src/api/admin_manager.py --list             # Listar usuarios
   python src/api/admin_manager.py --admins           # Solo administradores
   python src/api/admin_manager.py email@test.com     # Hacer admin específico
   python src/api/admin_manager.py --auto             # Creación automática
   python src/api/admin_manager.py --help             # Esta ayuda

   Desde src/:
   python api/admin_manager.py [opciones]

   Desde api/:
   python admin_manager.py [opciones]

📖 OPCIONES DISPONIBLES:
   --list                 Mostrar todos los usuarios
   --admins              Mostrar solo administradores
   --auto                Crear administradores predefinidos automáticamente
   --help, -h            Mostrar esta información de ayuda
   email@dominio.com     Hacer administrador al email especificado

📝 EJEMPLOS PRÁCTICOS:
   python src/api/admin_manager.py
   python src/api/admin_manager.py admin@agrovision.com
   python src/api/admin_manager.py --list
   python src/api/admin_manager.py --auto

🔧 REQUISITOS:
   - Ejecutar desde la carpeta raíz del proyecto
   - Tener configurada la base de datos
   - Archivo debe estar en src/api/admin_manager.py
    """)

def main():
    """Función principal del script"""
    print("Iniciando AgriVision AI - Gestor de Administradores...")
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) == 1:
        # Sin argumentos = modo interactivo
        modo_interactivo()
    
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        
        if arg == "--list":
            with app.app_context():
                listar_usuarios()
        
        elif arg == "--admins":
            with app.app_context():
                listar_administradores()
        
        elif arg == "--auto":
            crear_administradores_automatico()
        
        elif arg in ["--help", "-h"]:
            mostrar_ayuda()
        
        elif "@" in arg and "." in arg:
            # Parece un email válido
            with app.app_context():
                from utils import make_user_admin
                print(f"🔄 Procesando email: {arg}")
                result = make_user_admin(arg)
                print(f"📧 {arg}: {result['message']}")
        
        else:
            print(f"❌ Argumento no reconocido: '{arg}'")
            print("💡 Usa --help para ver las opciones disponibles")
            sys.exit(1)
    
    else:
        print("❌ Demasiados argumentos proporcionados")
        print("💡 Usa --help para ver el uso correcto")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Script interrumpido por el usuario")
        sys.exit(0)
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("💡 Verifica que estés ejecutando desde la ubicación correcta")
        print("💡 El script debe estar en: src/api/admin_manager.py")
        print("💡 Ejecutar desde la raíz del proyecto: python src/api/admin_manager.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Contacta al desarrollador si el problema persiste")
        sys.exit(1)