import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_administrador():
    st.header("🛡️ Panel del Administrador")
    st.write("Gestiona distritos, empleados y el estado general del sistema.")

    menu = st.sidebar.radio(
        "Menú del Administrador:",
        [
            "🏙️ Ver distritos",
            "👥 Ver grupos",
            "🧑‍💼 Ver empleados",
            "📊 Resumen general del sistema"
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
                st.write(f"""
                🏙️ **Distrito ID:** {d[0]}  
                • **Nombre:** {d[1]}  
                • **Representantes:** {d[2]}  
                • **Grupos:** {d[3]}  
                • **Estado:** {d[4]}
                """)
        else:
            st.warning("No existen distritos registrados.")

    # ------------------------------------------------------
    # MOSTRAR GRUPOS
    # ------------------------------------------------------
    elif menu == "👥 Ver grupos":
        st.subheader("👥 Grupos registrados")

        cursor.execute("""
            SELECT Grupo.Id_Grupo,
                   Grupo.Nombre,
                   Distrito.`Nombre del distrito`
            FROM Grupo
            INNER JOIN Distrito ON Grupo.Id_Distrito = Distrito.Id_Distrito
        """)
        filas = cursor.fetchall()

        if filas:
            for g in filas:
                st.write(f"🔸 **Grupo:** {g[1]} — **Distrito:** {g[2]} (ID {g[0]})")
        else:
            st.warning("No hay grupos registrados.")

    # ------------------------------------------------------
    # MOSTRAR EMPLEADOS
    # ------------------------------------------------------
    elif menu == "🧑‍💼 Ver empleados":
        st.subheader("🧑‍💼 Empleados del sistema")

        cursor.execute("SELECT Id_Empleado, Usuario, Rol FROM Empleado")
        filas = cursor.fetchall()

        if filas:
            for e in filas:
                icon = "👑" if e[2].lower() == "administrador" else "👤"
                st.write(f"{icon} **Usuario:** {e[1]} — **Rol:** {e[2]} (ID {e[0]})")
        else:
            st.warning("No hay empleados registrados.")

    # ------------------------------------------------------
    # RESUMEN GENERAL DEL SISTEMA
    # ------------------------------------------------------
    elif menu == "📊 Resumen general del sistema":
        st.subheader("📊 Indicadores Generales del Sistema")

        cursor.execute("SELECT COUNT(*) FROM Distrito")
        total_distritos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Grupo")
        total_grupos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Empleado")
        total_empleados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Prestamo")
        total_prestamos = cursor.fetchone()[0]

        st.info(f"🏙️ **Distritos:** {total_distritos}")
        st.info(f"👥 **Grupos:** {total_grupos}")
        st.info(f"🧑‍💼 **Empleados:** {total_empleados}")
        st.info(f"💰 **Préstamos registrados:** {total_prestamos}")

        st.success("📌 Vista estratégica del sistema actualizada.")
