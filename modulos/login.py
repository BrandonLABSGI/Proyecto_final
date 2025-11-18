import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.title("🔐 Inicio de Sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Usuario, Contra, Rol
            FROM Empleado
            WHERE Usuario = %s AND Contra = %s
        """, (usuario, contra))

        row = cursor.fetchone()

        if row:
            st.success("Inicio de sesión exitoso.")
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = row[0]
            st.session_state["rol"] = row[2]   # << GUARDAMOS EL ROL AQUÍ
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
