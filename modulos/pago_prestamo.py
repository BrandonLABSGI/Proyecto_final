import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # SOCIAS
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # PRÉSTAMO ACTIVO
    cur.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
        LIMIT 1
    """, (id_socia,))
    prestamo = cur.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])

    st.subheader("📄 Información del préstamo")
    st.write(f"**ID Préstamo:** {id_prestamo}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")

    st.divider()

    # CUOTAS PENDIENTES
    cur.execute("""
        SELECT *
        FROM Cuotas_prestamo
        WHERE Id_Prestamo=%s AND Estado='pendiente'
        ORDER BY Numero_cuota ASC
    """, (id_prestamo,))
    cuotas = cur.fetchall()

    if not cuotas:
        st.success("🎉 Todas las cuotas están pagadas.")
        return

    st.subheader("📅 Cuotas pendientes")

    opciones = {
        f"Cuota #{c['Numero_cuota']} — {c['Fecha_programada']} — ${c['Monto_cuota']}":
            c["Id_Cuota"]
        for c in cuotas
    }

    cuota_sel = st.selectbox("Seleccione la cuota a pagar:", opciones.keys())
    id_cuota = opciones[cuota_sel]

    fecha_pago = st.date_input("📅 Fecha del pago:", date.today()).strftime("%Y-%m-%d")

    if st.button("💾 Registrar pago"):

        # Datos de la cuota
        cur.execute("SELECT * FROM Cuotas_prestamo WHERE Id_Cuota=%s", (id_cuota,))
        cuota = cur.fetchone()
        monto_cuota = Decimal(cuota["Monto_cuota"])

        # OBTENER AHORRO ACTUAL
        cur.execute("""
            SELECT `Saldo acumulado`
            FROM Ahorro
            WHERE Id_Socia=%s
            ORDER BY Id_Ahorro DESC LIMIT 1
        """, (id_socia,))
        row = cur.fetchone()
        ahorro_actual = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

        # VALIDAR AHORRO
        if ahorro_actual < monto_cuota:
            st.error("❌ La socia no tiene suficiente ahorro para pagar esta cuota.")
            return

        # DESCONTAR AHORRO
        nuevo_ahorro = ahorro_actual - monto_cuota
        cur.execute("""
            INSERT INTO Ahorro(`Fecha del aporte`, `Monto del aporte`,
             `Tipo de aporte`, `Comprobante digital`, `Saldo acumulado`, Id_Socia)
            VALUES (%s,%s,'Pago cuota préstamo','---',%s,%s)
        """, (fecha_pago, -monto_cuota, nuevo_ahorro, id_socia))

        # SUMAR A CAJA
        id_caja = obtener_o_crear_reunion(fecha_pago)
        registrar_movimiento(
            id_caja,
            "Ingreso",
            f"Pago cuota préstamo {id_prestamo}",
            monto_cuota
        )

        # MARCAR CUOTA COMO PAGADA
        cur.execute("""
            UPDATE Cuotas_prestamo
            SET Estado='pagada', Fecha_pago=%s, Id_Caja=%s
            WHERE Id_Cuota=%s
        """, (fecha_pago, id_caja, id_cuota))

        # ACTUALIZAR SALDO DEL PRÉSTAMO
        nuevo_saldo = saldo_pendiente - monto_cuota
        if nuevo_saldo < 0:
            nuevo_saldo = Decimal("0.00")

        cur.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente`=%s,
                Estado_del_prestamo =
                    CASE WHEN %s=0 THEN 'pagado' ELSE 'activo' END
            WHERE Id_Préstamo=%s
        """, (nuevo_saldo, nuevo_saldo, id_prestamo))

        con.commit()

        st.success("✔ Pago registrado correctamente.")
        st.rerun()
