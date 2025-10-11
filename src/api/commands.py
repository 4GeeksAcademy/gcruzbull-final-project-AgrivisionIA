
import click
from api.models import db, User
import sys
import os
from werkzeug.security import generate_password_hash
from base64 import b64encode
from flask_sqlalchemy import SQLAlchemy
from api.utils import make_user_admin

"""
In this file, you can add as many commands as you want using the @app.cli.command decorator
Flask commands are usefull to run cronjobs or tasks outside of the API but sill in integration 
with youy database, for example: Import the price of bitcoin every night as 12am
"""
def setup_commands(app):
    
    """ 
    This is an example command "insert-test-users" that you can run from the command line
    by typing: $ flask insert-test-users 5
    Note: 5 is the number of users to add
    """
    @app.cli.command("insert-test-users") # name of our command
    @click.argument("count") # argument of out command
    def insert_test_users(count):
        print("Creating test users")
        for x in range(1, int(count) + 1):
            user = User()
            user.email = "test_user" + str(x) + "@test.com"
            user.password = "123456"
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            print("User: ", user.email, " created.")

        print("All test users created")

    @app.cli.command("insert-test-data")
    def insert_test_data():
        pass


 # ============ COMANDOS DE ADMINISTRACIÓN ============

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.option("--name", default="Administrador", help="Nombre completo del administrador")
    @click.option("--password", default="admin123", help="Contraseña del administrador")
    def create_admin_command(email, name, password):
        """Crear un nuevo usuario administrador."""
        
        # Usar las funciones de utils.py para mantener consistencia
        from api.utils import make_user_admin
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"Ya existe un usuario con email '{email}'")
            
            # Usar función de utils para hacerlo admin
            result = make_user_admin(email)
            click.echo(result["message"])
            return
        
        # Crear salt y hash de contraseña (como en register)
        salt = b64encode(os.urandom(32)).decode("utf-8")
        
        # Usar la misma función de hash que en routes.py
        def create_password(password, salt):
            return generate_password_hash(f"{password}{salt}")
        
        password_hash = create_password(password, salt)
        
        # Crear nuevo usuario admin
        new_user = User(
            full_name=name,
            email=email,
            phone_number="000000000",  # Teléfono por defecto
            password=password_hash,
            salt=salt,
            is_admin=True  # Crear admin
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            click.echo(f"Usuario administrador creado exitosamente:")
            click.echo(f"Nombre: {name}")
            click.echo(f"Email: {email}")
            click.echo(f"Contraseña: {password}")
            click.echo(f"Rol: Administrador")
        except Exception as error:
            db.session.rollback()
            click.echo(f"Error al crear usuario: {error}")

    @app.cli.command("make-admin")
    @click.argument("email")
    def make_admin_command(email):
        """Convertir un usuario existente en administrador."""
        
        # Usar función de utils.py
        result = make_user_admin(email)
        click.echo(result["message"])

    @app.cli.command("list-users")
    def list_users_command():
        """Listar todos los usuarios del sistema."""
        
        # Usar función de utils.py
        from api.utils import list_all_users
        users = list_all_users()
        
        if not users:
            click.echo(" No hay usuarios registrados")
            return
        
        click.echo(f"\n Lista de usuarios ({len(users)} total):")
        click.echo("-" * 70)
        
        admins = sum(1 for u in users if u['is_admin'] == 'admin')
        regulars = len(users) - admins
        
        for user in users:
            click.echo(f"{user['role_display']} | {user['email']:<30} | {user['full_name']}")
        
        click.echo("-" * 70)
        click.echo(f"Administradores: {admins} | Usuarios regulares: {regulars}")

    @app.cli.command("remove-admin")
    @click.argument("email")
    def remove_admin_command(email):
        """Quitar privilegios de administrador a un usuario."""
        
        # Usar función de utils.py
        from api.utils import remove_admin_privileges
        result = remove_admin_privileges(email)
        click.echo(result["message"])

    @app.cli.command("list-admins")
    def list_admins_command():
        """Listar solo los administradores."""
        
        from api.utils import get_admin_users
        admins = get_admin_users()
        
        if not admins:
            click.echo("No hay administradores registrados")
            return
        
        click.echo(f"\nAdministradores ({len(admins)} total):")
        click.echo("-" * 50)
        
        for admin in admins:
            click.echo(f" {admin['email']:<30} | {admin['full_name']}")
        
        click.echo("-" * 50)

    @app.cli.command("admin-status")
    @click.argument("email")
    def admin_status_command(email):
        """Verificar si un usuario es administrador."""
        
        from api.utils import is_user_admin
        is_admin = is_user_admin(email)
        
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f"Usuario '{email}' no encontrado")
            return
        
        role = "Administrador" if is_admin else "Usuario regular"
        click.echo(f"{user.full_name} ({email})")
        click.echo(f"Rol: {role}")

    # ============ COMANDO PARA INICIALIZAR PROYECTO ============

    @app.cli.command("init-project")
    @click.option("--admin-email", prompt="Email del administrador", help="Email del primer administrador")
    @click.option("--admin-name", prompt="Nombre del administrador", help="Nombre completo del administrador")
    @click.option("--admin-password", prompt="Contraseña", hide_input=True, confirmation_prompt=True, help="Contraseña del administrador")
    def init_project_command(admin_email, admin_name, admin_password):
        """Inicializar proyecto con primer administrador."""
        
        click.echo("Inicializando proyecto AgriVision AI...")
        
        # Verificar si ya hay administradores
        from api.utils import get_admin_users
        existing_admins = get_admin_users()
        
        if existing_admins:
            click.echo(f"Ya existen {len(existing_admins)} administradores:")
            for admin in existing_admins:
                click.echo(f"    {admin['email']}")
            
            if not click.confirm("¿Continuar creando otro administrador?"):
                click.echo("Operación cancelada")
                return
        
        # Crear primer administrador
        salt = b64encode(os.urandom(32)).decode("utf-8")
        
        def create_password(password, salt):
            return generate_password_hash(f"{password}{salt}")
        
        password_hash = create_password(admin_password, salt)
        
        admin_user = User(
            full_name=admin_name,
            email=admin_email,
            phone_number="000000000",
            password=password_hash,
            salt=salt,
            is_admin='admin'
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            click.echo("Proyecto inicializado exitosamente!")
            click.echo(f"Primer administrador creado:")
            click.echo(f"Email: {admin_email}")
            click.echo(f"Nombre: {admin_name}")
            click.echo(f"Contraseña: [configurada]")
            click.echo("\n Ya puedes iniciar sesión en AgriVision AI!")
            
        except Exception as error:
            db.session.rollback()
            click.echo(f"Error al crear administrador: {error}")

    # ============ COMANDO DE VERIFICACIÓN DEL SISTEMA ============

    @app.cli.command("system-check")
    def system_check_command():
        """Verificar el estado del sistema."""
        
        click.echo("VERIFICACIÓN DEL SISTEMA AGRIVISION AI")
        click.echo("=" * 50)
        
        # Verificar conexión a base de datos
        try:
            from api.utils import list_all_users, get_admin_users
            
            users = list_all_users()
            admins = get_admin_users()
            
            click.echo(f"Conexión a base de datos: OK")
            click.echo(f"Total usuarios: {len(users)}")
            click.echo(f"Total administradores: {len(admins)}")
            
            if len(admins) == 0:
                click.echo("ADVERTENCIA: No hay administradores configurados")
                click.echo("Ejecuta: flask create-admin admin@agrovision.com")
            
            # Verificar modelos
            from api.models import User, Farm, DiagnosticReport, Farm_images
            
            click.echo(f"  Tablas verificadas:")
            click.echo(f"   - Usuarios: {User.query.count()}")
            click.echo(f"   - Campos: {Farm.query.count()}")
            click.echo(f"   - Reportes diagnósticos: {DiagnosticReport.query.count()}")
            click.echo(f"   - Imágenes de campo: {Farm_images.query.count()}")
            
            click.echo("=" * 50)
            click.echo("Sistema verificado correctamente")
            
        except Exception as error:
            click.echo(f"Error en verificación: {error}")

    # ============ COMANDOS DE MIGRACIÓN ============

    @app.cli.command("migrate-admin-field")
    def migrate_admin_field_command():
        """Migrar campo is_admin de String a Boolean."""
        
        click.echo("MIGRACIÓN: is_admin (String → Boolean)")
        click.echo("=" * 50)
        
        try:
            # Verificar estado actual
            sample_user = User.query.first()
            if sample_user and isinstance(sample_user.is_admin, bool):
                click.echo("Los datos ya están en formato Boolean.")
                return
            
            users = User.query.all()
            if not users:
                click.echo("No hay usuarios en la base de datos.")
                return
            
            click.echo(f"Procesando {len(users)} usuarios...")
            
            admins_converted = 0
            users_converted = 0
            errors = 0
            
            for user in users:
                try:
                    old_value = getattr(user, 'is_admin', 'user')
                    
                    if str(old_value).lower() in ['admin', 'true', '1']:
                        user.is_admin = True
                        admins_converted += 1
                        click.echo(f"  {user.email}: 'admin' → True")
                    else:
                        user.is_admin = False
                        users_converted += 1
                        click.echo(f"  {user.email}: 'user' → False")
                        
                except Exception as e:
                    errors += 1
                    click.echo(f"  ERROR {user.email}: {str(e)}")
            
            if errors == 0:
                db.session.commit()
                click.echo("=" * 50)
                click.echo("MIGRACIÓN COMPLETADA")
                click.echo(f"Administradores: {admins_converted}")
                click.echo(f"Usuarios regulares: {users_converted}")
                click.echo(f"Total: {admins_converted + users_converted}")
            else:
                db.session.rollback()
                click.echo(f"MIGRACIÓN FALLIDA - {errors} errores")
                
        except Exception as e:
            db.session.rollback()
            click.echo(f"Error crítico: {str(e)}")

    @app.cli.command("verify-admin-migration")
    def verify_admin_migration_command():
        """Verificar migración del campo is_admin."""
        
        click.echo("VERIFICACIÓN DE MIGRACIÓN")
        click.echo("=" * 40)
        
        try:
            total_users = User.query.count()
            admin_users = User.query.filter_by(is_admin=True).count()
            regular_users = User.query.filter_by(is_admin=False).count()
            
            click.echo(f"Total usuarios: {total_users}")
            click.echo(f"Administradores: {admin_users}")
            click.echo(f"Usuarios regulares: {regular_users}")
            
            # Verificar tipos de datos
            all_boolean = True
            sample_size = min(5, total_users)
            
            if sample_size > 0:
                click.echo("\nMuestra de usuarios:")
                for user in User.query.limit(sample_size):
                    data_type = type(user.is_admin).__name__
                    click.echo(f"  {user.email}: {user.is_admin} ({data_type})")
                    
                    if not isinstance(user.is_admin, bool):
                        all_boolean = False
            
            if all_boolean:
                click.echo("\nVERIFICACIÓN EXITOSA: Todos los campos son Boolean")
            else:
                click.echo("\nVERIFICACIÓN FALLIDA: Algunos campos no son Boolean")
                
        except Exception as e:
            click.echo(f"Error en verificación: {str(e)}")

    @app.cli.command("full-migration")
    def full_migration_command():
        """Ejecutar migración completa y verificación."""
        
        click.echo("MIGRACIÓN COMPLETA DE is_admin")
        click.echo("=" * 60)
        
        # Ejecutar migración
        from flask import current_app
        ctx = current_app.app_context()
        
        with ctx:
            # Simular el comando de migración
            try:
                # Verificar estado actual
                sample_user = User.query.first()
                if sample_user and isinstance(sample_user.is_admin, bool):
                    click.echo("Los datos ya están en formato Boolean.")
                    # Ejecutar verificación
                    verify_admin_migration_command()
                    return
                
                users = User.query.all()
                if not users:
                    click.echo("No hay usuarios en la base de datos.")
                    return
                
                click.echo(f"Procesando {len(users)} usuarios...")
                
                admins_converted = 0
                users_converted = 0
                
                for user in users:
                    old_value = getattr(user, 'is_admin', 'user')
                    
                    if str(old_value).lower() in ['admin', 'true', '1']:
                        user.is_admin = True
                        admins_converted += 1
                    else:
                        user.is_admin = False
                        users_converted += 1
                
                db.session.commit()
                
                click.echo("MIGRACIÓN COMPLETADA")
                click.echo(f"Administradores: {admins_converted}")
                click.echo(f"Usuarios regulares: {users_converted}")
                
                # Ejecutar verificación
                click.echo("\n" + "=" * 40)
                verify_admin_migration_command()
                
                click.echo("\nPROCESO COMPLETADO EXITOSAMENTE")
                
            except Exception as e:
                db.session.rollback()
                click.echo(f"Error en migración completa: {str(e)}")

    @app.cli.command("backup-users")
    def backup_users_command():
        """Crear respaldo de usuarios antes de migración."""
        
        import json
        from datetime import datetime
        
        click.echo("CREANDO RESPALDO DE USUARIOS")
        click.echo("=" * 40)
        
        try:
            users = User.query.all()
            backup_data = []
            
            for user in users:
                backup_data.append({
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'is_admin': str(user.is_admin),  # Convertir a string para JSON
                    'is_admin_type': type(user.is_admin).__name__,
                    'backup_date': datetime.now().isoformat()
                })
            
            # Guardar en archivo
            backup_filename = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            click.echo(f"Respaldo creado: {backup_filename}")
            click.echo(f"Usuarios respaldados: {len(backup_data)}")
            
        except Exception as e:
            click.echo(f"Error creando respaldo: {str(e)}")

    # ============ ACTUALIZAR COMANDOS EXISTENTES ============
    
    # Actualizar el comando create-admin para usar Boolean
    @app.cli.command("create-admin-v2")
    @click.argument("email")
    @click.option("--name", default="Administrador", help="Nombre completo del administrador")
    @click.option("--password", default="admin123", help="Contraseña del administrador")
    def create_admin_v2_command(email, name, password):
        """Crear administrador con formato Boolean (versión actualizada)."""
        
        # Verificar si ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"Ya existe un usuario con email '{email}'")
            
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.session.commit()
                click.echo("Usuario promocionado a administrador.")
            else:
                click.echo("El usuario ya es administrador.")
            return
        
        # Crear salt y hash
        salt = b64encode(os.urandom(32)).decode("utf-8")
        
        def create_password(password, salt):
            return generate_password_hash(f"{password}{salt}")
        
        password_hash = create_password(password, salt)
        
        # Crear nuevo usuario admin con BOOLEAN
        new_user = User(
            full_name=name,
            email=email,
            phone_number="000000000",
            password=password_hash,
            salt=salt,
            is_admin=True  # BOOLEAN TRUE
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            click.echo("Usuario administrador creado exitosamente:")
            click.echo(f"Nombre: {name}")
            click.echo(f"Email: {email}")
            click.echo(f"Contraseña: {password}")
            click.echo(f"Rol: Administrador (Boolean: True)")
        except Exception as error:
            db.session.rollback()
            click.echo(f"Error al crear usuario: {error}")

    # ============ COMANDO DE TRANSICIÓN ============
    
    @app.cli.command("transition-to-boolean")
    @click.option("--backup/--no-backup", default=True, help="Crear respaldo antes de migrar")
    @click.option("--verify/--no-verify", default=True, help="Verificar después de migrar")
    def transition_to_boolean_command(backup, verify):
        """Proceso completo de transición a Boolean."""
        
        click.echo("TRANSICIÓN COMPLETA A SISTEMA BOOLEAN")
        click.echo("=" * 50)
        
        # Paso 1: Crear respaldo si se solicita
        if backup:
            click.echo("Paso 1: Creando respaldo...")
            backup_users_command()
            click.echo("")
        
        # Paso 2: Ejecutar migración
        click.echo("Paso 2: Ejecutando migración...")
        full_migration_command()
        click.echo("")
        
        # Paso 3: Verificar si se solicita
        if verify:
            click.echo("Paso 3: Verificación final...")
            verify_admin_migration_command()
        
        click.echo("\nTRANSICIÓN COMPLETADA")
        click.echo("Ahora puedes usar:")
        click.echo("  flask create-admin-v2 para crear admins con Boolean")
        click.echo("  Actualizar routes.py para eliminar conversiones de String")

    click.echo("Comandos de administración cargados correctamente")