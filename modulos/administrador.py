import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_administrador():
    st.header("🛡️ Panel del Administrador")
    st.write("""
    El administrador debe ver el panorama completo de los diferentes distritos, 
    así como la estrategia general asociada a su operación.
    """)

    # No hay menú: solo la vista de distritos
    st.subheader("🏙️ Distritos Registrados")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # CONSULTA CORRECTA SEGÚN TU BASE
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
            ### 🏙️ Distrito: **{d[1]}**
            **ID:** {d[0]}  
            **Representantes:** {d[2]}  
            **Cantidad de grupos:** {d[3]}  
            **Estado:** `{d[4]}`
            """)
    else:
        st.warning("No existen distritos registrados.")
