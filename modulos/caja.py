import mysql.connector
from decimal import Decimal
from modulos.conexion import obtener_conexion


# ============================================================
# 🔵 OBTENER SALDO ACTUAL (desde caja_general, como TU sistema original)
# ============================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
    row = cursor.fetchone()

    return float(row[0]) if row else 0.00


# ============================================================
# 🟦 FUNCIÓN CENTRAL — ASEGURA QUE LA REUNIÓN EXISTA Y ESTÉ CORRECTA
# ============================================================
def asegurar_reunion(fecha):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar reunión del día
    cursor.execute("SELECT * FROM caja_reunion WHERE fecha=%s", (fecha,))
    reunion = cursor.fetchone()

    # Buscar reunión anterior
    cursor.execute("""
        SELECT saldo_final 
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    saldo_correcto = Decimal(str(anterior["saldo_final"])) if anterior else Decimal("0.00")

    # -------------------------------------------------------
    # 🔥 Si ya existe la reunión → validar y corregir saldo inicial
    # -------------------------------------------------------
    if reunion:

        saldo_inicial_actual = Decimal(str(reunion["saldo_inicial"]))

        if saldo_inicial_actual != saldo_correcto:

            cursor.execute("""
                UPDATE caja_reunion
                SET saldo_inicial=%s,
                    saldo_final=%s
                WHERE id_caja=%s
            """, (saldo_correcto, saldo_correcto, reunion["id_caja"]))

            con.commit()

        return reunion["id_caja"]

    # -------------------------------------------------------
    # 🔥 Si NO existe → crearla con el saldo correcto
    # -------------------------------------------------------
    cursor.execute("""
        INSERT INTO caja_reunion(fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES(%s, %s, 0, 0, %s)
    """, (fecha, saldo_correcto, saldo_correcto))

    con.commit()
    return cursor.lastrowid


# ============================================================
# ⚠️ COMPATIBILIDAD: muchos módulos tuyos usan esta función
# ============================================================
def obtener_o_crear_reunion(fecha):
    return asegurar_reunion(fecha)


# ============================================================
# 🔵 ACTUALIZAR CAJA GENERAL (siempre sincronizada)
# ============================================================
def actualizar_caja_general(nuevo_saldo):
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("UPDATE caja_general SET saldo_actual=%s WHERE id=1", (nuevo_saldo,))
    con.commit()


# ============================================================
# 🟦 REGISTRAR MOVIMIENTO (Ingreso / Egreso)
# ============================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # Obtener valores actuales
    cursor.execute("SELECT * FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    reunion = cursor.fetchone()

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # -------------------------------------------------------
    # 🔵 Ajuste de valores
    # -------------------------------------------------------
    if tipo == "Ingreso":
        ingresos += monto
    elif tipo == "Egreso":
        egresos += monto
    else:
        raise ValueError("Tipo de movimiento inválido")

    saldo_final = saldo_inicial + ingresos - egresos

    # -------------------------------------------------------
    # 🔵 Actualizar reunión
    # -------------------------------------------------------
    cursor.execute("""
        UPDATE caja_reunion
        SET ingresos=%s,
            egresos=%s,
            saldo_final=%s
        WHERE id_caja=%s
    """, (ingresos, egresos, saldo_final, id_caja))

    # -------------------------------------------------------
    # 🔵 Insertar el movimiento del día
    # -------------------------------------------------------
    cursor.execute("""
        INSERT INTO caja_movimientos(id_caja, tipo, categoria, monto)
        VALUES(%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    # -------------------------------------------------------
    # 🔵 Sincronizar caja_general
    # -------------------------------------------------------
    actualizar_caja_general(saldo_final)

    con.commit()
    return True
