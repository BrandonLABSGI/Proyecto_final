from modulos.conexion import obtener_conexion

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

    # 3) Crear reunión válida (evita valores NULL)
    cursor.execute("""
        INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
        VALUES (%s, %s, 0, 0, %s)
    """, (fecha, saldo_anterior, saldo_anterior))
    con.commit()

    # 4) Siempre recuperar el ID correctamente
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (fecha,))
    nueva = cursor.fetchone()

    if not nueva:
        raise Exception("No se pudo crear o recuperar la reunión de caja.")

    return int(nueva["id_caja"])
