import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
        <style>
            body {
                background-color: #0d1117 !important;
            }

            .title-text {
                font-size: 32px;
                font-weight: 800;
                text-align: center;
                color: #0a3161;
                margin-bottom: 20px;
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
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # CENTRAR CONTENIDO
    # ============================
    st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)

    # Imagen pequeña y centrada
    st.image(
        "modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png",
        width=350
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Título
    st.markdown("<h2 class='title-text'>Bienvenida a Solidaridad CVX</h2>", unsafe_allow_html=True)

    # ============================
    # FORMULARIO LOGIN
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
            st.success("Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
