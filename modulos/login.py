import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
        <style>

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

            .center-img {
                display: flex;
                justify-content: center;
                margin-bottom: 10px;
            }

        </style>
    """, unsafe_allow_html=True)

    # ============================
    # IMAGEN CENTRADA
    # ============================
    st.markdown('<div class="center-img">', unsafe_allow_html=True)
    st.image("modulos/imagenes/senoras.png", width=260)
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================
    # TÍTULO
    # ============================
    st.markdown(
        "<h1 style='text-align:center; font-weight:800;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    # ============================
    # FORMULARIO
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
