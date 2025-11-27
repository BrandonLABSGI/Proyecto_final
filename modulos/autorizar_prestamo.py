import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# 🔵 AUTORIZAR PRÉSTAMO — VERSIÓN FINAL
# ============================================================
def autorizar_prestamo():

    st.header("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

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

    lista_socias = {f"{s['Id_Socia']} – {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # --------------------------------------------------------
    # Datos del préstamo
    # --------------------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del préstamo:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    monto = st.number_input("Monto a prestar ($):", min_value=0.00, value=0.00, step=0.25)
    descripcion = st.text_area("Descripción del préstamo:")

    if st.button("💾 Autorizar préstamo"):

        if monto <= 0:
            st.warning("⚠ Debe ingresar un monto válido.")
            return

        # ====================================================
        # 🔵 GARANTIZAR REUNIÓN
        # ====================================================
        id_caja = obtener_o_crear_reunion(fecha)

        # ====================================================
        # 🔵 Registrar préstamo en tabla Prestamo
        # ====================================================
        cursor.execute("""
            INSERT INTO Prestamo
            (Fecha_del_prestamo, Monto_prestado, Interes_total, Plazo, Cuotas,
             Saldo_pendiente, Estado_del_prestamo, Id_Grupo, Id_Socia, Id_Caja)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fecha,
            monto,
            0,          # No calculamos interés automáticamente
            0,          # Plazo
            0,          # Cuotas
            monto,      # Saldo pendiente inicial
            "Pendiente",
            1,          # Grupo 1 (tu sistema actual usa uno por defecto)
            id_socia,
            id_caja
        ))

        # ====================================================
        # 🔵 Registrar el egreso en caja
        # ====================================================
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Préstamo a {socia_sel}",
            monto=Decimal(monto)
        )

        con.commit()

        st.success("✔ Préstamo autorizado exitosamente.")
        st.rerun()

    # --------------------------------------------------------
    # Mostrar préstamos existentes de la socia
    # --------------------------------------------------------
    cursor.execute("""
        SELECT Id_Prestamo, Fecha_del_prestamo, Monto_prestado, Saldo_pendiente, Estado_del_prestamo
        FROM Prestamo
        WHERE Id_Socia=%s
        ORDER BY Id_Prestamo ASC
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if prestamos:
        st.markdown("### 📋 Historial de préstamos")
        st.dataframe(prestamos, use_container_width=True)
