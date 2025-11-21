import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


def gastos_grupo():

    st.title("🧾 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI
    # --------------------------------------------------------
    dui_input = st.text_input("DUI (9 dígitos)", max_chars=9)

    # Formateo del DUI solo si tiene 9 dígitos correctos
    dui_formateado = None
    if dui_input.isdigit() and len(dui_input) == 9:
        dui_formateado = dui_input[:8] + "-" + dui_input[8:]

    # --------------------------------------------------------
    # DESCRIPCIÓN
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto")

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # --------------------------------------------------------
    # SALDO
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # === VALIDACIONES SOLO AQUÍ ===

        if not responsable.strip():
            st.error("❌ Debe ingresar el nombre del responsable.")
            return

        if not descripcion.strip():
            st.error("❌ Debe ingresar la descripción del gasto.")
            return

        if not dui_input.isdigit() or len(dui_input) != 9:
            st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        if monto > saldo:
            st.error("❌ El monto del gasto no puede ser mayor al saldo disponible.")
            return

        # ----------------------------------------------------
        # CREAR O OBTENER REUNIÓN
        # ----------------------------------------------------
        id_caja = obtener_o_crear_reunion(fecha)

        # ----------------------------------------------------
        # REGISTRAR EN TABLA Gastos_grupo
        # ----------------------------------------------------
        cursor.execute("""
            INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fecha, descripcion, monto, responsable, dui_formateado, id_caja))
        con.commit()

        # ----------------------------------------------------
        # REGISTRAR MOVIMIENTO EN CAJA
        # ----------------------------------------------------
        registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion}", monto)

        st.success("✔ Gasto registrado exitosamente.")
        st.rerun()
