import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import asegurar_reunion, registrar_movimiento


# ============================================================
# 💳 AUTORIZAR PRÉSTAMO
# ============================================================
def autorizar_prestamo():

    st.header("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # SOCIAS
    # --------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dict_socias = {f"{s['Id_Socia']} – {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("Seleccione a la socia:", list(dict_socias.keys()))
    id_socia = dict_socias[socia_sel]

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del préstamo:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Crear / reparar reunión de caja
    id_caja = asegurar_reunion(fecha)

    # --------------------------------------------------------
    # MONTO Y DESCRIPCIÓN
    # --------------------------------------------------------
    monto = st.number_input("Monto a prestar ($):", min_value=0.00, step=0.25)
    descripcion = st.text_area("Descripción del préstamo:")

    if monto <= 0:
        st.info("Ingrese un monto mayor que cero.")
        return

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Autorizar préstamo"):

        monto_dec = Decimal(str(monto))

        # 1️⃣ Guardar préstamo
        cursor.execute("""
            INSERT INTO Prestamo (Id_Socia, Fecha_Prestamo, Monto, Descripcion, Estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_socia, fecha, monto_dec, descripcion, "Pendiente"))

        # 2️⃣ Registrar movimiento como EGRESO en caja
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Préstamo – {id_socia}",
            monto=monto_dec
        )

        # 3️⃣ Actualizar caja_general
        cursor.execute("""
            UPDATE caja_general
            SET saldo_actual = saldo_actual - %s
            WHERE id = 1
        """, (monto_dec,))

        con.commit()

        st.success(f"Préstamo autorizado correctamente para {socia_sel}.")
        st.rerun()

    # --------------------------------------------------------
    # LISTADO DEL DÍA
    # --------------------------------------------------------
    cursor.execute("""
        SELECT P.Id_Prestamo, S.Nombre, P.Monto, P.Estado
        FROM Prestamo P
        JOIN Socia S ON S.Id_Socia = P.Id_Socia
        WHERE P.Fecha_Prestamo = %s
        ORDER BY P.Id_Prestamo ASC
    """, (fecha,))
    prestamos = cursor.fetchall()

    if prestamos:
        st.subheader("📋 Préstamos autorizados en esta fecha")
        import pandas as pd
        st.dataframe(pd.DataFrame(prestamos), use_container_width=True)
