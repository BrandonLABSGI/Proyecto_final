from modulos.conexion import obtener_conexion


# ============================================================
# 1. OBTENER O CREAR REUNIÓN DE CAJA
# ============================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # 1) Buscar reunión existente
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    data = cursor.fetchone()

    if data:
        return int(data["id_caja"])

    # 2) Obtener saldo anterior
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    prev = cursor.fetchone()
    saldo_anterior = prev["saldo_final"] if prev else 0

    # 3) Crear reunión nueva
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_anterior, saldo_anterior))
    con.commit()

    # 4) Recuperar ID recién creado
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    nueva = cursor.fetchone()

    if not nueva:
        raise Exception("No se pudo crear la reunión de caja.")

    return int(nueva["id_caja"])


# ============================================================
# 2. REGISTRAR MOVIMIENTO
# ============================================================
def registrar_movimiento(id_caja, tipo, descripcion, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    if id_caja is None:
        raise ValueError("id_caja no puede ser None")

    # Registrar movimiento en tabla
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, descripcion, monto))

    # Obtener resumen de la reunión
    cursor.execute("""
        SELECT ingresos, egresos, saldo_inicial
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    reunion = cursor.fetchone()

    ingresos = reunion["ingresos"]
    egresos = reunion["egresos"]
    saldo_inicial = reunion["saldo_inicial"]

    # Actualizar saldo
    if tipo == "Ingreso":
        ingresos += monto
    else:
        egresos += monto

    saldo_final = saldo_inicial + ingresos - egresos

    cursor.execute("""
        UPDATE caja_reunion
        SET ingresos = %s, egresos = %s, saldo_final = %s
        WHERE id_caja = %s
    """, (ingresos, egresos, saldo_final, id_caja))

    con.commit()


# ============================================================
# 3. OBTENER SALDO POR FECHA
# ============================================================
def obtener_saldo_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["saldo_final"]

    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    return anterior["saldo_final"] if anterior else 0
