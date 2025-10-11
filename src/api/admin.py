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


# import os
# from flask import redirect, url_for, request, flash, session, jsonify
# from flask_admin import Admin, BaseView, expose, AdminIndexView
# from flask_admin.contrib.sqla import ModelView
# from markupsafe import Markup
# from wtforms import SelectField, TextAreaField
# from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, decode_token
# from functools import wraps

# from .models import db, User, Farm, Farm_images, DiagnosticReport

# def admin_required(f):
#     """Decorador para verificar autenticación de administrador"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         try:
#             # 1. Intentar obtener token del header Authorization
#             auth_header = request.headers.get('Authorization')
#             if auth_header and auth_header.startswith('Bearer '):
#                 token = auth_header.split(' ')[1]
#                 session['temp_token'] = token
            
#             # 2. Intentar obtener token de session si no hay header
#             elif 'temp_token' in session:
#                 # Usar el token guardado en session
#                 pass
            
#             # 3. Verificar JWT
#             verify_jwt_in_request()
#             current_user_id = get_jwt_identity()
            
#             # 4. Verificar que es admin
#             user = User.query.get(current_user_id)
#             if not user or not user.is_admin:
#                 return redirect('/admin/unauthorized')
                
#             return f(*args, **kwargs)
            
#         except Exception as e:
#             # Si no hay token válido, redirigir a página de info
#             return redirect('/admin/login-info')
    
#     return decorated_function

# class SecureAdminIndexView(AdminIndexView):
#     """Dashboard administrativo con JWT"""
    
#     @expose('/')
#     @admin_required
#     def index(self):
#         try:
#             current_user_id = get_jwt_identity()
#             current_user = User.query.get(current_user_id)
            
#             stats = {
#                 'total_users': User.query.count(),
#                 'total_admins': User.query.filter_by(is_admin=True).count(),
#                 'total_farms': Farm.query.count(),
#                 'total_images': Farm_images.query.count(),
#                 'ndvi_images': Farm_images.query.filter_by(image_type='NDVI').count(),
#                 'aerial_images': Farm_images.query.filter_by(image_type='AERIAL').count(),
#                 'total_reports': DiagnosticReport.query.filter_by(is_diagnostic=False).count(),
#                 'total_diagnostics': DiagnosticReport.query.filter_by(is_diagnostic=True).count(),
#                 'recent_users': User.query.order_by(User.id.desc()).limit(5).all(),
#                 'recent_farms': Farm.query.order_by(Farm.id.desc()).limit(5).all(),
#                 'recent_images': Farm_images.query.order_by(Farm_images.upload_date.desc()).limit(5).all(),
#                 'current_admin': current_user.full_name
#             }
            
#             return self.render('admin/index.html', **stats)
            
#         except Exception as e:
#             return self.render('admin/index.html', error=f"Error: {str(e)}")

# class SecureModelView(ModelView):
#     """Vista base con autenticación JWT"""
    
#     def is_accessible(self):
#         try:
#             # Verificar JWT
#             verify_jwt_in_request(optional=True)
#             current_user_id = get_jwt_identity()
            
#             if not current_user_id:
#                 return False
            
#             user = User.query.get(current_user_id)
#             return user and user.is_admin
            
#         except:
#             return False
    
#     def inaccessible_callback(self, name, **kwargs):
#         return redirect('/admin/login-info')

# # Vistas especializadas usando SecureModelView
# class UserModelView(SecureModelView):
#     column_list = ['id', 'full_name', 'email', 'phone_number', 'is_admin', 'farm_count']
#     column_searchable_list = ['full_name', 'email', 'phone_number']
#     column_filters = ['is_admin', 'email']
#     column_sortable_list = ['id', 'full_name', 'email', 'is_admin']
    
#     column_labels = {
#         'id': 'ID',
#         'full_name': 'Nombre Completo',
#         'email': 'Correo Electrónico',
#         'phone_number': 'Teléfono',
#         'is_admin': 'Es Administrador',
#         'farm_count': 'Granjas'
#     }
    
