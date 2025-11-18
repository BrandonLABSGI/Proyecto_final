import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.title("🔐 Inicio de sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Id_Empleado, Usuario, Rol 
            FROM Empleado 
            WHERE Usuario = %s AND Contra = %s
        """, (usuario, contra))

        row = cursor.fetchone()

        if row:
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = row[1]
            st.session_state["rol"] = row[2]   # 👈 IMPORTANTE
            st.success(f"Bienvenido, {row[1]}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
