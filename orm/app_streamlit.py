import streamlit as st
from sqlalchemy.orm import sessionmaker
from clases import engine, Continente, Pais, Jugador

# Configuración de la sesión (usando el engine de clases.py)
Session = sessionmaker(bind=engine)
session = Session()

# Título principal de la aplicación
st.set_page_config(layout="wide")
st.title("Sistema de Visualización de Jugadores de Fútbol")
st.markdown("---")

# =========================================================
# TABLA 1: INFORMACIÓN DETALLADA DE JUGADORES
# =========================================================
st.header("1. Listado Detallado de Jugadores")

# Consultamos todos los jugadores
# Nota: Usamos las relaciones para obtener nombres de países y continentes
jugadores = session.query(Jugador).all()
lista_jugadores = []

for j in jugadores:
    # Obtenemos el nombre del continente a través del país de nacimiento
    nombre_continente = j.pais_nacimiento.continente.nombre
    
    diccionario = {
        "Nombre Jugador": j.nombre,
        "País Nacimiento": j.pais_nacimiento.nombre,
        "País Donde Juega": j.pais_juego.nombre,
        "Posición": j.posicion,
        "Edad": j.edad,
        "Partidos Selección": j.partidos_seleccion,
        "Goles Selección": j.goles,
        "Continente": nombre_continente
    }
    lista_jugadores.append(diccionario)

# Mostramos la tabla detallada
st.dataframe(lista_jugadores, use_container_width=True)
st.markdown("---")


# =========================================================
# TABLA 2: ESTADÍSTICAS POR CONTINENTE
# =========================================================
st.header("2. Resumen por Continente")

continentes = session.query(Continente).all()
lista_continentes = []

for c in continentes:
    # Calculamos agregaciones manualmente recorriendo la relación
    # continente -> países -> jugadores nacidos ahí
    total_jugadores = 0
    total_goles = 0
    
    for p in c.paises:
        # Contamos jugadores cuya relación 'pais_nacimiento' coincide con el país p
        # En el ORM esto se puede acceder via p.jugadores si back_populates está definido
        # o mediante una subconsulta. Aquí lo haremos simple:
        jugadores_pais = session.query(Jugador).filter_by(pais_nac_id=p.id).all()
        
        total_jugadores += len(jugadores_pais)
        total_goles += sum(jug.goles for jug in jugadores_pais)

    lista_continentes.append({
        "Continente": c.nombre,
        "Número de Jugadores": total_jugadores,
        "Total Goles": total_goles
    })

st.dataframe(lista_continentes, use_container_width=True)
st.markdown("---")


# =========================================================
# TABLA 3: ESTADÍSTICAS POR PAÍS
# =========================================================
st.header("3. Resumen por País (Nacimiento)")

paises = session.query(Pais).all()
lista_paises = []

for p in paises:
    # Filtramos jugadores que nacieron en este país
    jugadores_nacidos = session.query(Jugador).filter_by(pais_nac_id=p.id).all()
    
    lista_paises.append({
        "País": p.nombre,
        "Número de Jugadores": len(jugadores_nacidos),
        "Total Goles Selección": sum(jug.goles for jug in jugadores_nacidos)
    })

# Ordenamos la lista por número de jugadores de forma descendente para mejor visualización
lista_paises = sorted(lista_paises, key=lambda x: x['Número de Jugadores'], reverse=True)

st.dataframe(lista_paises, use_container_width=True)

# Cerrar la sesión
session.close()