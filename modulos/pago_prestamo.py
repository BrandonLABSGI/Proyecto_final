import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import asegurar_reunion, registrar_movimiento


# ============================================================
# 💵 REGISTRAR PAGO DE PRÉSTAMO
# ============================================================
def pago_prestamo():

    st.header("💵 Registrar pago de préstamo")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # SOCIAS
    # --------------------------------------------------------
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    opciones = {f"{s['Id_Socia']} – {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("Seleccione la socia:", list(opciones.keys()))
    id_socia = opciones[socia_sel]

    # --------------------------------------------------------
    # PRÉSTAMOS PENDIENTES DE ESA SOCIA
    # --------------------------------------------------------
    cur.execute("""
        SELECT Id_Prestamo, Monto, Estado
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado='Pendiente'
        ORDER BY Id_Prestamo ASC
    """, (id_socia,))
    prestamos = cur.fetchall()

    if not prestamos:
        st.info("✔ La socia no tiene préstamos pendientes.")
        return

    opcion_prestamo = {
        f"ID {p['Id_Prestamo']} – Monto pendiente: ${p['Monto']:.2f}": p["Id_Prestamo"]
        for p in prestamos
    }
    prestamo_sel = st.selectbox("Seleccione préstamo a pagar:", list(opcion_prestamo.keys()))
    id_prestamo = opcion_prestamo[prestamo_sel]

    # --------------------------------------------------------
    # FECHA DEL PAGO
    # --------------------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del pago:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    id_caja = asegurar_reunion(fecha)

    # --------------------------------------------------------
    # MONTO A PAGAR
    # --------------------------------------------------------
    monto_pago = st.number_input("Monto del pago ($):", min_value=0.00, step=0.25)

    if monto_pago <= 0:
        st.info("Ingrese un monto mayor a cero.")
        return

    monto_pago_dec = Decimal(str(monto_pago))

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar pago"):

        # 1️⃣ Obtener monto pendiente del préstamo
        cur.execute("""
            SELECT Monto
            FROM Prestamo
            WHERE Id_Prestamo=%s
        """, (id_prestamo,))
        prestamo = cur.fetchone()

        monto_pendiente = Decimal(str(prestamo["Monto"]))

        if monto_pago_dec > monto_pendiente:
            st.error("❌ El pago no puede ser mayor que el monto pendiente.")
            return

        # 2️⃣ Actualizar préstamo
        nuevo_saldo = monto_pendiente - monto_pago_dec

        if nuevo_saldo == 0:
            # Marcar como pagado
            cur.execute("""
                UPDATE Prestamo
                SET Monto = 0, Estado='Pagado'
                WHERE Id_Prestamo=%s
            """, (id_prestamo,))
        else:
            cur.execute("""
                UPDATE Prestamo
                SET Monto=%s
                WHERE Id_Prestamo=%s
            """, (nuevo_saldo, id_prestamo))

        # 3️⃣ Registrar movimiento como ingreso
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago préstamo – {id_socia}",
            monto=monto_pago_dec
        )

        # 4️⃣ Actualizar caja_general
        cur.execute("""
            UPDATE caja_general
            SET saldo_actual = saldo_actual + %s
            WHERE id = 1
        """, (monto_pago_dec,))

        con.commit()

        st.success("Pago registrado correctamente.")
        st.rerun()

    # --------------------------------------------------------
    # LISTADO DE PAGOS DEL DÍA
    # --------------------------------------------------------
    cur.execute("""
        SELECT Id_Prestamo, S.Nombre, P.Monto AS Pendiente
        FROM Prestamo P
        JOIN Socia S ON S.Id_Socia = P.Id_Socia
        WHERE P.Fecha_Prestamo = %s
    """, (fecha,))
    registros = cur.fetchall()

    if registros:
        st.subheader("📋 Pagos registrados hoy")
        import pandas as pd
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
