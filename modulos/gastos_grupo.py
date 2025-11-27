import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# 💸 REGISTRAR GASTOS DEL GRUPO — VERSIÓN FINAL
# ============================================================
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # Fecha del gasto
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Responsable
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable:").strip()

    # --------------------------------------------------------
    # DUI (solo números, 9 dígitos)
    # --------------------------------------------------------
    dui_raw = st.text_input("DUI (9 dígitos):", value="", max_chars=9)
    dui = "".join([c for c in dui_raw if c.isdigit()])  # eliminar letras

    if len(dui) != 9:
        st.warning("⚠ El DUI debe contener exactamente 9 números.")

    # --------------------------------------------------------
    # Descripción
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto:").strip()

    # --------------------------------------------------------
    # Monto
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($):", min_value=0.00, step=0.25, format="%.2f")

    if st.button("💾 Registrar gasto"):

        # VALIDACIONES
        if not responsable:
            st.warning("⚠ Debe ingresar el nombre del responsable.")
            return

        if len(dui) != 9:
            st.warning("⚠ Ingrese un DUI válido (9 dígitos).")
            return

        if not descripcion:
            st.warning("⚠ Debe ingresar una descripción.")
            return

        if monto <= 0:
            st.warning("⚠ El monto debe ser mayor a cero.")
            return

        # ============================================================
        # 🔵 OBTENER O CREAR LA REUNIÓN DEL DÍA
        # ============================================================
        id_caja = obtener_o_crear_reunion(fecha)

        # ============================================================
        # 🔵 REGISTRAR GASTO EN TABLA Gastos_grupo
        # ============================================================
        cursor.execute("""
            INSERT INTO Gastos_grupo (fecha, responsable, dui, descripcion, monto, Id_Grupo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fecha, responsable, dui, descripcion, monto, 1))  # Id_Grupo = 1 (tu sistema actual)

        # ============================================================
        # 🔵 REGISTRAR EGRESO EN CAJA
        # ============================================================
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Gasto – {descripcion}",
            monto=Decimal(str(monto))
        )

        con.commit()

        st.success("✔ Gasto registrado exitosamente.")
        st.rerun()

    # ============================================================
    # 🔍 HISTORIAL DE GASTOS
    # ============================================================
    cursor.execute("""
        SELECT fecha, responsable, dui, descripcion, monto
        FROM Gastos_grupo
        ORDER BY fecha DESC
    """)

    registros = cursor.fetchall()

    st.markdown("### 📋 Historial de gastos")
    st.dataframe(registros, use_container_width=True)
