"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint, current_app, send_from_directory
from api.models import db, User, Farm, NDVI_images, Aereal_images
from api.utils import generate_sitemap, APIException, send_email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from base64 import b64encode
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import cloudinary
import cloudinary.uploader as uploader
from cloudinary.utils import cloudinary_url

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api, supports_credentials=True)


# @api.route('/hello', methods=['POST', 'GET'])
# def handle_hello():

#     response_body = {
#         "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
#     }

#     return jsonify(response_body), 200



# Manejo del Hash de la contraseña creando 2 funciones

def create_password(password, salt):
    return generate_password_hash(f"{password}{salt}")


def check_password(password_hash, password, salt):
    return check_password_hash(password_hash, f"{password}{salt}")

# Acá termina el manejo del Hash.


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
        'full_name' : data_form.get("full_name", None),       # None es por si no conseguimos el nombre
        'email' : data_form.get("email", None),
        'phone_number' : data_form.get("phone_number", None),
        'avatar' : data_files.get("avatar", None),              # En esta url se guarda el binario
        'password' : data_form.get("password", None),
        'public_id' : ''
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
            result_image = uploader.upload(data["avatar"])      # funcion .upload(lo_que_quiero_subir)

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
                token = create_access_token(identity=str(user.id))
                return jsonify({
                    "token": token}), 200
            else:
                return jsonify("Credentials failure"), 401
            

# 3) Ruta del Dashboard:

@api.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    # body = request.get_json()
    # user = User.query.filter_by(user_id=user_id).one_or_none()

    user = User.query.get(user_id)

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
            identity=body, expires_delta=expires_delta), 200

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
    user = User.query.filter_by(id = current_user_id).first()
    
    # user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Serializamos todas los huertos asociadas al usuario
    farms = [farm.serialize() for farm in user.farm_of_user]

    return jsonify({
        "full_name": user.full_name,
        "email": user.email,
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



# 8) Ruta del



# 9) [GET] /ndvi Listar todos los registros de url NDVI en la base de datos.

@api.route('/ndvi', methods=['GET'])
def get_ndvi_images():
    all_ndvi = NDVI_images.query.all()
    return jsonify([item.serialize() for item in all_ndvi]), 200


# 10) [GET] /aereal Listar todos los registros de url aereos en la base de datos.

@api.route('/aereal', methods=['GET'])
def get_aereal_images():
    all_aereal = Aereal_images.query.all()
    return jsonify([item.serialize() for item in all_aereal]), 200 


# 11) [GET] /users Listar todos los registros de usuario en la base de datos.

@api.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([item.serialize() for item in users]), 200


# 12) [GET] /user/<int:user_id> Muestra la información de un solo usuario según su id.

@api.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    single_user = User.query.get(user_id=user_id)

    if single_user is None:
        return jsonify({"error": "Person not found"}), 404
    else:
        return jsonify(single_user.serialize()), 200
    
# 13) [POST] de /farms para agregar campos

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


# 14) Eliminar huerto creado

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


# 15) Ruta para recibir la imagen del Avatar

@api.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "No se encontró ninguna imagen"}), 400

    file = request.files['avatar']

    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        # Subir la imagen a Cloudinary
        result_image = uploader.upload(file)
        avatar_url = result_image.get("secure_url")

        # Actualizar el usuario
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        user.avatar = avatar_url

        db.session.commit()

        return jsonify({"message": "Avatar actualizado con éxito", "avatar": avatar_url}), 200

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

# from flask import 

@api.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)
