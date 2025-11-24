import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    st.markdown("""
        <style>
            body {
                background-color: #0d1117;
            }
            .login-img {
                display: flex;
                justify-content: center;
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .login-img img {
                width: 520px;
                border-radius: 18px;
                box-shadow: 0px 4px 25px rgba(0,0,0,0.35);
            }
            .title {
                font-size: 28px;
                font-weight: 800;
                color: #e6edf3;
                margin-bottom: 10px;
            }
            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background: #ffffff !important;
                height: 45px;
                border-radius: 8px;
            }
            .stButton>button {
                background: #2e7d32;
                color: white;
                width: 200px;
                height: 45px;
                font-size: 17px;
                border-radius: 8px;
            }
            .stButton>button:hover {
                background: #1b5e20 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------
    # MOSTRAR TU IMAGEN COMPLETA
    # ---------------------------
    st.markdown('<div class="login-img">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

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
