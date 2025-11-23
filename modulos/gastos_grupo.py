import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable del gasto").strip()

    # --------------------------------------------------------
    # DESCRIPCIÓN DEL GASTO
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto").strip()

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto_raw = st.number_input(
        "Monto del gasto ($)",
        min_value=0.01,
        format="%.2f",
        step=0.01
    )
    monto = Decimal(str(monto_raw))

    # --------------------------------------------------------
    # OBTENER SALDO DISPONIBLE DE LA REUNIÓN
    # --------------------------------------------------------
    id_reunion = obtener_o_crear_reunion(fecha)

    cursor.execute(
        "SELECT saldo_final FROM caja_reunion WHERE id_caja = %s",
        (id_reunion,)
    )
    fila = cursor.fetchone()
    saldo_disponible = float(fila["saldo_final"]) if fila else 0.0

    # SOLO mostramos el verdadero saldo disponible
    st.info(f"📌 Saldo disponible: **${saldo_disponible:,.2f}**")

    # --------------------------------------------------------
    # VALIDACIÓN PRINCIPAL
    # --------------------------------------------------------
    if monto > saldo_disponible:
        st.error(
            f"❌ No puedes registrar un gasto mayor al saldo disponible (${saldo_disponible:,.2f})."
        )
        return

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        try:
            registrar_movimiento(
                id_caja=id_reunion,
                tipo="egreso",
                monto=monto,
                descripcion=descripcion,
                responsable=responsable,
                fecha=fecha
            )

            st.success("✅ Gasto registrado correctamente.")

        except Exception as e:
            st.error("❌ Ocurrió un error al registrar el gasto.")
            st.write(e)

    cursor.close()
    con.close()
