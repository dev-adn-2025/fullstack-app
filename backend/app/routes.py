
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from .models import Cliente, Proyecto, Base
from sqlalchemy import create_engine
import os

# API versioning
bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/appdb")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

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
