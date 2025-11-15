import streamlit as st
from modulos.config.conexion import obtener_conexion

# ------------------------------------------------------------
# Interfaz principal del rol Promotora
# ------------------------------------------------------------
def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")

    usuario = st.session_state.get("usuario", "Desconocido")
    st.sidebar.success(f"Sesión iniciada como: {usuario} (Promotora)")

    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return

    try:
        cursor = con.cursor(dictionary=True)

        # Buscar el ID de la promotora según su usuario
        cursor.execute("SELECT Id_Empleado FROM Empleado WHERE Usuario = %s", (usuario,))
        promotora = cursor.fetchone()

        if promotora:
            id_promotora = promotora["Id_Empleado"]

            # Mostrar los grupos asignados a esta promotora
            cursor.execute("""
                SELECT Nombre_grupo, fecha_inicio, Tasa_de_interes, Periodicidad_de_reuniones,
                       Tipo_de_multa, Reglas_de_prestamo
                FROM Grupo
                WHERE Id_Promotora = %s
            """, (id_promotora,))
            grupos = cursor.fetchall()

            if grupos:
                st.subheader("📋 Grupos Asignados")
                for grupo in grupos:
                    with st.expander(f"📌 {grupo['Nombre_grupo']}"):
                        st.write(f"**Fecha de inicio:** {grupo['fecha_inicio']}")
                        st.write(f"**Tasa de interés:** {grupo['Tasa_de_interes']}%")
                        st.write(f"**Periodicidad:** {grupo['Periodicidad_de_reuniones']}")
                        st.write(f"**Tipo de multa:** {grupo['Tipo_de_multa']}")
                        st.write(f"**Reglas:** {grupo['Reglas_de_prestamo']}")
            else:
                st.info("No hay grupos registrados para esta promotora.")
        else:
            st.warning("No se encontró información de la promotora.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
    finally:
        cursor.close()
        con.close()
