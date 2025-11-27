import mysql.connector
from decimal import Decimal
from modulos.conexion import obtener_conexion


# ============================================================
# 🟦 OBTENER SALDO ACTUAL DE LA CAJA (Última reunión cerrada)
# ============================================================
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT saldo_final 
        FROM caja_reunion
        ORDER BY fecha DESC LIMIT 1
    """)
    row = cursor.fetchone()

    return float(row[0]) if row else 0.00


# ============================================================
# 🟦 FUNCION CLAVE: OBTENER O CREAR REUNIÓN
#    🔥 REPARA SALDO_INICIAL SI YA EXISTE Y ESTÁ INCORRECTO
# ============================================================
def obtener_o_crear_reunion(fecha):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar reunión del día
    cursor.execute("SELECT * FROM caja_reunion WHERE fecha=%s", (fecha,))
    reunion = cursor.fetchone()

    # Saldo del día anterior
    cursor.execute("""
        SELECT saldo_final 
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    saldo_correcto = Decimal(str(anterior["saldo_final"])) if anterior else Decimal("0.00")

    # -------------------------------------------------------
    # 🔥 SI LA REUNIÓN YA EXISTE → VALIDAR Y CORREGIR
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
    # 🔥 SI NO EXISTE → CREARLA CON EL SALDO ADECUADO
    # -------------------------------------------------------
    cursor.execute("""
        INSERT INTO caja_reunion(fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES(%s, %s, 0, 0, %s)
    """, (fecha, saldo_correcto, saldo_correcto))

    con.commit()
    return cursor.lastrowid


# ============================================================
# 🟦 REGISTRAR MOVIMIENTO (INGRESO / EGRESO)
# ============================================================
def registrar_movimiento(id_caja, tipo, categoria, monto):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    # Obtener reunión actual
    cursor.execute("SELECT * FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    reunion = cursor.fetchone()

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # -------------------------------------------------------
    # 🔥 Ajuste de valores según tipo
    # -------------------------------------------------------
    if tipo == "Ingreso":
        ingresos += monto
    elif tipo == "Egreso":
        egresos += monto
    else:
        raise ValueError("Tipo de movimiento inválido")

    saldo_final = saldo_inicial + ingresos - egresos

    # -------------------------------------------------------
    # 🔥 Actualizar reunión
    # -------------------------------------------------------
    cursor.execute("""
        UPDATE caja_reunion
        SET ingresos=%s,
            egresos=%s,
            saldo_final=%s
        WHERE id_caja=%s
    """, (ingresos, egresos, saldo_final, id_caja))

    # -------------------------------------------------------
    # 🔥 Insertar el movimiento en caja_movimientos
    # -------------------------------------------------------
    cursor.execute("""
        INSERT INTO caja_movimientos(id_caja, tipo, categoria, monto)
        VALUES(%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

    con.commit()
    return True


# ============================================================
# 🟦 PROTEGER FECHAS FUTURAS (Opcional)
# ============================================================
def validar_fecha_reunion(fecha):
    """Se puede implementar si deseas bloquear reuniones futuras."""
    return True
