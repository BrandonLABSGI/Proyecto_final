import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion


# =====================================================
#  OBTENER O CREAR REUNIÓN DE CAJA
# =====================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Verificar si existe una reunión con esa fecha
    cursor.execute("""
        SELECT id_caja
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["id_caja"]

    # Si no existe, obtener último saldo final
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        ORDER BY fecha DESC
        LIMIT 1
    """)
    ultimo = cursor.fetchone()

    saldo_anterior = Decimal(str(ultimo["saldo_final"])) if ultimo else Decimal("0.00")

    # Crear reunión nueva heredando el saldo final anterior
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_anterior, saldo_anterior))

    con.commit()
    return cursor.lastrowid



# =====================================================
#  OBTENER SALDO POR FECHA
# =====================================================
def obtener_saldo_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar saldo exacto para la fecha
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return Decimal(str(reunion["saldo_final"]))

    # Si no existe, recuperar el último saldo previo
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    return Decimal(str(anterior["saldo_final"])) if anterior else Decimal("0.00")



# =====================================================
#  REGISTRAR MOVIMIENTO (Ingreso / Egreso)
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
        return

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # Registrar movimiento en caja_movimientos
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # Actualizar ingresos o egresos según el tipo
    if tipo == "Ingreso":
        ingresos += monto
    else:
        egresos += monto

    # Recalcular saldo final
    saldo_final = saldo_inicial + ingresos - egresos

    cursor.execute("""
        UPDATE caja_reunion
        SET ingresos = %s,
            egresos = %s,
            saldo_final = %s
        WHERE id_caja = %s
    """, (ingresos, egresos, saldo_final, id_caja))

    con.commit()
