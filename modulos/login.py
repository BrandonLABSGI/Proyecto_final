import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="wide")

    # ELIMINAR TODO LO QUE STREAMLIT AGREGA AUTOMÁTICAMENTE
    st.markdown("""
        <style>

        header, footer {visibility: hidden;}

        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }

        body {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* OCULTAR EL BLOQUE OSCURO DEBAJO */
        .stApp {
            overflow: hidden !important;
        }

        </style>
    """, unsafe_allow_html=True)

    # ================================
    # TARJETA COMPLETA DEL LOGIN
    # ================================
    st.markdown("""
        <style>
        .login-card {
            width: 900px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 4px 40px rgba(0,0,0,0.25);
            display: flex;
            overflow: hidden;
        }
        .left-img {
            width: 50%;
        }
        .left-img img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .right-box {
            width: 50%;
            padding: 50px;
            background: #faf9f4;
        }
        .title {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 20px;
            color: #0a3161;
        }
        </style>
    """, unsafe_allow_html=True)

    # CONTENEDOR HTML
    st.markdown("""
        <div class="login-card">
            <div class="left-img">
                <img src="modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png">
            </div>
            <div class="right-box">
                <div class="title">Iniciar Sesión</div>
                <div id="form-container"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # FORMULARIO STREAMLIT **DENTRO DE LA TARJETA**
    usuario = st.text_input("Usuario", key="user_input")
    contrasena = st.text_input("Contraseña", type="password", key="pass_input")

    if st.button("Iniciar sesión", key="btn_login"):

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
