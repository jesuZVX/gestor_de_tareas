from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from enum import Enum as PyEnum
from datetime import datetime

DATABASE_URL = "sqlite:///gestion_tareas.sqlite"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RolUsuario(PyEnum):
    admin = "admin"
    colaborador = "colaborador"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nombre_usuario = Column(String, unique=True, nullable=False)
    documento = Column(String, unique=True, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.colaborador)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Integer, default=1)

    proyectos = relationship("Proyecto", back_populates="creador")
    tareas = relationship("Tarea", back_populates="asignado")
    notificaciones = relationship("Notificacion", back_populates="usuario")

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(String, default="activo")
    id_usuario_creador = Column(Integer, ForeignKey("usuarios.id"))

    creador = relationship("Usuario", back_populates="proyectos")
    tareas = relationship("Tarea", back_populates="proyecto")

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    fecha_vencimiento = Column(Date)
    prioridad = Column(String)
    estado = Column(String, default="pendiente")
    id_proyecto = Column(Integer, ForeignKey("proyectos.id"))
    id_usuario_asignado = Column(Integer, ForeignKey("usuarios.id"))
    ruta_archivo = Column(String(255))

    proyecto = relationship("Proyecto", back_populates="tareas")
    asignado = relationship("Usuario", back_populates="tareas")

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    mensaje = Column(Text, nullable=False)
    leido = Column(Integer, default=0)
    fecha = Column(DateTime, default=datetime.utcnow)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="notificaciones")

def init_db():
    Base.metadata.create_all(bind=engine)
