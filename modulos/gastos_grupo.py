import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


def gastos_grupo():

    st.subheader("💸 Registrar gastos del grupo")

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
    responsable = st.text_input("Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI (UN SOLO CAMPO - máx 9 dígitos)
    # --------------------------------------------------------
    dui_raw = st.text_input("DUI (9 dígitos)", value="", max_chars=9)

    # Si intenta ingresar más de 9 dígitos, lo recortamos
    if len(dui_raw) > 9:
        dui_raw = dui_raw[:9]

    # Validación SOLO para el botón
    dui_valido = dui_raw.isdigit() and len(dui_raw) == 9

    # --------------------------------------------------------
    # CONCEPTO (opcional)
    # --------------------------------------------------------
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, step=0.01)

    # --------------------------------------------------------
    # SALDO DISPONIBLE
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN DE REGISTRO
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # Validación DUI
        if not dui_valido:
            st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        # Validación de saldo
        if monto > saldo:
            st.error("❌ No se puede registrar el gasto. El saldo es insuficiente.")
            return

        # Obtener reunión (Opción A)
        id_caja = obtener_o_crear_reunion(fecha)

        try:
            cursor.execute("""
                INSERT INTO Gastos_grupo (Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, descripcion, monto, responsable, dui_raw, id_caja))
            con.commit()

            # Registrar mov en caja
            registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion}", monto)

            st.success("✔ Gasto registrado correctamente.")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error registrando el gasto en MySQL.\n\n{e}")
