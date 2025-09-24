import os
from flask_admin import Admin
from .models import db, User, Farm, Farm_images, DiagnosticReport
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Farm, db.session))
    admin.add_view(ModelView(Farm_images, db.session))
    admin.add_view(ModelView(DiagnosticReport, db.session))
    # admin.add_view(ModelView(ImageAnalysis, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))


import os
from flask import redirect, url_for, request, flash, session
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from markupsafe import Markup
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from datetime import datetime

from .models import db, User, Farm, Farm_images, DiagnosticReport

def admin_required(f):
    """Decorador para verificar que el usuario es administrador usando flask_jwt_extended"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar JWT token usando flask_jwt_extended
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Buscar usuario
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin:
                flash('Acceso denegado. Necesitas permisos de administrador.', 'error')
                return redirect(url_for('admin.login_view'))
                
        except Exception as error:
            flash('Token inválido o expirado. Por favor inicia sesión.', f"error: {error.args}")
            return redirect(url_for('admin.login_view'))
        
        return f(*args, **kwargs)
    return decorated_function

class SecureAdminIndexView(AdminIndexView):
    """Vista personalizada del dashboard administrativo"""
    
    @expose('/')
    def index(self):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin:
                flash('Acceso denegado. Necesitas permisos de administrador.', 'error')
                return redirect(url_for('admin.login_view'))
            
            # Estadísticas del dashboard
            stats = {
                'total_users': User.query.count(),
                'total_admins': User.query.filter_by(is_admin=True).count(),
                'total_farms': Farm.query.count(),
                'total_images': Farm_images.query.count(),
                'ndvi_images': Farm_images.query.filter_by(image_type='NDVI').count(),
                'aerial_images': Farm_images.query.filter_by(image_type='AERIAL').count(),
                'total_reports': DiagnosticReport.query.filter_by(is_diagnostic=False).count(),
                'total_diagnostics': DiagnosticReport.query.filter_by(is_diagnostic=True).count(),
                'recent_users': User.query.order_by(User.id.desc()).limit(5).all(),
                'recent_farms': Farm.query.order_by(Farm.id.desc()).limit(5).all(),
                'recent_images': Farm_images.query.order_by(Farm_images.upload_date.desc()).limit(5).all(),
                'farms_without_diagnostics': Farm.query.outerjoin(
                    DiagnosticReport, 
                    (Farm.id == DiagnosticReport.farm_id) & (DiagnosticReport.is_diagnostic == True)
                ).filter(DiagnosticReport.id.is_(None)).count()
            }
            
            return self.render('admin/dashboard.html', **stats)
            
        except Exception:
            flash('Debes iniciar sesión para acceder al panel administrativo.', 'warning')
            return redirect(url_for('admin.login_view'))

class SecureModelView(ModelView):
    """Vista base segura para todos los modelos usando flask_jwt_extended"""
    
    def is_accessible(self):
        """Verificar si el usuario actual puede acceder"""
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return False
                
            user = User.query.get(current_user_id)
            return user and user.is_admin
            
        except Exception:
            return False
    
    def inaccessible_callback(self, name, **kwargs):
        """Callback cuando el acceso es denegado"""
        flash('Acceso denegado. Necesitas permisos de administrador.', 'error')
        return redirect(url_for('admin.login_view'))

class UserModelView(SecureModelView):
    """Vista personalizada para el modelo User"""
    
    # Configuración de columnas
    column_list = ['id', 'full_name', 'email', 'phone_number', 'is_admin', 'farm_count']
    column_searchable_list = ['full_name', 'email', 'phone_number']
    column_filters = ['is_admin', 'email']
    column_sortable_list = ['id', 'full_name', 'email', 'is_admin']
    column_default_sort = ('id', True)
    
    # Configuración de formulario
    form_columns = ['full_name', 'email', 'phone_number', 'avatar', 'is_admin']
    form_widget_args = {
        'full_name': {'placeholder': 'Nombre completo del usuario'},
        'email': {'placeholder': 'email@ejemplo.com'},
        'phone_number': {'placeholder': '+569 1234 5678'},
        'avatar': {'placeholder': 'URL de Cloudinary'}
    }
    
    # Labels en español
    column_labels = {
        'id': 'ID',
        'full_name': 'Nombre Completo',
        'email': 'Correo Electrónico',
        'phone_number': 'Teléfono',
        'is_admin': 'Es Administrador',
        'avatar': 'Avatar',
        'farm_count': 'Campos'
    }
    
    # Formateo personalizado
    def _format_admin_status(view, context, model, name):
        if model.is_admin:
            return Markup('<span class="label label-success">Administrador</span>')
        else:
            return Markup('<span class="label label-primary">Usuario</span>')
    
    def _format_farm_count(view, context, model, name):
        count = len(model.farm_of_user)
        if count == 0:
            return Markup('<span class="label label-warning">0 huertos</span>')
        else:
            return Markup(f'<span class="label label-info">{count} huerto{"s" if count != 1 else ""}</span>')
    
    def _format_avatar(view, context, model, name):
        if model.avatar:
            return Markup(f'<img src="{model.avatar}" width="50" height="50" class="img-circle">')
        else:
            return Markup('<span class="label label-default">Sin avatar</span>')
    
    column_formatters = {
        'is_admin': _format_admin_status,
        'farm_count': _format_farm_count,
        'avatar': _format_avatar
    }
    
    # Excluir campos sensibles del formulario
    form_excluded_columns = ['password', 'salt', 'public_id', 'farm_of_user', 
                            'user_diagnostic_reports', 'email_diagnostic_reports']
    
    # Configuración de creación
    def on_model_change(self, form, model, is_created):
        if is_created:
            # Generar public_id si es nuevo usuario
            import uuid
            model.public_id = str(uuid.uuid4())
            
            # Si no tiene contraseña, generar una temporal
            if not hasattr(model, 'password') or not model.password:
                from werkzeug.security import generate_password_hash
                from base64 import b64encode
                import os
                
                temp_password = "TempPass123!"
                salt = b64encode(os.urandom(32)).decode("utf-8")
                model.salt = salt
                model.password = generate_password_hash(f"{temp_password}{salt}")
                
                flash(f'Usuario creado con contraseña temporal: {temp_password}', 'warning')

class FarmModelView(SecureModelView):
    """Vista personalizada para el modelo Farm"""
    
    column_list = ['id', 'farm_name', 'farm_location', 'user_info', 'image_count', 'report_count', 'diagnostic_count']
    column_searchable_list = ['farm_name', 'farm_location']
    column_filters = ['farm_location', 'farm_to_user.full_name']
    column_sortable_list = ['id', 'farm_name', 'farm_location']
    
    # Labels en español
    column_labels = {
        'id': 'ID',
        'farm_name': 'Nombre del Campo',
        'farm_location': 'Ubicación',
        'user_id': 'ID Usuario',
        'user_info': 'Propietario',
        'image_count': 'Imágenes',
        'report_count': 'Reportes Usuario',
        'diagnostic_count': 'Diagnósticos Admin'
    }
    
    # Formateo personalizado
    def _format_user_info(view, context, model, name):
        user = model.farm_to_user
        if user:
            admin_badge = 'success' if user.is_admin else 'primary'
            return Markup(f'<span class="label label-{admin_badge}">{user.full_name}</span><br><small>{user.email}</small>')
        return 'Sin propietario'
    
    def _format_image_count(view, context, model, name):
        count = len(model.images)
        if count == 0:
            return Markup('<span class="label label-warning">0 imágenes</span>')
        else:
            return Markup(f'<span class="label label-success">{count} imagen{"es" if count != 1 else ""}</span>')
    
    def _format_report_count(view, context, model, name):
        count = len([r for r in model.diagnostic_reports if not r.is_diagnostic])
        if count == 0:
            return Markup('<span class="label label-default">0 reportes</span>')
        else:
            return Markup(f'<span class="label label-info">{count} reporte{"s" if count != 1 else ""}</span>')
    
    def _format_diagnostic_count(view, context, model, name):
        count = len([r for r in model.diagnostic_reports if r.is_diagnostic])
        if count == 0:
            return Markup('<span class="label label-danger">Sin diagnósticos</span>')
        else:
            return Markup(f'<span class="label label-success">{count} diagnóstico{"s" if count != 1 else ""}</span>')
    
    column_formatters = {
        'user_info': _format_user_info,
        'image_count': _format_image_count,
        'report_count': _format_report_count,
        'diagnostic_count': _format_diagnostic_count
    }
    
    # Configuración de formulario
    form_columns = ['farm_name', 'farm_location', 'user_id']
    form_args = {
        'user_id': {
            'label': 'Propietario',
            'coerce': int,
            'choices': lambda: [(user.id, f"{user.full_name} ({user.email})") for user in User.query.all()]
        }
    }

class FarmImagesModelView(SecureModelView):
    """Vista personalizada para el modelo Farm_images"""
    
    column_list = ['id', 'image_preview', 'farm_info', 'image_type', 'upload_date', 'uploaded_by']
    column_searchable_list = ['file_name', 'uploaded_by', 'image_type']
    column_filters = ['image_type', 'upload_date', 'farm_id']
    column_sortable_list = ['id', 'upload_date', 'image_type']
    column_default_sort = ('upload_date', True)
    
    # Labels en español
    column_labels = {
        'id': 'ID',
        'farm_id': 'ID Campo',
        'farm_info': 'Campo',
        'image_url': 'URL de Imagen',
        'image_preview': 'Vista Previa',
        'image_type': 'Tipo',
        'upload_date': 'Fecha de Subida',
        'file_name': 'Nombre de Archivo',
        'uploaded_by': 'Subido por'
    }
    
    # Formateo personalizado
    def _format_image_preview(view, context, model, name):
        if model.image_url:
            type_class = 'success' if model.image_type == 'NDVI' else 'info'
            return Markup(f'''
                <div class="text-center">
                    <img src="{model.image_url}" width="100" height="60" class="img-thumbnail">
                    <br><span class="label label-{type_class}">{model.image_type}</span>
                </div>
            ''')
        return 'Sin imagen'
    
    def _format_farm_info(view, context, model, name):
        farm = model.images_table
        if farm:
            return Markup(f'<strong>{farm.farm_name}</strong><br><small>{farm.farm_location}</small>')
        return 'Sin campo'
    
    def _format_upload_date(view, context, model, name):
        if model.upload_date:
            date_str = model.upload_date.strftime('%d/%m/%Y %H:%M')
            return Markup(f'<small>{date_str}</small>')
        return 'Sin fecha'
    
    column_formatters = {
        'image_preview': _format_image_preview,
        'farm_info': _format_farm_info,
        'upload_date': _format_upload_date
    }
    
    # Configuración de formulario
    form_columns = ['farm_id', 'image_url', 'image_type', 'file_name', 'uploaded_by']
    form_args = {
        'image_type': {
            'choices': [('NDVI', 'NDVI'), ('AERIAL', 'AERIAL')]
        },
        'farm_id': {
            'label': 'Campo',
            'coerce': int,
            'choices': lambda: [(farm.id, f"{farm.farm_name} - {farm.farm_location}") for farm in Farm.query.all()]
        }
    }

class DiagnosticReportModelView(SecureModelView):
    """Vista personalizada para el modelo DiagnosticReport"""
    
    column_list = ['id', 'user_info', 'farm_info', 'file_name', 'type_badge', 'uploaded_at', 'uploaded_by']
    column_searchable_list = ['file_name', 'uploaded_by', 'description']
    column_filters = ['is_diagnostic', 'uploaded_at', 'user_id', 'farm_id']
    column_sortable_list = ['id', 'uploaded_at', 'is_diagnostic']
    column_default_sort = ('uploaded_at', True)
    
    # Labels en español
    column_labels = {
        'id': 'ID',
        'user_id': 'ID Usuario',
        'user_info': 'Usuario',
        'farm_id': 'ID Campo',
        'farm_info': 'Campo',
        'file_name': 'Nombre del Archivo',
        'file_url': 'URL del Archivo',
        'uploaded_at': 'Fecha de Subida',
        'uploaded_by': 'Subido por',
        'description': 'Descripción',
        'is_diagnostic': 'Es Diagnóstico',
        'type_badge': 'Tipo'
    }
    
    # Formateo personalizado
    def _format_user_info(view, context, model, name):
        user = model.user_report
        if user:
            admin_badge = 'success' if user.is_admin else 'primary'
            return Markup(f'<span class="label label-{admin_badge}">{user.full_name}</span><br><small>{user.email}</small>')
        return 'Sin usuario'
    
    def _format_farm_info(view, context, model, name):
        farm = model.farm_report
        if farm:
            return Markup(f'<strong>{farm.farm_name}</strong><br><small>{farm.farm_location}</small>')
        return Markup('<span class="label label-default">Sin campo</span>')
    
    def _format_type_badge(view, context, model, name):
        if model.is_diagnostic:
            return Markup('<span class="label label-success">Diagnóstico Admin</span>')
        else:
            return Markup('<span class="label label-primary">Reporte Usuario</span>')
    
    def _format_file_link(view, context, model, name):
        if model.file_url:
            return Markup(f'<a href="{model.file_url}" target="_blank" class="btn btn-sm btn-primary">Ver archivo</a>')
        return 'Sin archivo'
    
    column_formatters = {
        'user_info': _format_user_info,
        'farm_info': _format_farm_info,
        'type_badge': _format_type_badge,
        'file_url': _format_file_link
    }
    
    # Configuración de formulario
    form_columns = ['user_id', 'farm_id', 'file_name', 'file_url', 'uploaded_by', 'description', 'is_diagnostic']
    form_args = {
        'user_id': {
            'label': 'Usuario',
            'coerce': int,
            'choices': lambda: [(user.id, f"{user.full_name} ({user.email})") for user in User.query.all()]
        },
        'farm_id': {
            'label': 'Campo (Opcional)',
            'coerce': int,
            'choices': lambda: [(0, 'Sin campo asignado')] + [(farm.id, f"{farm.farm_name} - {farm.farm_location}") for farm in Farm.query.all()]
        },
        'description': {
            'widget': TextAreaField().widget,
            'render_kw': {'rows': 4, 'placeholder': 'Descripción detallada del reporte o diagnóstico...'}
        }
    }

class LoginView(BaseView):
    """Vista de login simple que redirige a tu frontend"""
    
    @expose('/')
    def login_view(self):
        # Mensaje para redirigir al usuario a tu aplicación principal
        message = """
        <div style="text-align: center; margin-top: 50px;">
            <h2>Panel Administrativo AgriVision AI</h2>
            <p>Para acceder al panel administrativo, primero debes:</p>
            <ol style="display: inline-block; text-align: left;">
                <li>Iniciar sesión en la aplicación principal</li>
                <li>Asegurarte de tener permisos de administrador</li>
                <li>Regresar a esta página</li>
            </ol>
            <br>
            <a href="{}" class="btn btn-primary">Ir a la Aplicación Principal</a>
        </div>
        """.format(os.environ.get('FRONTEND_URL', 'http://localhost:3000'))
        
        return Markup(message)

def setup_admin(app):
    """Configurar Flask-Admin integrado con tu sistema existente"""
    
    # Configuración básica
    app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
    
    # Crear instancia de Admin con vista personalizada
    admin = Admin(
        app, 
        name='AgriVision AI - Panel Administrativo',
        template_mode='bootstrap3',
        index_view=SecureAdminIndexView(name='Dashboard', menu_icon_type='fa', menu_icon_value='fa-dashboard')
    )
    
    # Agregar vistas de modelos personalizadas
    admin.add_view(UserModelView(
        User, db.session,
        name='Usuarios',
        category='Gestión de Usuarios',
        menu_icon_type='fa',
        menu_icon_value='fa-users'
    ))
    
    admin.add_view(FarmModelView(
        Farm, db.session,
        name='Campos',
        category='Gestión Agrícola',
        menu_icon_type='fa',
        menu_icon_value='fa-leaf'
    ))
    
    admin.add_view(FarmImagesModelView(
        Farm_images, db.session,
        name='Imágenes de Drones',
        category='Gestión Agrícola',
        menu_icon_type='fa',
        menu_icon_value='fa-camera'
    ))
    
    admin.add_view(DiagnosticReportModelView(
        DiagnosticReport, db.session,
        name='Reportes y Diagnósticos',
        category='Análisis',
        menu_icon_type='fa',
        menu_icon_value='fa-file-text-o'
    ))
    
    # Agregar vista de login informativa
    admin.add_view(LoginView(
        name='Información de Acceso',
        menu_icon_type='fa',
        menu_icon_value='fa-info-circle'
    ))
    
    return admin