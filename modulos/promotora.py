import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_promotora():
    st.title("📋 Panel de Promotora")
    st.info("Supervisa tus grupos, valida información financiera y descarga reportes consolidados.")

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

# ============================================
# PÁGINA 1 — Consultar grupos asignados
# ============================================

def pagina_consultar_grupos():
    st.header("👥 Grupos Asignados")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Los grupos deben tener un campo Id_Promotora asignado en tu tabla Grupo
    cursor.execute("SELECT * FROM Grupo")
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No hay grupos registrados.")
        return

    for g in grupos:
        st.subheader(g["Nombre_Grupo"])
        st.write(f"📌 **ID:** {g['Id_Grupo']}")
        st.write(f"📅 **Inicio:** {g['Fecha_Inicio']}")
        st.write(f"🔁 **Periodicidad:** {g['Periodicidad']}")
        st.markdown("---")

# ============================================
# PÁGINA 2 — Validar información financiera
# ============================================

def pagina_validar_finanzas():
    st.header("📑 Validar Información Financiera")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Prestamo")
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("No hay datos financieros registrados.")
        return

    st.write("### 📌 Lista de Préstamos")
    for p in prestamos:
        st.write(f"ID Préstamo: {p['Id_Prestamo']}")
        st.write(f"Monto: ${p['Monto']}")
        st.write(f"Estado: {p['Estado']}")
        st.markdown("---")

# ============================================
# PÁGINA 3 — Reportes Consolidados
# ============================================

def pagina_reportes():
    st.header("📊 Reportes Consolidados")
    st.info("Aquí podrás generar reportes generales del distrito o de cada grupo.")
