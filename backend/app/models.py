from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(128), nullable=False)
    usuario = Column(String(64), unique=True, nullable=False)
    correo = Column(String(128), unique=True, nullable=False)
    contrasena = Column(String(256), nullable=False)  # Hasheada
    activo = Column(Boolean, default=True)
    proyectos = relationship("Proyecto", back_populates="cliente")

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(128), nullable=False)
    nombre_corto = Column(String(32), nullable=False)
    descripcion = Column(Text, nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estado = Column(String(32), default="activo")  # activo, cancelado, eliminado
    cliente = relationship("Cliente", back_populates="proyectos")
