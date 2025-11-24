import streamlit as st
from decimal import Decimal
from datetime import date, timedelta
from modulos.conexion import obtener_conexion


# ================================================================
# 🟢 1. OBTENER ÚLTIMO DÍA CERRADO
# ================================================================
def obtener_ultimo_dia_cerrado():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, saldo_final
        FROM caja_reunion
        WHERE dia_cerrado = 1
        ORDER BY fecha DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    con.close()
    return row   # Puede ser None si nunca han cerrado un día



# ================================================================
# 🟢 2. OBTENER O CREAR REUNIÓN (YA CORREGIDO)
#    → SI NO EXISTE, CREA AUTOMÁTICAMENTE
#    → SALDO INICIAL = SALDO FINAL DEL DÍA ANTERIOR
# ================================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Verificar si ya existe la reunión del día
    cursor.execute("""
        SELECT id_caja
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        con.close()
        return reunion["id_caja"]

    # Si NO existe → obtener último día cerrado
    ultimo = obtener_ultimo_dia_cerrado()

    if ultimo:
        saldo_inicial = Decimal(str(ultimo["saldo_final"]))
    else:
        # Si es el primer día del sistema
        saldo_inicial = Decimal("0.00")

    # Crear la nueva reunión
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final, dia_cerrado)
        VALUES (%s, %s, 0, 0, %s, 0)
    """, (fecha, saldo_inicial, saldo_inicial))

    con.commit()
    new_id = cursor.lastrowid
    con.close()
    return new_id



# ================================================================
# 🟢 3. OBTENER SALDO REAL (TABLA caja_general)
# ================================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()
    con.close()

    if not row:
        return Decimal("0.00")

    return Decimal(str(row["saldo_actual"]))



# ================================================================
# 🟢 4. REGISTRAR MOVIMIENTO (Ingreso / Egreso)
# ================================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # Registrar movimiento histórico
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # Obtener saldo real actual
    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    saldo_real = Decimal(str(cursor.fetchone()["saldo_actual"]))

    if tipo == "Ingreso":
        saldo_real += monto
    else:
        saldo_real -= monto

    # Guardar saldo real
    cursor.execute("""
        UPDATE caja_general
        SET saldo_actual = %s
        WHERE id = 1
    """, (saldo_real,))

    # Actualizar reunión
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
    con.close()



# ================================================================
# 🟢 5. OBTENER REPORTE DE UN DÍA
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
    """, (fecha,))

    rows = cursor.fetchall()
    con.close()
    return rows
