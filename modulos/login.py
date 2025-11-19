import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ======== ESTILOS ========
    st.markdown("""
    <style>

    /* Fondo gris MUY claro */
    body, .stApp {
        background-color: #F4F6F8 !important;
    }

    /* Caja principal */
    .login-card {
        background-color: white;
        padding: 50px 40px;
        border-radius: 18px;
        width: 420px;
        margin-left: auto;
        margin-right: auto;
        margin-top: 70px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }

    /* Titulos */
    .titulo {
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        color: #0A3B70;
        margin-top: 10px;
        margin-bottom: 25px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #CCD1D5;
        font-size: 16px;
    }

    /* Botón */
    .stButton>button {
        width: 100%;
        background-color: #3BAA36 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 45px;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }

    .stButton>button:hover {
        background-color: #2E8A2B !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ======== TARJETA ========
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    # LOGO (centrado)
    st.image("modulos/imagenes/logo.png", width=200)

    # Título
    st.markdown("<div class='titulo'>Inicio de Sesión</div>", unsafe_allow_html=True)

    # Campos de entrada
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    # Botón
    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT Usuario, Rol
            FROM Empleado
            WHERE Usuario = %s AND Contra = %s
        """, (usuario, password))

        datos = cursor.fetchone()

        if datos:
            st.session_state["usuario"] = datos["Usuario"]
            st.session_state["rol"] = datos["Rol"]
            st.session_state["sesion_iniciada"] = True
            st.success("Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True)
