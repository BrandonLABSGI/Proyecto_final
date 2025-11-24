import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ===========================
    # ESTILOS
    # ===========================
    st.markdown("""
        <style>
            body {
                background-color: #0e1117;
            }
            .titulo {
                font-size: 40px;
                font-weight: 800;
                text-align: center;
                color: white;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .img-center {
                display: flex;
                justify-content: center;
                margin-top: 20px;
                margin-bottom: -10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # ===========================
    # IMAGEN CENTRADA
    # ===========================
    st.markdown('<div class="img-center">', unsafe_allow_html=True)
    st.image("modulos/imagenes/senoras.png", width=330)
    st.markdown('</div>', unsafe_allow_html=True)

    # ===========================
    # TÍTULO
    # ===========================
    st.markdown('<div class="titulo">Bienvenida a Solidaridad CVX</div>', unsafe_allow_html=True)

    # ===========================
    # CAMPOS DE LOGIN
    # ===========================
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
            st.success("Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

