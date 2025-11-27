import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import asegurar_reunion, registrar_movimiento


# ============================================================
# REGISTRO DE AHORRO
# ============================================================
def ahorro():

    st.header("💰 Registrar ahorro")

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

    # Combobox
    opciones = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("Seleccione a la socia:", list(opciones.keys()))
    id_socia = opciones[socia_sel]

    # --------------------------------------------------------
    # FECHA DE OPERACIÓN
    # --------------------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del ahorro:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Crear o reparar la reunión para esta fecha
    id_caja = asegurar_reunion(fecha)

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del ahorro ($):", min_value=0.00, step=0.25)

    if monto <= 0:
        st.info("Ingrese un monto mayor a cero.")
        return

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar ahorro"):

        # Registrar en Caja
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Ahorro – {id_socia}",
            monto=monto
        )

        # Registrar ahorro particular
        cur.execute("""
            INSERT INTO Ahorro (Id_Socia, Fecha, Monto)
            VALUES (%s, %s, %s)
        """, (id_socia, fecha, Decimal(str(monto))))

        # Actualizar caja general
        cur.execute("""
            UPDATE caja_general
            SET saldo_actual = saldo_actual + %s
            WHERE id = 1
        """, (Decimal(str(monto)),))

        con.commit()

        st.success("Ahorro registrado correctamente.")
        st.rerun()

    # --------------------------------------------------------
    # LISTADO DE AHORROS DEL DÍA
    # --------------------------------------------------------
    cur.execute("""
        SELECT A.Id_Ahorro, S.Nombre, A.Monto
        FROM Ahorro A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Fecha=%s
        ORDER BY A.Id_Ahorro ASC
    """, (fecha,))
    registros = cur.fetchall()

    if registros:
        st.subheader("📋 Ahorros registrados en esta fecha")
        import pandas as pd
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
