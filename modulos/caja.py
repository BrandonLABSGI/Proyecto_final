import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# Crear o recuperar la caja del día
# ---------------------------------------------------------
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        # 1. Verificar si ya existe caja en esa fecha
        cursor.execute("SELECT * FROM Caja WHERE Fecha = %s", (fecha,))
        fila = cursor.fetchone()

        if fila:
            return fila["Id_Caja"]

        # 2. Obtener saldo final anterior
        cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Fecha DESC LIMIT 1")
        ultimo = cursor.fetchone()
        saldo_anterior = ultimo["Saldo_actual"] if ultimo else 0

        # 3. Crear registro nuevo
        cursor.execute("""
            INSERT INTO Caja (Concepto, Monto, Saldo_actual, Fecha)
            VALUES ('Saldo inicial del día', 0, %s, %s)
        """, (saldo_anterior, fecha))

        con.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        con.close()



# ---------------------------------------------------------
# Registrar un movimiento en caja
# ---------------------------------------------------------
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        # Obtener saldo actual
        cursor.execute("SELECT Saldo_actual FROM Caja WHERE Id_Caja = %s", (id_caja,))
        fila = cursor.fetchone()

        if not fila:
            return False

        saldo_actual = fila["Saldo_actual"]

        # Calcular nuevo saldo
        if tipo == "Ingreso":
            nuevo_saldo = saldo_actual + monto
        else:
            nuevo_saldo = saldo_actual - monto

        # Insertar movimiento en tabla Caja
        cursor.execute("""
            INSERT INTO Caja (Concepto, Monto, Saldo_actual, Fecha)
            VALUES (%s, %s, %s, CURDATE())
        """, (categoria, monto if tipo=="Ingreso" else -monto, nuevo_saldo))

        con.commit()
        return True

    finally:
        cursor.close()
        con.close()



# ---------------------------------------------------------
# Obtener saldo actual (último registro)
# ---------------------------------------------------------
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor()

    try:
        cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Fecha DESC, Id_Caja DESC LIMIT 1")
        fila = cursor.fetchone()
        return fila[0] if fila else 0
    finally:
        cursor.close()
        con.close()



# ---------------------------------------------------------
# Obtener saldo por fecha
# ---------------------------------------------------------
def obtener_saldo_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor()

    try:
        cursor.execute("""
            SELECT Saldo_actual
            FROM Caja
            WHERE Fecha = %s
            ORDER BY Id_Caja DESC LIMIT 1
        """, (fecha,))

        fila = cursor.fetchone()
        return fila[0] if fila else 0

    finally:
        cursor.close()
        con.close()



# ---------------------------------------------------------
# Mostrar reporte general de caja (opcional)
# ---------------------------------------------------------
def mostrar_reporte_caja():
    st.subheader("📊 Reporte de Caja")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Caja ORDER BY Fecha DESC, Id_Caja DESC")
        filas = cursor.fetchall()

        if not filas:
            st.info("No hay movimientos registrados.")
            return

        st.dataframe(filas)

    finally:
        cursor.close()
        con.close()
