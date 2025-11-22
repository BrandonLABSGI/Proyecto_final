def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    monto = Decimal(str(monto))

    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos
        FROM caja_reunion
        WHERE id_caja = %s
    """, (id_caja,))
    reunion = cursor.fetchone()

    if not reunion:
        return

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
        VALUES (%s, %s, %s, %s)
    """, (id_caja, tipo, categoria, monto))

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
