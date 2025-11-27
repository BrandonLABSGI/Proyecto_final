import streamlit as st
from decimal import Decimal
from datetime import date
from modulos.conexion import obtener_conexion


# ================================================================
# 🔹 1. OBTENER SALDO DEL DÍA ANTERIOR
# ================================================================
def obtener_saldo_dia_anterior(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT saldo_final 
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    row = cursor.fetchone()
    con.close()

    if row:
        return Decimal(str(row["saldo_final"]))

    return None


# ================================================================
# 🔹 2. ACTUALIZAR SALDO INICIAL DEL DÍA SIGUIENTE
# ================================================================
def actualizar_saldo_inicial_dia_siguiente(fecha, saldo_final):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_caja
        FROM caja_reunion
        WHERE fecha > %s
        ORDER BY fecha ASC
        LIMIT 1
    """, (fecha,))
    row = cursor.fetchone()

    if row:  # Existe un día siguiente creado antes
        id_caja = row["id_caja"]

        cursor.execute("""
            UPDATE caja_reunion
            SET saldo_inicial = %s,
                saldo_final = %s
            WHERE id_caja = %s
        """, (saldo_final, saldo_final, id_caja))

        con.commit()

    con.close()


# ================================================================
# 🔹 3. OBTENER O CREAR REUNIÓN — AHORA 100% CORRECTO
# ================================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ¿Ya existe reunión?
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["id_caja"]

    # Buscar saldo final del día anterior
    saldo_anterior = obtener_saldo_dia_anterior(fecha)

    if saldo_anterior is not None:
        saldo_inicial = saldo_anterior
    else:
        cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        row = cursor.fetchone()
        saldo_inicial = Decimal(str(row["saldo_actual"])) if row else Decimal("0.00")

    # Crear nueva reunión
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_inicial, saldo_inicial))
    con.commit()

    return cursor.lastrowid


# ================================================================
# 🔹 4. SALDO REAL GENERAL
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
# 🔹 5. REGISTRAR MOVIMIENTO (INGRESO/EGRESO)
# ================================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # Ajustar saldo real general
    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()
    saldo_general = Decimal(str(row["saldo_actual"]))

    if tipo == "Ingreso":
        saldo_general += monto
    else:
        saldo_general -= monto

    cursor.execute("""
        UPDATE caja_general
        SET saldo_actual = %s
        WHERE id = 1
    """, (saldo_general,))

    # Actualizar caja por reunión
    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos 
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    row = cursor.fetchone()

    saldo_reunion = (
        Decimal(str(row["saldo_inicial"]))
        + Decimal(str(row["ingresos"]))
        - Decimal(str(row["egresos"]))
    )

    if tipo == "Ingreso":
        saldo_reunion += monto
        cursor.execute("""
            UPDATE caja_reunion
            SET ingresos = ingresos + %s,
                saldo_final = %s
            WHERE id_caja = %s
        """, (monto, saldo_reunion, id_caja))
    else:
        saldo_reunion -= monto
        cursor.execute("""
            UPDATE caja_reunion
            SET egresos = egresos + %s,
                saldo_final = %s
            WHERE id_caja = %s
        """, (monto, saldo_reunion, id_caja))

    con.commit()
    con.close()


# ================================================================
# 🔹 6. REPORTE POR FECHA
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
            "saldo_final": Decimal("0.00"),
        }

    return {
        "ingresos": Decimal(str(row["ingresos"])),
        "egresos": Decimal(str(row["egresos"])),
        "saldo_final": Decimal(str(row["saldo_final"])),
    }


# ================================================================
# 🔹 7. MOVIMIENTOS POR FECHA
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
