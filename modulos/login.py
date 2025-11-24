import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS PROFESIONALES
    # ============================
    st.markdown("""
        <style>

            /* Contenedor principal de la tarjeta */
            .login-container {
                width: 900px;
                margin: 60px auto;
                background: #faf9f4;
                border-radius: 18px;
                box-shadow: 0px 4px 40px rgba(0,0,0,0.25);
                overflow: hidden;
                display: flex;
            }

            /* Panel izquierdo */
            .login-left {
                width: 50%;
                background-color: #ffffff;
            }
            .login-left img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            /* Panel derecho */
            .login-right {
                width: 50%;
                padding: 50px 45px;
                background: #faf9f4;
            }

            .title {
                font-size: 32px;
                font-weight: 800;
                margin-bottom: 25px;
                color: #0a3161;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background-color: white !important;
                border-radius: 8px;
                height: 45px;
                border: 1px solid #d1d5db;
                color: #000 !important;
            }

            .stButton>button {
                width: 100%;
                height: 45px;
                background-color: #2e7d32;
                color: white;
                border-radius: 8px;
                font-size: 17px;
                margin-top: 15px;
            }

            .stButton>button:hover {
                background-color: #1b5e20 !important;
            }

            /* Centrado absoluto */
            .center-box {
                display: flex;
                justify-content: center;
            }

        </style>
    """, unsafe_allow_html=True)

    # ============================
    # TARJETA LOGIN
    # ============================
    st.markdown('<div class="center-box"><div class="login-container">', unsafe_allow_html=True)

    # -------- Imagen a la izquierda --------
    st.markdown('<div class="login-left">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------- Formulario a la derecha --------
    st.markdown('<div class="login-right">', unsafe_allow_html=True)

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

    st.markdown('</div></div></div>', unsafe_allow_html=True)
