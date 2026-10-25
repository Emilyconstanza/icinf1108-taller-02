from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_index=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Relación con otra entidad
    registros = relationship("Registro", back_populates="propietario")


class Registro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_index=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relación inversa
    propietario = relationship("Usuario", back_populates="registros")