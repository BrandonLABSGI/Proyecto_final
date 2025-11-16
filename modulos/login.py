import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.title("Inicio de sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")
    boton = st.button("Ingresar")

    if boton:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            query = """
                SELECT Usuario, Rol 
                FROM Empleado
                WHERE Usuario = %s AND Contra = %s
            """
            cursor.execute(query, (usuario, contra))
            resultado = cursor.fetchone()

            if resultado:
                st.session_state["sesion_iniciada"] = True
                st.session_state["usuario"] = resultado[0]
                st.session_state["rol"] = resultado[1]  # Admin | Director | Promotora

                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")

