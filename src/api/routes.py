"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, current_app, send_from_directory
from api.models import db, User, Farm, Farm_images, DiagnosticReport
from api.utils import generate_sitemap, APIException, send_email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from base64 import b64encode
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime, timezone
import cloudinary
import cloudinary.uploader as uploader
from cloudinary.utils import cloudinary_url
from uuid import uuid4

api = Blueprint('api', __name__)

# Allow CORS requests to this API
# CORS(api, supports_credentials=True)

# CONFIGURACIÓN CORS MEJORADA
CORS(api, 
     supports_credentials=True,
     origins=["*"],  # En producción, especifica dominios exactos
)

# Manejo del Hash de la contraseña creando 2 funciones


def create_password(password, salt):
    return generate_password_hash(f"{password}{salt}")


def check_password(password_hash, password, salt):
    return check_password_hash(password_hash, f"{password}{salt}")

# Acá termina el manejo del Hash.

# Verificar si el usuario es admin
def is_admin_user(user_id):
    from api.utils import is_user_admin_by_id
    return is_user_admin_by_id(user_id)

# Duración de vida del token
expires_token = 200
expires_delta = timedelta(hours=expires_token)

# Comienzo rutas.

@api.route('/healt-check', methods=['GET'])
def handle_check():
    response_body = {
        "message": "Todo esta ok"
    }

    return jsonify(response_body), 200


# 1) Register:

@api.route('/register', methods=['POST'])
def add_user():
    data_form = request.form        # Trae datos del formulario
    data_files = request.files      # Trae archivos del formulario

    print("form", data_form)
    print("files", data_files)

    data = {
        # None es por si no conseguimos el nombre
        'full_name': data_form.get("full_name", None),
        'email': data_form.get("email", None),
        'phone_number': data_form.get("phone_number", None),
        # En esta url se guarda el binario
        'avatar': data_files.get("avatar", None),
        'password': data_form.get("password", None),
        'public_id': ''
    }

    print("avatar raw object:", data["avatar"])

    # Creación del usuario:
    if any(field is None or field == "" for field in [data['full_name'], data['email'], data['phone_number'], data['password']]):
        return jsonify('Error: Fields full_name, email, phone_number, and password are mandatory'), 400

    # Verificar si el usuario ya existe
    existing_user = User.query.filter_by(email=data['email']).one_or_none()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    try:
        # Crear el salt antes de crear la contraseña
        salt = b64encode(os.urandom(32)).decode("utf-8")

        # Subir imagen a Cloudinary

        if data["avatar"] is not None:
            # funcion .upload(lo_que_quiero_subir)
            result_image = uploader.upload(data["avatar"])

            data["avatar"] = result_image["secure_url"]

        # Crear el usuario
        user = User()
        user.full_name = data['full_name']
        user.email = data['email']
        user.phone_number = data['phone_number']
        user.avatar = data['avatar']
        user.salt = salt
        user.password = create_password(data['password'], salt)

        # Transacción a la BD:
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}"), 500

# 2) Ruta del Login

@api.route('/login', methods=['POST'])
def handle_login():
    data = request.json
    email = data.get("email", None)
    password = data.get("password", None)

    if email is None or password is None:
        return jsonify('You must write the email and password'), 400

    # Validamos existencia del usuario
    else:
        user = User.query.filter_by(email=email).one_or_none()
        if user is None:
            return jsonify("Credentials are wrong, try again"), 400
        else:
            if check_password(user.password, password, user.salt):
                token = create_access_token(identity=str(
                    user.id), expires_delta=expires_delta)
                return jsonify({
                    "token": token}), 200
            else:
                return jsonify("Credentials failure"), 401

# 3) Ruta del Dashboard:

@api.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if user is None:
        return jsonify(
            {"Error": "User not found"}
        ), 404
    else:
        return jsonify(
            {'message': 'Bienvenido a tu dashboard de Agrovision IA! Acá podras ver el análisis del historial de tu huerto, reportes guardados, y configuraciones de cuenta'}
        ), 200

# 4) Ruta del Reset-Password

@api.route("/reset-password", methods=["POST"])
def reset_password_user():
    body = request.json

    user = User.query.filter_by(email=body).one_or_none()

    if user is None:
        return jsonify("User not found"), 404
    else:
        create_token = create_access_token(
            identity=body, expires_delta=expires_delta)

    message_url = f"""
    <a href="{os.getenv("FRONTEND_URL")}/reset-password?token={create_token}">Recuperar contraseña</a>
"""
    data = {
        "subject": "Password recovery",
        "to": body,
        "message": message_url
    }

    sended_email = send_email(
        data.get("subject"), data.get("to"), data.get("message"))

    if sended_email:
        return jsonify("Message sent successfully"), 200
    else:
        return jsonify("Error"), 400