#     def _format_admin_status(view, context, model, name):
#         if model.is_admin:
#             return Markup('<span class="label label-success">Admin</span>')
#         else:
#             return Markup('<span class="label label-primary">Usuario</span>')
    
#     def _format_farm_count(view, context, model, name):
#         count = len(model.farm_of_user)
#         return Markup(f'<span class="label label-info">{count}</span>')
    
#     column_formatters = {
#         'is_admin': _format_admin_status,
#         'farm_count': _format_farm_count
#     }
    
#     form_columns = ['full_name', 'email', 'phone_number', 'avatar', 'is_admin']
#     form_excluded_columns = ['password', 'salt', 'public_id', 'farm_of_user', 
#                             'user_diagnostic_reports', 'email_diagnostic_reports']

# class FarmModelView(SecureModelView):
#     column_list = ['id', 'farm_name', 'farm_location', 'user_info', 'stats']
#     column_searchable_list = ['farm_name', 'farm_location']
#     column_filters = ['farm_location']
    
#     column_labels = {
#         'id': 'ID',
#         'farm_name': 'Nombre',
#         'farm_location': 'Ubicación',
#         'user_info': 'Propietario',
#         'stats': 'Estadísticas'
#     }
    
#     def _format_user_info(view, context, model, name):
#         user = model.farm_to_user
#         if user:
#             return Markup(f'<strong>{user.full_name}</strong><br><small>{user.email}</small>')
#         return 'Sin propietario'
    
#     def _format_stats(view, context, model, name):
#         images = len(model.images)
#         reports = len(model.diagnostic_reports)
#         return Markup(f'📷 {images} | 📄 {reports}')
    
#     column_formatters = {
#         'user_info': _format_user_info,
#         'stats': _format_stats
#     }

# class FarmImagesModelView(SecureModelView):
#     column_list = ['id', 'farm_info', 'image_type', 'upload_date', 'uploaded_by']
#     column_filters = ['image_type', 'upload_date']
#     column_default_sort = ('upload_date', True)
    
#     column_labels = {
#         'id': 'ID',
#         'farm_info': 'Granja',
#         'image_type': 'Tipo',
#         'upload_date': 'Fecha',
#         'uploaded_by': 'Subido por'
#     }
    
#     def _format_farm_info(view, context, model, name):
#         farm = model.images_table
#         if farm:
#             return Markup(f'<strong>{farm.farm_name}</strong>')
#         return 'Sin granja'
    
#     column_formatters = {
#         'farm_info': _format_farm_info
#     }

# class DiagnosticReportModelView(SecureModelView):
#     column_list = ['id', 'user_info', 'farm_info', 'file_name', 'type_badge', 'uploaded_at']
#     column_filters = ['is_diagnostic', 'uploaded_at']
#     column_default_sort = ('uploaded_at', True)
    
#     column_labels = {
#         'id': 'ID',
#         'user_info': 'Usuario',
#         'farm_info': 'Granja',
#         'file_name': 'Archivo',
#         'type_badge': 'Tipo',
#         'uploaded_at': 'Fecha'
#     }
    
#     def _format_user_info(view, context, model, name):
#         user = model.user_report
#         if user:
#             return Markup(f'<strong>{user.full_name}</strong>')
#         return 'Sin usuario'
    
#     def _format_farm_info(view, context, model, name):
#         farm = model.farm_report
#         if farm:
#             return Markup(f'{farm.farm_name}')
#         return 'Sin granja'
    
#     def _format_type_badge(view, context, model, name):
#         if model.is_diagnostic:
#             return Markup('<span class="label label-success">Diagnóstico</span>')
#         else:
#             return Markup('<span class="label label-primary">Reporte</span>')
    
#     column_formatters = {
#         'user_info': _format_user_info,
#         'farm_info': _format_farm_info,
#         'type_badge': _format_type_badge
#     }

# class LoginInfoView(BaseView):
#     """Vista informativa para login"""
    
