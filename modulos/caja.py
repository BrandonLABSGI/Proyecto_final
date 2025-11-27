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

    return None


# ================================================================
# 🟢 2. OBTENER O CREAR REUNIÓN
# ================================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Si ya existe, devolver id_caja
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        cursor.close()
        con.close()
        return reunion["id_caja"]

    # Buscar saldo anterior
    saldo_anterior = obtener_saldo_dia_anterior(fecha)

    if saldo_anterior is not None:
        saldo_inicial = saldo_anterior
    else:
        cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        row = cursor.fetchone()
        saldo_inicial = Decimal(str(row["saldo_actual"])) if row else Decimal("0.00")

    # Crear reunión
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
# 🟢 4. REGISTRAR MOVIMIENTO — **VERSIÓN FINAL FUNCIONAL**
# ================================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Normalizar tipo
    tipo_normalizado = tipo.strip().capitalize()
    monto = Decimal(str(monto))

    # Guardar en caja_movimientos
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo_normalizado, categoria, monto))

    # Obtener saldo_general actual
    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()
    saldo_general = Decimal(str(row["saldo_actual"]))

    # Ajuste de saldo_general
    if tipo_normalizado == "Ingreso":
        saldo_general += monto
    else:
        saldo_general -= monto

    cursor.execute("""
        UPDATE caja_general
        SET saldo_actual = %s
        WHERE id = 1
    """, (saldo_general,))

    # ============================================================
    # 🔥 ACTUALIZACIÓN DEL REGISTRO DEL DÍA (caja_reunion)
    # ============================================================
    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    row = cursor.fetchone()

    saldo_inicial = Decimal(str(row["saldo_inicial"]))
    ingresos_prev = Decimal(str(row["ingresos"]))
    egresos_prev = Decimal(str(row["egresos"]))

    # Recalcular el saldo actual de la reunión
    saldo_actual_reunion = saldo_inicial + ingresos_prev - egresos_prev

    # Aplicar el nuevo movimiento
    if tipo_normalizado == "Ingreso":
        ingresos_prev += monto
        saldo_actual_reunion += monto

        cursor.execute("""
            UPDATE caja_reunion
            SET ingresos = %s, saldo_final = %s
            WHERE id_caja = %s
        """, (ingresos_prev, saldo_actual_reunion, id_caja))

    else:
        egresos_prev += monto
        saldo_actual_reunion -= monto

        cursor.execute("""
            UPDATE caja_reunion
            SET egresos = %s, saldo_final = %s
            WHERE id_caja = %s
        """, (egresos_prev, saldo_actual_reunion, id_caja))

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

    return {
        "ingresos": Decimal(str(row["ingresos"])),
        "egresos": Decimal(str(row["egresos"])),
        "saldo_final": Decimal(str(row["saldo_final"])),
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
        ORDER BY id_mov ASC
    """, (fecha,))

    rows = cursor.fetchall()

    cursor.close()
    con.close()

    return rows