# 5) Ruta del Update-Password

@api.route("/update-password", methods=["PUT"])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    body = request.get_json()
    user = User.query.filter_by(user_id=user_id).one_or_none()

    if user is not None:
        salt = b64encode(os.urandom(32)).decode("utf-8")
        new_password = body.get("new_password", None)

        if not new_password:
            return jsonify({"Error": "The password was not updated"}), 400

        password = create_password(new_password, salt)

        user.salt = salt
        user.password = password

        try:
            db.session.commit()
            return jsonify("Password changed successfuly"), 201
        except Exception as error:
            db.session.rollback()
            return jsonify(f"Error: {error.args}"), 500

    else:
        return jsonify({"Error": "User not found"}), 404

# 6) Ruta del Profile

@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Serializamos todas los huertos asociadas al usuario
    farms = [farm.serialize() for farm in user.farm_of_user]

    return jsonify({
        "full_name": user.full_name,
        "email": user.email,
        'is_admin': user.is_admin == 'admin',  # CONVERTIR A BOOLEAN para el frontend
        "phone_number": user.phone_number,
        "avatar": user.avatar,
        "farms": farms              # Lista de diccionarios con farm_name, farm_location y user_id
    }), 200

# 7) Ruta del AboutUs

@api.route('/about-us', methods=['GET'])
def get_about_us():
    return jsonify({
        "message": {
            "mission": "Mediante el uso de Inteligencia Artificial...",
            "technology": "Nuestra plataforma utiliza algoritmos...",
            "history": "AgriVision AI nació con la visión..."
        }
    }), 200

# subir imagen (ndvi o aerea)

@api.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    data_form = request.form        # Trae datos del formulario
    data_files = request.files      # Trae archivos del formulario

    print(data_files)

    try:
        current_user_id = get_jwt_identity()
        farm_id = data_form.get("farm_id")
        image_type = data_form.get("image_type")  # 'ndvi' o 'aerial'
        image_file = data_files.get("image_url")  # imagen

        if image_file is None:
            return jsonify({"error": "No se recibió ningún archivo de imagen"}), 400

        if not farm_id or not image_type or not image_file:
            return jsonify({"error": "Faltan datos requeridos"}), 400

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Subir imagen a Cloudinary
        upload_result = uploader.upload(image_file, folder="dron_images")

        # Obtener la URL segura
        image_url = upload_result.get('secure_url')

        # file_name = image_file.filename

        file_name = upload_result.get("original_filename"),
        uploaded_by = str(user.email)  # o email si lo tienes

        # Crear instancia del modelo
        new_image = Farm_images(
            farm_id=farm_id,
            image_type=image_type,
            image_url=image_url,
            upload_date=datetime.now(timezone.utc),
            file_name=file_name,
            uploaded_by=uploaded_by
        )
        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            "message": "Image uploaded successfully",
            "url": image_url,
            "data": new_image.serialize()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": "Error al subir imagen", "error": {error.args}}), 500

# obtener imagenes del usuario autenticado

@api.route('/user-images', methods=['GET'])
@jwt_required()
def get_user_images():
    current_user_id = get_jwt_identity()

    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    farms = Farm.query.filter_by(user_id=current_user_id).all()
    farm_ids = [farm.id for farm in farms]

    # La función in_() se usa para filtrar por varios valores (como un WHERE ... IN (...) en SQL). SELECT * FROM farm_images WHERE farm_id IN (1, 2, 5);....Este SQL dice: dame todas las imágenes cuya farm_id esté en la lista [1, 2, 5].
    images = Farm_images.query.filter(Farm_images.farm_id.in_(farm_ids)).all()

    result = [{
        "id": images.id,
        "farm_id": images.farm_id,
        "image_url": images.image_url,
        "image_type": images.image_type,
        "upload_date": images.upload_date.isoformat() if images.upload_date else None
    } for images in images]

    return jsonify(result), 200

# obtener todas las imagenes de un campo

