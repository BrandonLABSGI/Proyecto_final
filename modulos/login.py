import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Bienvenida — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
        <style>
            body {
                background-color: #0d1117 !important;
            }

            .welcome-title {
                font-size: 42px;
                font-weight: 800;
                text-align: center;
                color: #ffffff;
                margin-top: 20px;
                margin-bottom: 40px;
            }

            .img-box {
                display: flex;
                justify-content: center;
                margin-top: 10px;
            }

            .img-box img {
                width: 320px;               /* ⬅️ AJUSTA AQUÍ EL TAMAÑO */
                border-radius: 18px;
                box-shadow: 0px 4px 30px rgba(0,0,0,0.25);
            }

        </style>
    """, unsafe_allow_html=True)

    # ============================
    # IMAGEN DE SEÑORAS
    # ============================
    st.markdown('<div class="img-box">', unsafe_allow_html=True)
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================
    # MENSAJE DE BIENVENIDA
    # ============================
    st.markdown('<div class="welcome-title">Bienvenida a Solidaridad CVX</div>', unsafe_allow_html=True)

    # ============================
    # FORMULARIO DE LOGIN
    # ============================
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
