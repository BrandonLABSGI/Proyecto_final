import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ==========================================
    # ESTILOS
    # ==========================================
    st.markdown("""
        <style>

            body, .stApp {
                background-color: #0d0f16 !important;
            }

            /* Contenedor tarjeta */
            .login-card {
                width: 900px;
                margin: 60px auto;
                background: #ffffff;
                border-radius: 22px;
                box-shadow: 0px 4px 40px rgba(0,0,0,0.25);
                overflow: hidden;
                display: flex;
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
                padding: 45px 40px;
                background: #faf9f4;
            }

            .title {
                font-size: 32px;
                font-weight: 800;
                color: #0a3161;
                margin-bottom: 25px;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background-color: white !important;
                height: 45px;
                border-radius: 8px;
                border: 1px solid #d4d4d4;
                color: black !important;
            }

            .stButton>button {
                width: 100%;
                height: 45px;
                border-radius: 8px;
                background-color: #2e7d32;
                color: white;
                font-size: 17px;
            }

            .stButton>button:hover {
                background-color: #1e5b23;
            }

        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # TARJETA LOGIN
    # ==========================================
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    # PANEL IZQUIERDO
    st.markdown('<div class="left-side">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # PANEL DERECHO
    st.markdown('<div class="right-side">', unsafe_allow_html=True)

    st.markdown('<div class="title">Iniciar Sesión</div>', unsafe_allow_html=True)

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

    st.markdown('</div></div>', unsafe_allow_html=True)
