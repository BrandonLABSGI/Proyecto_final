import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        # coloca tu contraseña si tienes
        database="btfcfbzptdyxq4f8afmu"  # nombre exacto de tu BD
    )

