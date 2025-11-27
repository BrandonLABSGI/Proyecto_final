import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# 🔵 REGISTRAR PAGO DE PRÉSTAMO — VERSIÓN FINAL
# ============================================================
def pago_prestamo():

    st.header("💵 Registrar pago de préstamo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # Obtener socias
    # --------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dict_socias = {f"{s['Id_Socia']} – {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # --------------------------------------------------------
    # Obtener préstamos pendientes de la socia
    # --------------------------------------------------------
    cursor.execute("""
        SELECT 
            Id_Prestamo,
            Fecha_del_prestamo,
            Monto_prestado,
            Saldo_pendiente,
            Estado_del_prestamo
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='Pendiente'
        ORDER BY Id_Prestamo ASC
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("✔ La socia no tiene préstamos pendientes.")
        return

    dict_prestamos = {
        f"#{p['Id_Prestamo']} – Pendiente: ${p['Saldo_pendiente']}": p["Id_Prestamo"]
        for p in prestamos
    }

    prest_sel = st.selectbox("Seleccione el préstamo:", dict_prestamos.keys())
    id_prestamo = dict_prestamos[prest_sel]

    # Obtener datos del préstamo seleccionado
    cursor.execute("""
        SELECT * FROM Prestamo WHERE Id_Prestamo=%s
    """, (id_prestamo,))
    prest = cursor.fetchone()

    saldo_pendiente = Decimal(str(prest["Saldo_pendiente"]))

    # --------------------------------------------------------
    # Información de pago
    # --------------------------------------------------------
    monto_pago = st.number_input("Monto a pagar ($):", min_value=0.00, value=float(saldo_pendiente), step=0.25)

    fecha_raw = st.date_input("📅 Fecha del pago:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    if st.button("💾 Registrar pago"):

        if monto_pago <= 0:
            st.warning("⚠ Debe ingresar un monto válido.")
            return

        if monto_pago > saldo_pendiente:
            st.warning("⚠ El monto excede el saldo pendiente.")
            return

        # ====================================================
        # 🔵 Garantizar reunión
        # ====================================================
        id_caja = obtener_o_crear_reunion(fecha)

        # ====================================================
        # 🔵 Actualizar saldo del préstamo
        # ====================================================
        nuevo_saldo = saldo_pendiente - Decimal(str(monto_pago))

        nuevo_estado = "Pendiente"
        if nuevo_saldo <= 0:
            nuevo_saldo = Decimal("0.00")
            nuevo_estado = "Pagado"

        cursor.execute("""
            UPDATE Prestamo
            SET Saldo_pendiente=%s,
                Estado_del_prestamo=%s
            WHERE Id_Prestamo=%s
        """, (nuevo_saldo, nuevo_estado, id_prestamo))

        # ====================================================
        # 🔵 Registrar ingreso en caja
        # ====================================================
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago préstamo #{id_prestamo} – {socia_sel}",
            monto=monto_pago
        )

        con.commit()

        st.success("✔ Pago registrado exitosamente.")
        st.rerun()

    # --------------------------------------------------------
    # Mostrar historial de préstamos de la socia
    # --------------------------------------------------------
    cursor.execute("""
        SELECT Id_Prestamo, Monto_prestado, Saldo_pendiente, Estado_del_prestamo
        FROM Prestamo
        WHERE Id_Socia=%s
        ORDER BY Id_Prestamo ASC
    """, (id_socia,))
    historial = cursor.fetchall()

    st.markdown("### 📋 Historial de préstamos")
    st.dataframe(historial, use_container_width=True)
