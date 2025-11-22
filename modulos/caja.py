import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion


# =====================================================
# OBTENER O CREAR REUNIÓN
# =====================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Verificar si existe reunión
    cursor.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        cursor.close()
        con.close()
        return reunion["id_caja"]

    # Obtener último saldo final existente
    cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
    ultimo = cursor.fetchone()
    saldo_anterior = Decimal(str(ultimo["saldo_final"])) if ultimo else Decimal("0.00")

    # Crear nueva reunión heredando saldo anterior
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_anterior, saldo_anterior))

    con.commit()
    nuevo_id = cursor.lastrowid

    cursor.close()
    con.close()
    return nuevo_id


# =====================================================
# OBTENER SALDO POR FECHA
# =====================================================
def obtener_saldo_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar reunión exacta
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        saldo = Decimal(str(reunion["saldo_final"]))
        cursor.close()
        con.close()
        return saldo

    # Si no existe, tomar última reunión anterior
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    cursor.close()
    con.close()

    return Decimal(str(anterior["saldo_final"])) if anterior else Decimal("0.00")


# =====================================================
# REGISTRAR MOVIMIENTO (INGRESO / EGRESO)
# =====================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # Obtener datos actuales de esa reunión
    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    reunion = cursor.fetchone()

    if not reunion:
        cursor.close()
        con.close()
        return

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # Actualizar ingresos o egresos
    if tipo == "Ingreso":
        ingresos += monto
    else:
        egresos += monto

    # Calcular nuevo saldo
    saldo_final = saldo_inicial + ingresos - egresos

    # Actualizar tabla caja_reunion
    cursor.execute("""
        UPDATE caja_reunion
        SET ingresos = %s, egresos = %s, saldo_final = %s
        WHERE id_caja = %s
    """, (ingresos, egresos, saldo_final, id_caja))

    con.commit()

    cursor.close()
    con.close()
