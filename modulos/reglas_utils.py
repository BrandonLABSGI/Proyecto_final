import mysql.connector
from modulos.conexion import obtener_conexion

def obtener_reglas():
    """
    Devuelve un diccionario con todas las reglas internas existentes.
    Siempre toma la primera fila porque la tabla solo guarda una regla activa.
    """
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    reglas = cursor.fetchone()

    cursor.close()
    con.close()
    return reglas

