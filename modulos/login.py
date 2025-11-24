import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS DEL LOGIN (idéntico al ejemplo)
    # ============================
    st.markdown("""
        <style>
            body {
                background-color: #11141A;
            }
            .login-card {
                width: 900px;
                background: #ffffff;
                border-radius: 22px;
                box-shadow: 0px 4px 35px rgba(0,0,0,0.35);
                overflow: hidden;
                display: flex;
                margin: 70px auto;
            }

            .left-panel img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .right-panel {
                width: 50%;
                padding: 40px 50px;
                background: #faf9f4;
            }

            .title {
                font-size: 30px;
                font-weight: 800;
                color: #0a3161;
                margin-bottom: 25px;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background-color: white !important;
                border-radius: 8px;
                height: 45px;
                border: 1px solid #cfcfcf;
                color: #000;
            }

            .stButton>button {
                width: 100%;
                height: 45px;
                background-color: #2e7d32;
                color: white;
                border-radius: 8px;
                font-size: 17px;
                margin-top: 10px;
            }

            .stButton>button:hover {
                background-color: #1b5e20 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # TARJETA LOGIN EXACTA
    # ============================
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    # PANEL IZQUIERDO (IMAGEN COMPLETA)
    st.markdown('<div class="left-panel" style="width:50%;">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # PANEL DERECHO (FORMULARIO)
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)

    st.markdown('<div class="title">Inicio de Sesión</div>', unsafe_allow_html=True)

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

    st.markdown('</div></div>', unsafe_allow_html=True)
