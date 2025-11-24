import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ==========================
    #   ESTILOS DEL LOGIN
    # ==========================
    st.markdown("""
        <style>

        body {
            background-color: #11141A !important;
        }

        .login-wrapper {
            width: 860px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 18px;
            box-shadow: 0px 4px 40px rgba(0,0,0,0.25);
            overflow: hidden;
            display: flex;
        }

        .login-image {
            width: 50%;
        }
        .login-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .login-box {
            width: 50%;
            padding: 45px 40px;
            background: #faf9f4;
        }

        .title {
            font-size: 30px;
            font-weight: 800;
            color: #0A3161;
            margin-bottom: 25px;
        }

        .stTextInput>div>div>input,
        .stPasswordInput>div>div>input {
            background-color: white;
            border-radius: 8px;
            height: 42px;
            border: 1px solid #CCC;
        }

        .stButton>button {
            width: 100%;
            background-color: #2e7d32;
            color: white;
            height: 45px;
            border-radius: 8px;
            font-size: 17px;
            margin-top: 20px;
        }

        .stButton>button:hover {
            background-color: #1b5e20;
        }

        </style>
    """, unsafe_allow_html=True)

    # ==========================
    #    TARJETA DEL LOGIN
    # ==========================
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    # Imagen
    st.markdown('<div class="login-image">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # Formulario
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown('<div class="title">Iniciar Sesión</div>', unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s", (usuario, contrasena))
        datos = cur.fetchone()

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = datos["rol"]
            st.success("Inicio de sesión correcto.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown('</div></div>', unsafe_allow_html=True)
