from modulos.conexion import obtener_conexion


# ============================================================
# 1. OBTENER O CREAR REUNIÓN DE CAJA
# ============================================================
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # 1) Buscar si ya existe reunión
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["id_caja"]

    # 2) Obtener último saldo previo
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    ultimo = cursor.fetchone()
    saldo_anterior = ultimo["saldo_final"] if ultimo else 0

    # 3) Crear reunión nueva
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_anterior, saldo_anterior))
    con.commit()

    # 4) Recuperar ID insertado correctamente (Streamlit Cloud compatible)
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    nueva = cursor.fetchone()

    return nueva["id_caja"]


# ============================================================
# 2. REGISTRAR MOVIMIENTO
# ============================================================
def registrar_movimiento(id_caja, tipo, descripcion, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Asegurarnos de que id_caja NO sea None
    if id_caja is None:
        raise ValueError("id_caja no puede ser None")

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, descripcion, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, descripcion, monto))

    # Obtener los valores actuales
    cursor.execute("""
        SELECT ingresos, egresos, saldo_inicial
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    reunion = cursor.fetchone()

    ingresos = reunion["ingresos"]
    egresos = reunion["egresos"]
    saldo_inicial = reunion["saldo_inicial"]

    # Actualizar según tipo
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

    # Buscar reunión exacta
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["saldo_final"]

    # Buscar la última previa
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    return anterior["saldo_final"] if anterior else 0
