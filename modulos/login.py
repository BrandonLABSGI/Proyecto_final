import streamlit as st
import base64
from modulos.conexion import obtener_conexion

# ======================================================
#  IMAGEN BASE64 — ilustración estilo CVX (generada)
# ======================================================
ilustracion_base64 = """
iVBORw0KGgoAAAANSUhEUgAAA...
"""  # ← Aquí va la imagen BASE64 completa (te la pegaré en el siguiente mensaje porque es larga)

# ======================================================
#  IMAGEN BASE64 — logo CVX (manitas verdes)
# ======================================================
logo_base64 = """
iVBORw0KGgoAAAANSUhEUgAAA...
"""  # ← También completa (te la envío en el siguiente mensaje)

# ======================================================
# Función para renderizar imágenes desde BASE64
# ======================================================
def image_from_base64(b64):
    return f"<img src='data:image/png;base64,{b64}' style='width:100%; border-radius:12px;'/>"


def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============ ESTILOS ============
    st.markdown("""
        <style>

            body {
                background-color: #0f1117;
            }

            /* Tarjeta principal */
            .card {
                width: 900px;
                margin: 60px auto;
                background: #ffffff;
                border-radius: 18px;
                box-shadow: 0px 4px 40px rgba(0,0,0,0.30);
                display: flex;
                overflow: hidden;
            }

            /* Panel izquierdo */
            .left {
                width: 50%;
                background-color: #ffffff;
            }

            /* Panel derecho */
            .right {
                width: 50%;
                padding: 45px 45px;
                background: #faf9f4;
            }

            .title {
                font-size: 32px;
                font-weight: 900;
                margin-bottom: 25px;
                color: #0a3161;
            }

            /* Estilos inputs */
            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                height: 45px;
                border-radius: 8px;
                border: 1px solid #d1d5db;
                background-color: #ffffff !important;
                color: #000 !important;
            }

            /* Botón */
            .stButton>button {
                width: 100%;
                height: 45px;
                border-radius: 8px;
                background-color: #2e7d32;
                color: white;
                font-size: 18px;
            }
            
            .stButton>button:hover {
                background-color: #1b5e20 !important;
            }

        </style>
    """, unsafe_allow_html=True)

    # ============ ESTRUCTURA ============

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Panel izquierdo con la imagen
    st.markdown("<div class='left'>", unsafe_allow_html=True)
    st.markdown(image_from_base64(ilustracion_base64), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Panel derecho con el formulario
    st.markdown("<div class='right'>", unsafe_allow_html=True)

    st.markdown(image_from_base64(logo_base64), unsafe_allow_html=True)
    st.markdown("<h1 class='title'>Iniciar Sesión</h1>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s", (usuario, contrasena))
        datos = cursor.fetchone()

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = datos["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
