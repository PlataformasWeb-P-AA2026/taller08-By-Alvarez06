import csv
from sqlalchemy.orm import sessionmaker
from clases import engine, Continente, Pais, Jugador

# Configuración de la sesión
Session = sessionmaker(bind=engine)
session = Session()

# Diccionario de apoyo (ya que el CSV no tiene la columna continente)
MAPEO_CONTINENTES = {
    "Alemania":      "Europa",
    "Argentina":     "América del Sur",
    "Australia":     "Oceanía",
    "Brasil":        "América del Sur",
    "Ecuador":       "América del Sur",
    "España":        "Europa",
    "Estados Unidos":"América del Norte",
    "Francia":       "Europa",
    "Inglaterra":    "Europa",
    "Japón":         "Asia",
    "Marruecos":     "África",
    "México":        "América del Norte",
    "Nigeria":       "África",
    "Portugal":      "Europa",
    "Senegal":       "África",
}

try:
    print("Iniciando la lectura del CSV...")
    
    # Leer todos los datos a la memoria para procesarlos en fases
    datos_csv = []
    with open('../data/jugadores_futbol.csv', mode='r', encoding='utf-8-sig') as f:
        lector = csv.DictReader(f, delimiter=',')
        for fila in lector:
            datos_csv.append(fila)

    print("Archivo leído correctamente. Iniciando migración en 3 fases...\n")

    # ==========================================
    # FASE 1: POBLAR CONTINENTES
    # ==========================================
    print("Fase 1: Insertando Continentes...")
    # Extraemos los continentes únicos de nuestro diccionario más un 'Desconocido' por defecto
    continentes_unicos = set(MAPEO_CONTINENTES.values())
    continentes_unicos.add('Desconocido')

    for nom_continente in continentes_unicos:
        # Verificamos si ya existe antes de insertarlo
        if not session.query(Continente).filter_by(nombre=nom_continente).first():
            session.add(Continente(nombre=nom_continente))
    
    # Guardamos los continentes para que tengan un ID asignado en la BD
    session.commit()
    print(" -> Continentes guardados.\n")


    # ==========================================
    # FASE 2: POBLAR PAÍSES
    # ==========================================
    print("Fase 2: Insertando Países...")
    paises_unicos = set()
    
    # Recorremos el CSV en memoria para extraer todos los nombres de países sin repetir
    for fila in datos_csv:
        paises_unicos.add(fila['pais_nacimiento'].strip())
        paises_unicos.add(fila['pais_donde_juega'].strip())
        
    for nom_pais in paises_unicos:
        if not session.query(Pais).filter_by(nombre=nom_pais).first():
            nom_continente = MAPEO_CONTINENTES.get(nom_pais, 'Desconocido')
            
            # CONSULTA QUERY: Obtenemos el objeto Continente correspondiente
            continente_obj = session.query(Continente).filter_by(nombre=nom_continente).first()
            
            # Creamos el país asignando el objeto continente
            session.add(Pais(nombre=nom_pais, continente=continente_obj))
            
    # Guardamos los países para que tengan un ID asignado en la BD
    session.commit()
    print(" -> Países guardados.\n")


    # ==========================================
    # FASE 3: POBLAR JUGADORES
    # ==========================================
    print("Fase 3: Insertando Jugadores...")
    for fila in datos_csv:
        nom_pais_nac = fila['pais_nacimiento'].strip()
        nom_pais_juega = fila['pais_donde_juega'].strip()
        
        # CONSULTAS QUERY: Obtenemos los objetos País correspondientes
        obj_pais_nacimiento = session.query(Pais).filter_by(nombre=nom_pais_nac).first()
        obj_pais_juego = session.query(Pais).filter_by(nombre=nom_pais_juega).first()
        
        # Creamos el jugador asignando los objetos obtenidos de las consultas
        jugador_obj = Jugador(
            nombre=fila['nombre_jugador'].strip(),
            posicion=fila['posicion'].strip(),
            edad=int(fila['edad']),
            partidos_seleccion=int(fila['numero_partidos_seleccion']),
            goles=int(fila['goles_seleccion']),
            pais_nacimiento=obj_pais_nacimiento,
            pais_juego=obj_pais_juego
        )
        session.add(jugador_obj)

    # Guardado final de todos los jugadores
    session.commit()
    print(" -> Jugadores guardados.\n")

    print("[ÉXITO] Toda la base de datos ha sido poblada correctamente mediante inserción en cascada.")

except FileNotFoundError:
    print("\n[ERROR]: No se encontró el archivo 'jugadores_futbol.csv'.")
except ValueError as val_err:
    session.rollback()
    print(f"\n[ERROR]: Problema convirtiendo números (revisa edad, goles o partidos): {val_err}")
except Exception as e:
    session.rollback()
    print(f"\n[ERROR]: Ocurrió un error inesperado durante la migración: {e}")
finally:
    session.close()