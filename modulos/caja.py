import streamlit as st
from decimal import Decimal
from datetime import date
from modulos.conexion import obtener_conexion


# ================================================================
# 🟢 1. OBTENER SALDO FINAL DEL DÍA ANTERIOR
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

    cursor.close()
    con.close()

    if row:
        return Decimal(str(row["saldo_final"]))

    return None  # No existe día anterior


# ================================================================
# 🟢 2. OBTENER O CREAR REUNIÓN — *ARREGLO DEFINITIVO*
# ================================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Ver si ya existe
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        cursor.close()
        con.close()
        return reunion["id_caja"]

    # Buscar saldo del día anterior
    saldo_anterior = obtener_saldo_dia_anterior(fecha)

    if saldo_anterior is not None:
        saldo_inicial = saldo_anterior
    else:
        # Primer día del sistema → usar saldo_actual de caja_general
        cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        row = cursor.fetchone()
        saldo_inicial = Decimal(str(row["saldo_actual"])) if row else Decimal("0.00")

    # Crear nueva reunión
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_inicial, saldo_inicial))

    con.commit()

    last_id = cursor.lastrowid

    cursor.close()
    con.close()

    return last_id


# ================================================================
# 🟢 3. OBTENER SALDO REAL
# ================================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()

    cursor.close()
    con.close()

    if not row:
        return Decimal("0.00")

    return Decimal(str(row["saldo_actual"]))


# ================================================================
# 🟢 4. REGISTRAR MOVIMIENTO — CORREGIDO DEFINITIVO
# ================================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Normalizar tipo (CORRECCIÓN CLAVE)
    tipo = tipo.strip().lower()

    monto = Decimal(str(monto))

    # Registrar movimiento histórico
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo.capitalize(), categoria, monto))

    # Obtener saldo actual general
    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()
    saldo = Decimal(str(row["saldo_actual"]))

    # Ajustar saldo real
    if tipo == "ingreso":
        saldo += monto
    else:
        saldo -= monto

    cursor.execute("""
        UPDATE caja_general
        SET saldo_actual = %s
        WHERE id = 1
    """, (saldo,))

    # ========================================================
    # CALCULAR SALDO REAL DE LA REUNIÓN (SIN CAMBIAR TU LÓGICA)
    # ========================================================
    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos 
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    row = cursor.fetchone()

    saldo_inicial = Decimal(str(row["saldo_inicial"]))
    ingresos_prev = Decimal(str(row["ingresos"]))
    egresos_prev = Decimal(str(row["egresos"]))

    saldo_actual_reunion = saldo_inicial + ingresos_prev - egresos_prev

    # AJUSTAR POR EL NUEVO MOVIMIENTO
    if tipo == "ingreso":
        saldo_actual_reunion += monto
        cursor.execute("""
            UPDATE caja_reunion
            SET ingresos = ingresos + %s,
                saldo_final = %s
            WHERE id_caja = %s
        """, (monto, saldo_actual_reunion, id_caja))
    else:
        saldo_actual_reunion -= monto
        cursor.execute("""
            UPDATE caja_reunion
            SET egresos = egresos + %s,
                saldo_final = %s
            WHERE id_caja = %s
        """, (monto, saldo_actual_reunion, id_caja))

    con.commit()

    cursor.close()
    con.close()


# ================================================================
# 🟢 5. OBTENER REPORTE POR FECHA
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

    cursor.close()
    con.close()

    if not row:
        return {
            "ingresos": Decimal("0.00"),
            "egresos": Decimal("0.00"),
            "saldo_final": Decimal("0.00"),
        }

    ingresos = Decimal(str(row["ingresos"]))
    egresos = Decimal(str(row["egresos"]))
    saldo_final = Decimal(str(row["saldo_final"]))

    return {
        "ingresos": ingresos,
        "egresos": egresos,
        "saldo_final": saldo_final,
    }


# ================================================================
# 🟢 6. OBTENER MOVIMIENTOS POR FECHA
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

    rows = cursor.fetchall()

    cursor.close()
    con.close()

    return rows
