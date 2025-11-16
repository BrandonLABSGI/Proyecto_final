import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_administrador():
    st.header("🛡️ Panel del Administrador")
    st.write("""
    El administrador debe ver el panorama completo del sistema: 
    estado general de los distritos, situación global y métricas clave 
    para la toma de decisiones estratégicas.
    """)

    menu = st.sidebar.radio(
        "Menú del Administrador:",
        [
            "🏙️ Ver distritos",
            "📊 Panorama general del sistema"
        ]
    )

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # ------------------------------------------------------
    # MOSTRAR DISTRITOS
    # ------------------------------------------------------
    if menu == "🏙️ Ver distritos":
        st.subheader("🏙️ Distritos Registrados")

        cursor.execute("""
            SELECT Id_Distrito,
                   `Nombre del distrito`,
                   Representantes,
                   `Cantidad de grupos`,
                   `Estado del distrito`
            FROM Distrito
        """)
        filas = cursor.fetchall()

        if filas:
            for d in filas:
                st.markdown(f"""
                ---
                ### 🏙️ Distrito **{d[1]}**
                **ID:** {d[0]}  
                **Representantes:** {d[2]}  
                **Cantidad de grupos:** {d[3]}  
                **Estado:** `{d[4]}`  
                """)
        else:
            st.warning("No existen distritos registrados.")

    # ------------------------------------------------------
    # PANORAMA GENERAL DEL SISTEMA
    # ------------------------------------------------------
    elif menu == "📊 Panorama general del sistema":
        st.subheader("📊 Panorama Estratégico del Sistema")

        # Métricas generales
        cursor.execute("SELECT COUNT(*) FROM Distrito")
        total_distritos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Grupo")
        total_grupos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Empleado")
        total_empleados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Prestamo")
        total_prestamos = cursor.fetchone()[0]

        st.info(f"🏙️ **Distritos activos:** {total_distritos}")
        st.info(f"👥 **Grupos funcionando:** {total_grupos}")
        st.info(f"🧑‍💼 **Empleados registrados:** {total_empleados}")
        st.info(f"💰 **Préstamos registrados:** {total_prestamos}")

        st.success("""
        📌 *El administrador puede observar el comportamiento general 
        y conocer el estado estratégico de todos los distritos y operaciones.*
        """)
