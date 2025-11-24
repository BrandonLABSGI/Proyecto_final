import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Inicio de Sesión — Solidaridad CVX", layout="centered")

    # --------------------- CSS ---------------------
    st.markdown("""
        <style>
            body {
                background-color: #0d1017 !important;
            }

            .card-login {
                width: 880px;
                margin: 50px auto;
                background: #ffffff;
                border-radius: 18px;
                overflow: hidden;
                display: flex;
                flex-direction: row;
                box-shadow: 0 4px 35px rgba(0,0,0,0.30);
            }

            .left-side {
                width: 50%;
            }
            .left-side img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .right-side {
                width: 50%;
                padding: 40px 45px;
                background: #faf9f4;
            }

            .title {
                font-size: 30px;
                font-weight: 800;
                color: #0A3161;
                margin-bottom: 20px;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                height: 42px;
                background: white !important;
                border-radius: 7px;
            }

            .stButton>button {
                width: 100%;
                height: 45px;
                font-size: 17px;
                border-radius: 7px;
                background-color: #2e7d32;
                color: white;
            }
            .stButton>button:hover {
                background-color: #1b5e20;
            }
        </style>
    """, unsafe_allow_html=True)

    # --------------------- TARJETA LOGIN ---------------------
    st.markdown('<div class="card-login">', unsafe_allow_html=True)

    # PANEL IZQUIERDO = IMAGEN
    st.markdown('<div class="left-side">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # PANEL DERECHO = FORMULARIO
    st.markdown('<div class="right-side">', unsafe_allow_html=True)

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
