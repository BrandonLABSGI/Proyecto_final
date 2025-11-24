import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    st.markdown("""
        <style>
            header, footer {visibility: hidden;}
            .main-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 40px;
            }
            .login-card {
                position: relative;
                width: 900px;
            }
            .form-box {
                position: absolute;
                top: 200px;          /* Ajustar posicion vertical */
                left: 520px;         /* Ajustar posicion horizontal */
                width: 330px;
                padding: 20px;
            }
            label {
                font-size: 16px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container"><div class="login-card">', unsafe_allow_html=True)

    # IMAGEN COMPLETA DEL LOGIN
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png", use_column_width=True)

    # FORMULARIO SUPERPUESTO
    st.markdown('<div class="form-box">', unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s",
            (usuario, contrasena)
        )

        datos = cursor.fetchone()

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = datos["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown('</div></div></div>', unsafe_allow_html=True)
