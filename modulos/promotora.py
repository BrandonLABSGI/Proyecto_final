import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_promotora():
    st.title("📋 Panel de Promotora")
    st.info("Supervisa los grupos bajo tu distrito, valida información y genera reportes.")

    opciones = [
        "Consultar grupos asignados",
        "Validar información financiera",
        "Reportes consolidados"
    ]

    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

    if seleccion == "Consultar grupos asignados":
        pagina_consultar_grupos()

    elif seleccion == "Validar información financiera":
        pagina_validar_finanzas()

    elif seleccion == "Reportes consolidados":
        pagina_reportes()


# ========= PÁGINAS =========

def pagina_consultar_grupos():
    st.header("👥 Grupos Asignados")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Grupo, Nombre_Grupo, Fecha_Inicio, Periodicidad FROM Grupo")
    grupos = cursor.fetchall()

    if len(grupos) == 0:
        st.warning("No hay grupos registrados.")
        return

    for g in grupos:
        st.write(f"**Grupo:** {g[1]}")
        st.write(f"• ID: {g[0]}")
        st.write(f"• Inicio: {g[2]}")
        st.write(f"• Reuniones: {g[3]}")
        st.markdown("---")


def pagina_validar_finanzas():
    st.header("📑 Validar Información Financiera")
    st.info("Aquí puedes revisar préstamos, pagos, movimientos y estados financieros.")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM Prestamo")
    prestamos = cursor.fetchall()

    st.write("### Préstamos Registrados", prestamos)


def pagina_reportes():
    st.header("📊 Reportes Consolidados")
    st.success("Aquí podrás descargar reportes financieros generales (PDF / Excel).")