#     @expose('/')
#     def login_info(self):
#         from flask import Response
#         html_content = '''
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>AgriVision AI - Admin Login</title>
#             <style>
#                 body { font-family: Arial, sans-serif; margin: 0; padding: 50px; background: #f5f5f5; }
#                 .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
#                 h2 { color: #333; text-align: center; }
#                 ol { margin: 20px 0; }
#                 li { margin: 10px 0; }
#                 .btn { display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; }
#                 .btn:hover { background: #0056b3; }
#                 .info { background: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #bee5eb; }
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h2>Panel Administrativo AgriVision AI</h2>
#                 <div class="info">
#                     <strong>Información:</strong> Necesitas autenticación JWT para acceder.
#                 </div>
#                 <p><strong>Para acceder al panel administrativo:</strong></p>
#                 <ol>
#                     <li>Inicia sesión como <strong>administrador</strong> en la aplicación principal</li>
#                     <li>Asegúrate de tener permisos de administrador</li>
#                     <li>El sistema verificará automáticamente tu token JWT</li>
#                     <li>Regresa a esta página</li>
#                 </ol>
                
#                 <div style="text-align: center; margin-top: 30px;">
#                     <a href="/" class="btn">Ir a la Aplicación Principal</a>
#                     <a href="/admin" class="btn" style="background: #28a745;">Intentar Acceso Nuevamente</a>
#                 </div>
                
#                 <hr style="margin: 30px 0;">
#                 <p><small><strong>Nota:</strong> Si ya eres administrador y tienes problemas de acceso, contacta al desarrollador del sistema.</small></p>
#             </div>
#         </body>
#         </html>
#         '''
#         return Response(html_content, mimetype='text/html')

# class UnauthorizedView(BaseView):
#     """Vista para acceso no autorizado"""
    
#     @expose('/')
#     def unauthorized(self):
#         from flask import Response
#         html_content = '''
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>Acceso Denegado - AgriVision AI</title>
#             <style>
#                 body { font-family: Arial, sans-serif; margin: 0; padding: 50px; background: #f8d7da; }
#                 .container { max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 1px solid #f5c6cb; }
#                 h2 { color: #721c24; text-align: center; }
#                 .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f5c6cb; }
#                 .btn { display: inline-block; background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px; }
#                 .btn:hover { background: #218838; }
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h2>Acceso Denegado</h2>
#                 <div class="error">
#                     <strong>Error:</strong> No tienes permisos de administrador.
#                 </div>
#                 <p>Solo los usuarios con permisos de administrador pueden acceder a este panel.</p>
#                 <p>Si crees que deberías tener acceso:</p>
#                 <ul>
#                     <li>Verifica que tu cuenta tenga permisos de administrador</li>
#                     <li>Contacta al administrador del sistema</li>
#                     <li>Inicia sesión con una cuenta diferente</li>
#                 </ul>
                
#                 <div style="text-align: center; margin-top: 30px;">
#                     <a href="/" class="btn">Volver al Inicio</a>
#                     <a href="/admin/login-info" class="btn" style="background: #007bff;">Información de Login</a>
#                 </div>
#             </div>
#         </body>
#         </html>
#         '''
#         return Response(html_content, mimetype='text/html')

# def setup_admin(app):
#     """Configurar Flask-Admin con JWT"""
    
#     # Configuración
#     if not app.secret_key:
#         app.secret_key = os.environ.get('FLASK_APP_KEY', 'agrivision-secret')
    
#     app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
    
#     # Crear Admin
#     admin = Admin(
#         app, 
#         name='AgriVision AI - Admin Panel',
#         template_mode='bootstrap3',
#         index_view=SecureAdminIndexView(name='Dashboard')
#     )
    
#     # Vistas de datos
#     admin.add_view(UserModelView(User, db.session, name='Usuarios'))
#     admin.add_view(FarmModelView(Farm, db.session, name='Granjas'))
#     admin.add_view(FarmImagesModelView(Farm_images, db.session, name='Imágenes'))
#     admin.add_view(DiagnosticReportModelView(DiagnosticReport, db.session, name='Reportes'))
    
#     # Vistas informativas
#     admin.add_view(LoginInfoView(name='Login Info', endpoint='login_info'))
#     admin.add_view(UnauthorizedView(name='Sin Acceso', endpoint='unauthorized'))
    
#     return admin