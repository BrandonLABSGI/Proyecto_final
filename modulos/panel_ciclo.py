import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date

def panel_ciclo():

    st.title("📘 Administración del Ciclo General")

    con = obtener_conexion()
    cursor = con.cursor()

    # Ciclo activo
    cursor.execute("SELECT id_ciclo, nombre_ciclo, fecha_inicio FROM ciclo WHERE estado='abierto'")
    ciclo_activo = cursor.fetchone()

    # ---------------------------------------------------------------------
    # SI YA HAY UN CICLO ACTIVO → MOSTRARLO
    # ---------------------------------------------------------------------
    if ciclo_activo:
        st.subheader("🔵 Ciclo activo")
        st.info(f"**Nombre:** {ciclo_activo[1]}\n\n**Fecha de inicio:** {ciclo_activo[2]}")

        st.warning("⚠️ Para cerrar este ciclo usa la opción **Cerrar Ciclo** en el menú lateral.")
        return

    # ---------------------------------------------------------------------
    # SI NO HAY CICLO ACTIVO → CREAR UNO NUEVO
    # ---------------------------------------------------------------------
    st.subheader("🟢 Abrir un nuevo ciclo")

    with st.form("nuevo_ciclo"):
        nombre = st.text_input("Nombre del ciclo:")
        enviar = st.form_submit_button("📘 Abrir ciclo")

    if enviar:
        if nombre.strip() == "":
            st.error("❌ Debes ingresar un nombre para el ciclo.")
            return

        cursor.execute("""
            INSERT INTO ciclo (nombre_ciclo, fecha_inicio, saldo_inicial, estado)
            VALUES (%s, %s, %s, %s)
        """, (nombre, date.today(), 0.00, "abierto"))

        con.commit()

        st.success("✅ Ciclo abierto exitosamente.")
        st.rerun()