@api.route('/user-images/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_farm_images(farm_id):
    try:
        images = Farm_images.query.filter_by(farm_id=farm_id).all()
        return jsonify([img.serialize() for img in images]), 200
    except Exception as error:
        return jsonify({"Error": "Error al obtener imágenes", "error": {error.args}}), 500

# eliminar una imagen
@api.route('/delete-image/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    current_user_id = get_jwt_identity()
    image = Farm_images.query.get(image_id)

    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if not image:
        return jsonify({"error": "Imagen no encontrada"}), 404

    # Verifica que la imagen pertenezca a una finca del usuario
    farm = Farm.query.get(image.farm_id)

    if not farm or farm.user_id != current_user_id:
        return jsonify({"message": "No autorizado para eliminar esta imagen"}), 403

    db.session.delete(image)
    db.session.commit()

    return jsonify({"message": "Imagen eliminada exitosamente"}), 200

# obtener imagen especifica
@api.route('/get-image/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image(image_id):
    current_user_id = get_jwt_identity()
    image = Farm_images.query.get(image_id)

    if not image:
        return jsonify({"message": "Imagen no encontrada"}), 404

    farm = Farm.query.get(image.farm_id)
    if not farm or farm.user_id != current_user_id:
        return jsonify({"message": "No autorizado"}), 403

    return jsonify({
        "id": image.id,
        "farm_id": image.farm_id,
        "image_url": image.image_url,
        "image_type": image.image_type,
        "upload_date": image.upload_date.isoformat() if image.upload_date else None
    }), 200

# 12) [GET] /users Listar todos los registros de usuario en la base de datos.

@api.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    users = User.query.all(user_id)
    return jsonify([item.serialize() for item in users]), 200

# 13) [GET] /user/<int:user_id> Muestra la información de un solo usuario según su id.

@api.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    single_user = User.query.get(user_id)

    if single_user is None:
        return jsonify({"error": "Person not found"}), 404
    else:
        return jsonify(single_user.serialize()), 200

# 14) [POST] de /farms para agregar campos

@api.route('/farms', methods=['POST'])
@jwt_required()
def create_farm():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    farm_name = data.get("farm_name")
    farm_location = data.get("farm_location")

    if not farm_name or not farm_location:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Validar si ya existe un huerto con ese nombre o ubicación
    existing_farm = Farm.query.filter(
        (Farm.farm_name == farm_name) | (Farm.farm_location == farm_location)
    ).first()

    if existing_farm:
        return jsonify({"error": "Ya existe un huerto con ese nombre o ubicación"}), 409

    new_farm = Farm(
        user_id=current_user_id,
        farm_name=farm_name,
        farm_location=farm_location
    )

    db.session.add(new_farm)
    db.session.commit()

    return jsonify({"message": "Registro de campo creado correctamente"}), 201

# 15) Eliminar huerto creado

@api.route('/farms/<int:farm_id>', methods=['DELETE'])
@jwt_required()
def delete_farm(farm_id):
    current_user_id = get_jwt_identity()
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user_id).first()

    if not farm:
        return jsonify({"error": "Campo no encontrado o no autorizado"}), 404

    db.session.delete(farm)
    db.session.commit()

    return jsonify({"message": "Huerto eliminado correctamente"}), 200

# 16) Ruta para filtrar imágenes NDVI por farm_id: recibe un farm_id como parámetro y devuelve todas las imágenes NDVI asociadas a ese campo.

@api.route('/ndvi-images/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_ndvi_images_by_farm(farm_id):
    from models import NDVI_images

    current_user_id = get_jwt_identity()

    images = NDVI_images.query.filter_by(
        id=farm_id, user_id=current_user_id).all()

    if not images:
        return jsonify({"message": "No NDVI images found for this farm"}), 404

    return jsonify([img.serialize() for img in images]), 200

# 17) Ruta para filtrar imágenes aéreas por farm_id: recibe un farm_id como parámetro y devuelve todas las imágenes aéreas asociadas a ese campo.

@api.route('/aerial-images/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_aerial_images_by_farm(farm_id):
    from models import Aerial_images

    current_user_id = get_jwt_identity()

    images = Aerial_images.query.filter_by(
        id=farm_id, user_id=current_user_id).all()

    if not images:
        return jsonify({"message": "No aerial images found for this farm"}), 404

    return jsonify([img.serialize() for img in images]), 200

# ) Ruta para actualizar la imagen del Avatar

@api.route('/update-avatar', methods=['PUT'])
@jwt_required()
def update_avatar():

    data_files = request.files      # Trae archivos del formulario

    if 'avatar' not in data_files:
        return jsonify({"error": "No se encontró ninguna imagen"}), 400

    image = data_files['avatar']
    if image.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).one_or_none()

        if user is None:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Eliminar imagen anterior si tiene public_id
        if user.public_id:
            uploader.destroy(user.public_id)

        # Subir nueva imagen
        result_image = uploader.upload(image)

        avatar_url = result_image.get("secure_url")
        public_id = result_image.get("public_id")

        # Actualizar usuario
        user.avatar = avatar_url
        user.public_id = public_id
        db.session.commit()

        print("Se subió imagen nueva:", avatar_url)

        return jsonify({"avatar": avatar_url}), 200

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"Error al subir la imagen: {error.args}"}), 500

@api.route('/get-avatar', methods=['GET'])
@jwt_required()
def get_avatar():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({"avatar": user.avatar}), 200

    except Exception as error:
        return jsonify({"error": f"Error al obtener avatar: {error.args}"}), 500

@api.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

# ----------- SUBIR REPORTES -----------------------------

# 2) Ruta para que el usuario vea el informe: Simplemente devolver el enlace o servir el archivo:

@api.route('/get-report/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_single_report(farm_id):
    current_user_id = get_jwt_identity()
    # request.args: es un diccionario especial de Flask que contiene los parámetros de la URL enviados en la query string.
    # devuelve Un número entero (int) o None
    farm_id = request.args.get('farm_id', type=int)

    # objeto de tipo Farm
    farm = Farm.query.get(farm_id)

    if not farm:
        return jsonify({"error": "Campo no encontrado"}), 404

    current_user = User.query.get(current_user_id)
    # Verificar permisos si no admin
    # getattr() en Python se utiliza para acceder a atributos de un objeto de forma dinámica, utilizando el nombre del atributo como una cadena.
    # getattr(objeto, nombre_atributo, valor_predeterminado)
    if not getattr(current_user, 'is_admin', False):
        if farm.user_id != current_user_id:
            return jsonify({"error": "No autorizado para ver este reporte"}), 403
        
    if not current_user:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    single_report = DiagnosticReport.query.filter_by(user_id=current_user_id, farm_id=farm_id).first()
    if not single_report:
        return jsonify({"error": "Reporte no encontrado"}), 404

    return jsonify({
        "message": "Reporte de Huerto obtenido",
        "id": single_report.id,
        "user_id": single_report.user_id,
        "farm_id": single_report.farm_id,
        'file_name': single_report.file_name,
        "file_url": single_report.file_url,
        "uploaded_at": single_report.uploaded_at.isoformat(),
        'description': single_report.description        
    }), 200
        
# Solo admin puede subir diagnósticos
@api.route('/upload-diagnostic', methods=['POST'])
@jwt_required()
def upload_diagnostic_admin_only():
    current_user_id = get_jwt_identity()
    
    # VERIFICAR PERMISOS DE ADMIN
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo los administradores pueden subir diagnósticos"}), 403

    data_files = request.files
    data_form = request.form

    print("Admin uploading diagnostic:", data_files.keys())

    try:
        farm_id = data_form.get("farm_id")
        file_report = data_files.get('diagnostic_file')
        
        if not file_report:
            return jsonify({"error": "No se envió ningún informe de diagnóstico"}), 400
        
        if file_report.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400

        if farm_id is None:
            return jsonify({"error": "Falta farm_id"}), 400

        secure_file_name = secure_filename(file_report.filename)
        
        # Validar extensión
        ALLOWED_EXT = {'pdf', 'docx', 'doc', 'txt'}
        extension = secure_file_name.rsplit('.', 1)[-1].lower() if '.' in secure_file_name else ''
        if extension not in ALLOWED_EXT:
            return jsonify({"error": f"Formato no permitido. Permitidos: {ALLOWED_EXT}"}), 400

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Verificar que la farm existe
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404

        # Subir archivo a Cloudinary CON PERMISOS PÚBLICOS
        try:
            upload_result = uploader.upload(
                file_report,
                public_id=f"diagnostic_{secure_file_name.rsplit('.', 1)[0]}_{current_user_id}_{farm_id}",
                folder="diagnostics",
                access_mode="public",
                type="upload",
                delivery_type="upload",
                # resource_type="raw"  # necesario para PDF, DOCX, TXT
            )
            
            print(f"Cloudinary upload result: {upload_result.get('secure_url')}")
            
        except Exception as error:
            print(f"Error en Cloudinary: {error}")
            return jsonify({"error": f"Error al subir a Cloudinary: {error.args}"}), 500

        secure_report_url = upload_result.get("secure_url")

        # Guardar en la base de datos COMO DIAGNÓSTICO
        new_diagnostic = DiagnosticReport(
            user_id=current_user_id,
            farm_id=farm_id,
            file_name=secure_file_name,
            file_url=secure_report_url,
            uploaded_at=datetime.now(timezone.utc),
            uploaded_by=user.email,
            description=data_form.get('description', 'Informe de diagnóstico'),
            is_diagnostic=True  # MARCAR COMO DIAGNÓSTICO
        )
        
        db.session.add(new_diagnostic)
        db.session.commit()

        return jsonify({
            "message": "Informe de diagnóstico subido correctamente",
            "diagnostic_id": new_diagnostic.id,
            "file_url": secure_report_url,
            "data": new_diagnostic.serialize()
        }), 201

    except Exception as error:
        db.session.rollback()
        print(f"Error completo: {error}")
        return jsonify({"error": f"Error al subir el informe de diagnóstico: {error.args}"}), 500

# Obtener solo diagnósticos
@api.route('/get-diagnostics/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_diagnostics_only(farm_id):
    current_user_id = get_jwt_identity()
    
    try:
        # Verificar que la farm existe
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404

        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verificar permisos: debe ser el dueño de la farm o admin
        if not is_admin_user(current_user_id) and farm.user_id != int(current_user_id):
            return jsonify({"error": "No autorizado para ver estos diagnósticos"}), 403
        
        # Obtener SOLO diagnósticos (no reportes de usuarios)
        diagnostics = DiagnosticReport.query.filter_by(
            farm_id=farm_id,
            is_diagnostic=True
        ).order_by(DiagnosticReport.uploaded_at.desc()).all()

        return jsonify([diagnostic.serialize() for diagnostic in diagnostics]), 200

    except Exception as error:
        print(f"Error getting diagnostics: {error}")
        return jsonify({"error": f"Error al obtener informes de diagnóstico: {error.args}"}), 500

# Upload-report para usuarios (NO diagnósticos)
@api.route('/upload-report', methods=['POST'])
@jwt_required()
def upload_report():
    current_user_id = get_jwt_identity()
    user_id = current_user_id

    data_files = request.files
    data_form = request.form

    print("User uploading report:", data_files.keys())

    try:
        farm_id = data_form.get("farm_id")
        file_report = data_files.get('file_url')  # Mantener nombre original
        
        if not file_report:
            return jsonify({"error": "No se envió ningún archivo"}), 400
        
        if file_report.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400

        if farm_id is None:
            return jsonify({"error": "Falta farm_id"}), 400

        secure_file_name = secure_filename(file_report.filename)
        
        # Validar extensión
        ALLOWED_EXT = {'pdf', 'docx', 'doc', 'txt'}
        extension = secure_file_name.rsplit('.', 1)[-1].lower() if '.' in secure_file_name else ''
        if extension not in ALLOWED_EXT:
            return jsonify({"error": f"Formato no permitido. Permitidos: {ALLOWED_EXT}"}), 400

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Verificar que farm existe y pertenece al usuario
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404
        
        if farm.user_id != int(current_user_id):
            return jsonify({"error": "No autorizado para subir reportes a este campo"}), 403

        # Subir archivo a Cloudinary
        try:
            upload_result = uploader.upload(
                file_report,
                public_id=f"report_{secure_file_name.rsplit('.', 1)[0]}_{current_user_id}_{farm_id}",
                folder="reports",
                access_mode="public",
                type="upload",
                delivery_type="upload",
                # resource_type="raw"  # necesario para PDF, DOCX, TXT
            )
        except Exception as error:
            return jsonify({"error": f"Error al subir a Cloudinary: {error.arg}"}), 500

        secure_report_url = upload_result.get("secure_url")
        print("User report uploaded to:", secure_report_url)

        # Guardar en la base de datos COMO REPORTE DE USUARIO
        new_report = DiagnosticReport(
            user_id=user_id,
            farm_id=farm_id,
            file_name=secure_file_name,
            file_url=secure_report_url,
            uploaded_at=datetime.now(timezone.utc),
            uploaded_by=user.email,
            description=data_form.get('description', 'Informe de usuario'),
            is_diagnostic=False  # NO es diagnóstico, es reporte de usuario
        )
        
        db.session.add(new_report)
        db.session.commit()

        return jsonify({
            "message": "Informe subido correctamente",
            "report_id": new_report.id,
            "file_url": secure_report_url,
            "data": new_report.serialize()
        }), 201

    except Exception as error:
        db.session.rollback()
        print(f"Error uploading report: {error}")
        return jsonify({"error": f"Error al subir el archivo: {error.args}"}), 500

@api.route('/download-report/<int:report_id>', methods=['GET'])
@jwt_required()
def download_report(report_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    email = User.query.filter_by(email = email, user_id = current_user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    report = DiagnosticReport.query.filter_by(
        id=report_id,
        user_id=current_user_id
    ).first()

    if not report:
        return jsonify({"error": "Reporte no encontrado"}), 404
    
    farm_id = Farm.query.filter_by(farm_id=farm_id, user_id=user).first()

    if not report:
        return jsonify({"error": "Reporte no encontrado"}), 404

    return jsonify({
        "id": report.id,
        'user_id': report.user_id,
        "farm_id": report.farm_id,
        'file_name': report.file_name,
        "file_url": report.file_url,
        "upload_by": report.email,
        "uploaded_at": report.uploaded_at.isoformat()
    }), 200

    # # send_from_directory() sirve el archivo de manera segura desde la carpeta configurada.
    # # as_attachment=False abre en el navegador (si es PDF). Si quieres forzar descarga, pon as_attachment=True.

# Reports que solo devuelve reportes de usuarios (no diagnósticos)
@api.route('/reports', methods=['GET'])
@jwt_required()
def list_reports():
    current_user_id = get_jwt_identity()
    farm_id = request.args.get('farm_id', type=int)

    if not farm_id:
        return jsonify({"error": "farm_id es requerido"}), 400

    try:
        # Verificar que farm existe y el usuario tiene acceso
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404
        
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Verificar permisos: debe ser el dueño de farm o admin
        if not is_admin_user(current_user_id) and farm.user_id != int(current_user_id):
            return jsonify({"error": "No autorizado para ver estos reportes"}), 403

        # Obtener SOLO reportes de usuarios (no diagnósticos)
        reports = DiagnosticReport.query.filter_by(
            farm_id=farm_id,
            is_diagnostic=False  # Solo reportes de usuarios
        ).order_by(DiagnosticReport.uploaded_at.desc()).all()

        return jsonify([report.serialize() for report in reports]), 200

    except Exception as error:
        print(f"Error getting reports: {error}")
        return jsonify({"error": f"Error al obtener reportes: {error.args}"}), 500
    
# ------ INFORME DEL DASHBOARD ------

@api.route('/upload_informe', methods=['POST'])
@jwt_required()
def upload_informe():
    current_user_id = get_jwt_identity()

    farm_id = DiagnosticReport.query.filter_by(farm_id=farm_id)

    data_files = request.files

    try:
        # Verificar si el archivo viene en la request
        if 'report' not in data_files:
            return jsonify({"error": "No file part"}), 400

        file_report = data_files['report']
        if file_report.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Subir a Cloudinary
        upload_result = uploader.upload(file_report)

        file_url = upload_result['secure_url']
        file_name = file_report.filename

        # Guardar en la base de datos

        new_informe = DiagnosticReport(
                user_id = current_user_id,
                farm_id = farm_id,
                file_name = file_name,
                file_url = file_url,
                uploaded_at = datetime.now(timezone.utc)
            )
        db.session.add(new_informe)
        db.session.commit()

        return jsonify({
            "message": "Informe subido correctamente",
            "file_id": new_informe.id,
            "file_url": file_url
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"Error al subir el archivo: {error.args}"}), 500


# ============ ENDPOINTS DE ADMINISTRACIÓN  ============

# VER TODOS LOS USUARIOS CON SUS CAMPOS
@api.route('/admin/all-users', methods=['GET'])
@jwt_required()
def get_all_users_admin():
    """Ver todos los usuarios con sus campos (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden acceder"}), 403
    
    try:
        users = User.query.all()
        
        result = []
        for user in users:
            user_farms = [farm.serialize() for farm in user.farm_of_user]
            
            # Contar reportes e imágenes por usuario
            total_reports = DiagnosticReport.query.filter_by(user_id=user.id, is_diagnostic=False).count()
            total_images = 0
            for farm in user.farm_of_user:
                total_images += Farm_images.query.filter_by(farm_id=farm.id).count()
            
            result.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_admin": user.is_admin,
                "avatar": user.avatar,
                "farms_count": len(user_farms),
                "farms": user_farms,
                "total_reports": total_reports,
                "total_images": total_images
            })
        
        return jsonify({
            "total_users": len(result),
            "users": result
        }), 200
        
    except Exception as error:
        return jsonify({"error": f"Error al obtener usuarios: {error.args}"}), 500

# VER TODOS LOS CAMPOS CON DETALLES
@api.route('/admin/all-farms', methods=['GET'])
@jwt_required()
def get_all_farms_admin():
    """Ver todos los campos de todos los usuarios con estadísticas (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden acceder"}), 403
    
    try:
        # Obtener todos los campos con información del usuario
        farms = db.session.query(Farm, User).join(User, Farm.user_id == User.id).all()
        
        result = []
        for farm, user in farms:
            # Estadísticas del campo
            reports_count = DiagnosticReport.query.filter_by(farm_id=farm.id, is_diagnostic=False).count()
            diagnostics_count = DiagnosticReport.query.filter_by(farm_id=farm.id, is_diagnostic=True).count()
            images_count = Farm_images.query.filter_by(farm_id=farm.id).count()
            ndvi_images = Farm_images.query.filter_by(farm_id=farm.id, image_type='NDVI').count()
            aerial_images = Farm_images.query.filter_by(farm_id=farm.id, image_type='AERIAL').count()
            
            result.append({
                "farm_id": farm.id,
                "farm_name": farm.farm_name,
                "farm_location": farm.farm_location,
                "user_id": user.id,
                "user_name": user.full_name,
                "user_email": user.email,
                "user_avatar": user.avatar,
                "statistics": {
                    "user_reports": reports_count,
                    "admin_diagnostics": diagnostics_count,
                    "total_images": images_count,
                    "ndvi_images": ndvi_images,
                    "aerial_images": aerial_images
                }
            })
        
        return jsonify({
            "total_farms": len(result),
            "farms": result
        }), 200
        
    except Exception as error:
        return jsonify({"error": f"Error al obtener campos: {str(error)}"}), 500

# VER DETALLES ESPECÍFICOS DE UN CAMPO
@api.route('/admin/farm-details/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_farm_details_admin(farm_id):
    """Ver detalles completos de un campo específico (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden acceder"}), 403
    
    try:
        # Obtener campo con información del usuario
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404
        
        user = User.query.get(farm.user_id)
        
        # Obtener reportes del usuario para este campo
        user_reports = DiagnosticReport.query.filter_by(
            farm_id=farm_id, 
            is_diagnostic=False
        ).order_by(DiagnosticReport.uploaded_at.desc()).all()
        
        # Obtener diagnósticos del admin para este campo
        admin_diagnostics = DiagnosticReport.query.filter_by(
            farm_id=farm_id, 
            is_diagnostic=True
        ).order_by(DiagnosticReport.uploaded_at.desc()).all()
        
        # Obtener imágenes del campo
        images = Farm_images.query.filter_by(farm_id=farm_id).order_by(Farm_images.upload_date.desc()).all()
        
        result = {
            "farm": {
                "id": farm.id,
                "farm_name": farm.farm_name,
                "farm_location": farm.farm_location
            },
            "owner": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "avatar": user.avatar
            },
            "user_reports": [report.serialize() for report in user_reports],
            "admin_diagnostics": [diagnostic.serialize() for diagnostic in admin_diagnostics],
            "images": [image.serialize() for image in images],
            "statistics": {
                "total_user_reports": len(user_reports),
                "total_admin_diagnostics": len(admin_diagnostics),
                "total_images": len(images),
                "ndvi_images": len([img for img in images if img.image_type == 'NDVI']),
                "aerial_images": len([img for img in images if img.image_type == 'AERIAL'])
            }
        }
        
        return jsonify(result), 200
        
    except Exception as error:
        return jsonify({"error": f"Error al obtener detalles del campo: {str(error)}"}), 500

# SUBIR DIAGNÓSTICO A CAMPO ESPECÍFICO
@api.route('/admin/upload-diagnostic', methods=['POST'])
@jwt_required()
def upload_diagnostic_to_specific_farm():
    """Subir diagnóstico a un campo específico (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden subir diagnósticos"}), 403

    data_files = request.files
    data_form = request.form

    try:
        farm_id = data_form.get("farm_id")
        description = data_form.get("description", "Diagnóstico profesional del campo")
        file_report = data_files.get('diagnostic_file')
        
        if not file_report:
            return jsonify({"error": "No se envió archivo de diagnóstico"}), 400
        
        if not farm_id:
            return jsonify({"error": "farm_id es requerido"}), 400

        # Verificar que la farm existe
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404

        secure_file_name = secure_filename(file_report.filename)
        
        # Validar extensión
        ALLOWED_EXT = {'pdf', 'docx', 'doc', 'txt'}
        extension = secure_file_name.rsplit('.', 1)[-1].lower() if '.' in secure_file_name else ''
        if extension not in ALLOWED_EXT:
            return jsonify({"error": f"Formato no permitido. Permitidos: {ALLOWED_EXT}"}), 400

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "Usuario administrador no encontrado"}), 404

        # Subir archivo a Cloudinary CON PERMISOS PÚBLICOS
        try:
            upload_result = uploader.upload(
                file_report,
                public_id=f"diagnostic_{farm_id}_{secure_file_name.rsplit('.', 1)[0]}_{current_user_id}",
                folder="diagnostics",
                # resource_type="auto",
                access_mode="public",
                type="upload",
                delivery_type="upload",
                # resource_type="raw"  # necesario para PDF, DOCX, TXT
            )
        except Exception as error:
            return jsonify({"error": f"Error al subir a Cloudinary: {str(error)}"}), 500

        secure_report_url = upload_result.get("secure_url")

        # Guardar en la base de datos COMO DIAGNÓSTICO
        new_diagnostic = DiagnosticReport(
            user_id=current_user_id,  # Admin que sube
            farm_id=farm_id,          # Campo específico
            file_name=secure_file_name,
            file_url=secure_report_url,
            uploaded_at=datetime.now(timezone.utc),
            uploaded_by=user.email,
            description=description,
            is_diagnostic=True  # MARCAR COMO DIAGNÓSTICO
        )
        
        db.session.add(new_diagnostic)
        db.session.commit()

        return jsonify({
            "message": "Diagnóstico subido correctamente",
            "diagnostic_id": new_diagnostic.id,
            "file_url": secure_report_url,
            "farm_info": {
                "farm_id": farm.id,
                "farm_name": farm.farm_name,
                "farm_location": farm.farm_location,
                "owner": farm.farm_to_user.full_name
            },
            "data": new_diagnostic.serialize()
        }), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"Error al subir diagnóstico: {str(error)}"}), 500

# VER TODOS LOS REPORTES POR ESTADO
@api.route('/admin/reports-overview', methods=['GET'])
@jwt_required()
def get_reports_overview_admin():
    """Overview de todos los reportes y diagnósticos (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden acceder"}), 403
    
    try:
        # Reportes de usuarios (pendientes de diagnóstico)
        user_reports = DiagnosticReport.query.filter_by(is_diagnostic=False).all()
        
        # Diagnósticos ya realizados
        admin_diagnostics = DiagnosticReport.query.filter_by(is_diagnostic=True).all()
        
        # Campos sin diagnósticos
        farms_with_diagnostics = [d.farm_id for d in admin_diagnostics]
        farms_without_diagnostics = Farm.query.filter(~Farm.id.in_(farms_with_diagnostics)).all()
        
        result = {
            "overview": {
                "total_user_reports": len(user_reports),
                "total_admin_diagnostics": len(admin_diagnostics),
                "farms_without_diagnostics": len(farms_without_diagnostics),
                "total_farms": Farm.query.count(),
                "total_users": User.query.filter_by(is_admin='user').count()
            },
            "recent_user_reports": [report.serialize() for report in user_reports[-10:]],  # Últimos 10
            "recent_diagnostics": [diagnostic.serialize() for diagnostic in admin_diagnostics[-10:]],  # Últimos 10
            "farms_needing_attention": [{
                "farm_id": farm.id,
                "farm_name": farm.farm_name,
                "farm_location": farm.farm_location,
                "owner": farm.farm_to_user.full_name,
                "user_reports": DiagnosticReport.query.filter_by(farm_id=farm.id, is_diagnostic=False).count()
            } for farm in farms_without_diagnostics[:5]]  # Primeros 5
        }
        
        return jsonify(result), 200
        
    except Exception as error:
        return jsonify({"error": f"Error al obtener overview: {str(error)}"}), 500

# OBTENER DIAGNÓSTICOS DE UN CAMPO ESPECÍFICO
@api.route('/admin/diagnostics/<int:farm_id>', methods=['GET'])
@jwt_required()
def get_farm_diagnostics_admin(farm_id):
    """Obtener todos los diagnósticos de un campo específico (solo admin)"""
    current_user_id = get_jwt_identity()
    
    if not is_admin_user(current_user_id):
        return jsonify({"error": "Solo administradores pueden acceder"}), 403
    
    try:
        # Verificar que la farm existe
        farm = Farm.query.get(farm_id)
        if not farm:
            return jsonify({"error": "Campo no encontrado"}), 404
        
        # Obtener diagnósticos del campo
        diagnostics = DiagnosticReport.query.filter_by(
            farm_id=farm_id, 
            is_diagnostic=True
        ).order_by(DiagnosticReport.uploaded_at.desc()).all()
        
        result = {
            "farm_info": {
                "farm_id": farm.id,
                "farm_name": farm.farm_name,
                "farm_location": farm.farm_location,
                "owner": farm.farm_to_user.full_name
            },
            "diagnostics": [diagnostic.serialize() for diagnostic in diagnostics],
            "total_diagnostics": len(diagnostics)
        }
        
        return jsonify(result), 200
        
    except Exception as error:
        return jsonify({"error": f"Error al obtener diagnósticos: {error.args}"}), 500