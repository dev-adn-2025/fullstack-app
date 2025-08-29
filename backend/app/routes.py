import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from .models import Cliente, Proyecto, Base
from sqlalchemy import create_engine

from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA = int(os.getenv("JWT_EXP_DELTA", "3600"))  # segundos
JWT_REFRESH_DELTA = int(os.getenv("JWT_REFRESH_DELTA", "86400"))  # segundos

# API versioning
bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/appdb")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

# Decorador para proteger endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.endpoint == "api_v1.registrar_cliente":
            return f(*args, **kwargs)
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.cliente_id = payload["sub"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(*args, **kwargs)
    return decorated

# Login endpoint
@bp.route("/login", methods=["POST"])
def login():
    data = request.json
    with get_session() as session:
        cliente = session.query(Cliente).filter_by(usuario=data["usuario"]).first()
        if not cliente or not cliente.activo:
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
        if not check_password_hash(cliente.contrasena, data["contrasena"]):
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
        now = datetime.utcnow()
        access_payload = {
            "sub": cliente.id,
            "exp": now + timedelta(seconds=JWT_EXP_DELTA),
            "iat": now,
            "type": "access"
        }
        refresh_payload = {
            "sub": cliente.id,
            "exp": now + timedelta(seconds=JWT_REFRESH_DELTA),
            "iat": now,
            "type": "refresh"
        }
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({"access_token": access_token, "refresh_token": refresh_token})

# Refresh token endpoint
@bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.json
    refresh_token = data.get("refresh_token")
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload["type"] != "refresh":
            return jsonify({"error": "Token inválido"}), 401
        cliente_id = payload["sub"]
        now = datetime.utcnow()
        access_payload = {
            "sub": cliente_id,
            "exp": now + timedelta(seconds=JWT_EXP_DELTA),
            "iat": now,
            "type": "access"
        }
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return jsonify({"access_token": access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401


from contextlib import contextmanager
@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

# Registro de cliente: usuario debe ser único (sin importar correo/status)
@bp.route("/clientes", methods=["POST"])
def registrar_cliente():
    data = request.json
    with get_session() as session:
        if session.query(Cliente).filter_by(usuario=data["usuario"]).first():
            return jsonify({"error": "Usuario ya existe"}), 400
        cliente = Cliente(
            nombre_completo=data["nombre_completo"],
            usuario=data["usuario"],
            correo=data["correo"],
            contrasena=generate_password_hash(data["contrasena"])
        )
        session.add(cliente)
        session.commit()
        return jsonify({"id": cliente.id}), 201


# Solo se puede modificar nombre completo y correo
@bp.route("/clientes/<int:id>", methods=["PUT"])
@token_required
def modificar_cliente(id):
    data = request.json
    with get_session() as session:
        cliente = session.get(Cliente, id)
        if not cliente or not cliente.activo:
            return jsonify({"error": "Cliente no encontrado"}), 404
        if "nombre_completo" in data:
            cliente.nombre_completo = data["nombre_completo"]
        if "correo" in data:
            cliente.correo = data["correo"]
        session.commit()
        return jsonify({"msg": "Datos actualizados"})


# Baja cliente
@bp.route("/clientes/<int:id>", methods=["DELETE"])
@token_required
def baja_cliente(id):
    with get_session() as session:
        cliente = session.get(Cliente, id)
        if not cliente or not cliente.activo:
            return jsonify({"error": "Cliente no encontrado"}), 404
        cliente.activo = False
        session.commit()
        return jsonify({"msg": "Cliente dado de baja"})


# Modificar contraseña (endpoint propio)
@bp.route("/clientes/<int:id>/password", methods=["PUT"])
@token_required
def actualizar_password(id):
    data = request.json
    with get_session() as session:
        cliente = session.get(Cliente, id)
        if not cliente or not cliente.activo:
            return jsonify({"error": "Cliente no encontrado"}), 404
        # Regla: la nueva contraseña debe ser diferente a la anterior
        if check_password_hash(cliente.contrasena, data["contrasena"]):
            return jsonify({"error": "La nueva contraseña debe ser diferente a la anterior"}), 400
        cliente.contrasena = generate_password_hash(data["contrasena"])
        session.commit()
        return jsonify({"msg": "Contraseña actualizada"})

# Crear proyecto
@bp.route("/proyectos", methods=["POST"])
def crear_proyecto():
    data = request.json
    with get_session() as session:
        proyecto = Proyecto(
            nombre_completo=data["nombre_completo"],
            nombre_corto=data["nombre_corto"],
            descripcion=data.get("descripcion", ""),
            cliente_id=data["cliente_id"]
        )
        session.add(proyecto)
        session.commit()
        return jsonify({"id": proyecto.id}), 201

# Cancelar proyecto
@bp.route("/proyectos/<int:id>/cancelar", methods=["PUT"])
def cancelar_proyecto(id):
    with get_session() as session:
        proyecto = session.get(Proyecto, id)
        if not proyecto or proyecto.estado != "activo":
            return jsonify({"error": "Proyecto no encontrado o no activo"}), 404
        proyecto.estado = "cancelado"
        session.commit()
        return jsonify({"msg": "Proyecto cancelado"})

# Eliminar proyecto
@bp.route("/proyectos/<int:id>", methods=["DELETE"])
def eliminar_proyecto(id):
    with get_session() as session:
        proyecto = session.get(Proyecto, id)
        if not proyecto:
            return jsonify({"error": "Proyecto no encontrado"}), 404
        session.delete(proyecto)
        session.commit()
        return jsonify({"msg": "Proyecto eliminado"})

# Listar proyectos de un cliente
@bp.route("/clientes/<int:id>/proyectos", methods=["GET"])
def listar_proyectos_cliente(id):
    with get_session() as session:
        proyectos = session.query(Proyecto).filter_by(cliente_id=id).all()
        return jsonify([
            {
                "id": p.id,
                "nombre_completo": p.nombre_completo,
                "nombre_corto": p.nombre_corto,
                "descripcion": p.descripcion,
                "estado": p.estado
            } for p in proyectos
        ])
