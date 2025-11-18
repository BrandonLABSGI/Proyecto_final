import streamlit as st
from modulos.conexion import obtener_conexion


def login():

    st.title("🔐 Inicio de sesión")

    usuario = st.text_input("Usuario:")
    password = st.text_input("Contraseña:", type="password")

    if st.button("Ingresar"):

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Id_Empleado, Usuario, Rol
            FROM Empleado
            WHERE Usuario = %s AND Contra = %s
        """, (usuario, password))

        fila = cursor.fetchone()

        if fila:
            id_empleado, user, rol = fila

            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = user
            st.session_state["rol"] = rol

            st.rerun()

        else:
            st.error("❌ Usuario o contraseña incorrectos.")
