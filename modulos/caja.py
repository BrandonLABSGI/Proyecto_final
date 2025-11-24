import streamlit as st
from decimal import Decimal
from datetime import date
from modulos.conexion import obtener_conexion


# ================================================================
# 🟢 1. OBTENER O CREAR REUNIÓN DEL DÍA
#    — Opción A: usar saldo_final del día anterior SIEMPRE
# ================================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------
    # ¿Ya existe una reunión hoy?
    # --------------------------------------------
    cursor.execute("""
        SELECT id_caja
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["id_caja"]

    # --------------------------------------------
    # Buscar día inmediatamente anterior cerrado
    # --------------------------------------------
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s AND dia_cerrado = 1
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))

    row = cursor.fetchone()

    # Si no hay días cerrados, saldo inicial = 0
    saldo_inicial = Decimal(str(row["saldo_final"])) if row else Decimal("0.00")

    # --------------------------------------------
    # Crear la nueva reunión
    # --------------------------------------------
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final, dia_cerrado)
        VALUES (%s, %s, 0, 0, %s, 0)
    """, (fecha, saldo_inicial, saldo_inicial))

    con.commit()
    return cursor.lastrowid



# ================================================================
# 🟢 2. OBTENER SALDO ACTUAL (de caja_general)
# ================================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()

    if not row:
        return Decimal("0.00")

    return Decimal(str(row["saldo_actual"]))



# ================================================================
# 🟢 3. REGISTRAR MOVIMIENTO (Ingreso/Egreso)
# ================================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # -------------------------
    # Registrar movimiento
    # -------------------------
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # -------------------------
    # Obtener saldo actual
    # -------------------------
    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()
    saldo = Decimal(str(row["saldo_actual"]))

    # -------------------------
    # Actualizar saldo real
    # -------------------------
    if tipo == "Ingreso":
        saldo += monto
    else:
        saldo -= monto

    cursor.execute("""
        UPDATE caja_general
        SET saldo_actual = %s
        WHERE id = 1
    """, (saldo,))

    # -------------------------
    # Actualizar datos de reunión
    # -------------------------
    if tipo == "Ingreso":
        cursor.execute("""
            UPDATE caja_reunion
            SET ingresos = ingresos + %s,
                saldo_final = saldo_final + %s
            WHERE id_caja = %s
        """, (monto, monto, id_caja))
    else:
        cursor.execute("""
            UPDATE caja_reunion
            SET egresos = egresos + %s,
                saldo_final = saldo_final - %s
            WHERE id_caja = %s
        """, (monto, monto, id_caja))

    con.commit()



# ================================================================
# 🟢 4. OBTENER REPORTE POR FECHA
# ================================================================
def obtener_reporte_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    row = cursor.fetchone()

    if not row:
        return {
            "ingresos": Decimal("0.00"),
            "egresos": Decimal("0.00"),
            "balance": Decimal("0.00"),
            "saldo_final": Decimal("0.00"),
        }

    ingresos = Decimal(str(row["ingresos"]))
    egresos = Decimal(str(row["egresos"]))
    saldo_final = Decimal(str(row["saldo_final"]))

    return {
        "ingresos": ingresos,
        "egresos": egresos,
        "balance": ingresos - egresos,
        "saldo_final": saldo_final,
    }



# ================================================================
# 🟢 5. OBTENER MOVIMIENTOS POR FECHA
# ================================================================
def obtener_movimientos_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos cm
        JOIN caja_reunion cr ON cm.id_caja = cr.id_caja
        WHERE cr.fecha = %s
    """, (fecha,))

    return cursor.fetchall()
