# -------------------------------
# login.py
# -------------------------------

import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    # ESTILOS DEL FORMULARIO
    st.markdown(
        """
        <style>
        .login-box {
            background-color: white;
            padding: 40px;
            border-radius: 15px;
            width: 420px;
            margin-left: auto;
            margin-right: auto;
            margin-top: 40px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .login-title {
            text-align: center;
            font-size: 32px;
            color: #0C3C78;
            font-weight: bold;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    # LOGO ONG
    st.image("modulos/imagenes/logo.png", width=200)

    # TÍTULO
    st.markdown("<div class='login-title'>Inicio de Sesión</div>", unsafe_allow_html=True)

    # CAMPOS
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    # BOTÓN
    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT Usuario, Rol
                FROM Empleado
                WHERE Usuario = %s AND Contra = %s
            """, (usuario, password))

            datos = cursor.fetchone()

            if datos:
                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Rol"]
                st.session_state["sesion_iniciada"] = True

                st.success("Inicio de sesión exitoso.")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")

        except Exception as e:
            st.error(f"Error en login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

