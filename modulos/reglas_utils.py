import mysql.connector
from modulos.conexion import obtener_conexion


def obtener_reglas():
    """
    Devuelve un diccionario con TODAS las reglas internas.
    Si no existen, devuelve None.
    """

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM reglas_internas ORDER BY id_regla DESC LIMIT 1")
    row = cur.fetchone()

    if not row:
        return None

    reglas = {
        "ahorro_minimo": float(row.get("ahorro_minimo", 0)),
        "prestamo_maximo": float(row.get("prestamo_maximo", 0)),
        "interes_por_10": float(row.get("interes_por_10", 0)),
        "plazo_maximo": int(row.get("plazo_maximo", 0)),
        "multa_inasistencia": float(row.get("multa_inasistencia", 0)),
        "multa_mora": float(row.get("multa_mora", 0)),
        "permisos_validos": row.get("permisos_validos", "enfermedad, trabajo, maternidad")
    }

    cur.close()
    con.close()
    return reglas
