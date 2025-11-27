import mysql.connector
from decimal import Decimal
from modulos.conexion import obtener_conexion


# ============================================================
# OBTENER SALDO ACTUAL (última reunión)
# ============================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        ORDER BY fecha DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    return float(row[0]) if row else 0.00


# ============================================================
# ASEGURAR REUNIÓN DEL DÍA
# Crea o repara la reunión para la fecha indicada
# ============================================================
def asegurar_reunion(fecha):

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ¿Existe la reunión de este día?
    cur.execute("SELECT * FROM caja_reunion WHERE fecha=%s", (fecha,))
    reunion = cur.fetchone()

    # Obtener saldo final anterior
    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cur.fetchone()

    saldo_inicial_correcto = Decimal(str(anterior["saldo_final"])) if anterior else Decimal("0.00")

    # --------------------------------------------------------
    # SI YA EXISTE LA REUNIÓN — REPARAR si está mala
    # --------------------------------------------------------
    if reunion:

        saldo_inicial_actual = Decimal(str(reunion["saldo_inicial"]))

        if saldo_inicial_actual != saldo_inicial_correcto:
            # Rehacer el saldo de este día
            ingresos = Decimal(str(reunion["ingresos"]))
            egresos = Decimal(str(reunion["egresos"]))
            saldo_final = saldo_inicial_correcto + ingresos - egresos

            cur.execute("""
                UPDATE caja_reunion
                SET saldo_inicial=%s,
                    saldo_final=%s
                WHERE id_caja=%s
            """, (saldo_inicial_correcto, saldo_final, reunion["id_caja"]))

            con.commit()

        return reunion["id_caja"]

    # --------------------------------------------------------
    # SI NO EXISTE — CREAR UNA NUEVA REUNIÓN
    # --------------------------------------------------------
    cur.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_inicial_correcto, saldo_inicial_correcto))

    con.commit()
    return cur.lastrowid


# ============================================================
# REGISTRAR MOVIMIENTO (Ingreso / Egreso)
# ============================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):

    monto = Decimal(str(monto))

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Obtener datos actuales
    cur.execute("SELECT * FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    reunion = cur.fetchone()

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # Aplicar movimiento
    if tipo == "Ingreso":
        ingresos += monto
    elif tipo == "Egreso":
        egresos += monto
    else:
        raise ValueError("Tipo inválido, use 'Ingreso' o 'Egreso'")

    # Recalcular saldo
    saldo_final = saldo_inicial + ingresos - egresos

    # Actualizar reunión
    cur.execute("""
        UPDATE caja_reunion
        SET ingresos=%s,
            egresos=%s,
            saldo_final=%s
        WHERE id_caja=%s
    """, (ingresos, egresos, saldo_final, id_caja))

    # Registrar movimiento
    cur.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    con.commit()
    return True
