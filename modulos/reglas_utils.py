from modulos.conexion import obtener_conexion

def obtener_reglas():
    """
    Obtiene la única fila existente de reglas internas.
    La tabla debe tener solo un registro vigente.
    Devuelve un diccionario con todas las columnas.
    """
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    reglas = cursor.fetchone()

    cursor.close()
    con.close()
    return reglas


