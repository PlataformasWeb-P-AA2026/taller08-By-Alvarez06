from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from config import cadena_base_datos

# Configuración de la conexión a SQLite
engine = create_engine(cadena_base_datos)
Base = declarative_base()

class Continente(Base):
    __tablename__ = 'continente'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    # Relación 1:N con Pais
    paises = relationship("Pais", back_populates="continente")

class Pais(Base):
    __tablename__ = 'pais'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    # Clave foránea y relación con Continente
    continente_id = Column(Integer, ForeignKey('continente.id'))
    continente = relationship("Continente", back_populates="paises")

class Jugador(Base):
    __tablename__ = 'jugador'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    posicion = Column(String(50))
    edad = Column(Integer)
    partidos_seleccion = Column(Integer)
    goles = Column(Integer)
    
    # Relación 1: País de Nacimiento
    pais_nac_id = Column(Integer, ForeignKey('pais.id'))
    pais_nacimiento = relationship("Pais", foreign_keys=[pais_nac_id])
    
    # Relación 2: País donde juega
    pais_juego_id = Column(Integer, ForeignKey('pais.id'))
    pais_juego = relationship("Pais", foreign_keys=[pais_juego_id])

# Generar las tablas en la base de datos
Base.metadata.create_all(engine)