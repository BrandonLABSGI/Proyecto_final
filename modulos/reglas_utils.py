from modulos.conexion import obtener_conexion

def obtener_reglas():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla DESC LIMIT 1")
    reglas = cursor.fetchone()

    cursor.close()
    con.close()

    return reglas
