import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================
    # FUENTE PERSONALIZADA
    # ============================
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
    <style>

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F7 100%) !important;
    }

    .login-card {
        background-color: white;
        padding: 45px 45px 55px 45px;
        border-radius: 22px;
        width: 420px;
        margin-left: auto;
        margin-right: auto;
        margin-top: 100px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.10);
        transition: all 0.3s ease-in-out;
    }

    .login-card:hover {
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }

    .logo-container {
        text-align: center;
        margin-bottom: 15px;
    }

    .titulo {
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        color: #0A3B70;
        margin-bottom: 25px;
    }

    label {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #2F3B4C !important;
    }

    .stTextInput>div>div>input {
        background-color: #FAFBFF !important;
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        padding: 12px !important;
        font-size: 16px !important;
    }

    .stTextInput>div>div>input:focus {
        border: 1px solid #3BAA36 !important;
        box-shadow: 0 0 0 2px rgba(59,170,54,0.2) !important;
    }

    .stButton>button {
        width: 100%;
        background-color: #3BAA36 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        margin-top: 12px;
        border: none;
    }

    .stButton>button:hover {
        background-color: #2F8F2B !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================
    # TARJETA DE LOGIN
    # ============================
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    # LOGO
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png", width=220)
    st.markdown("</div>", unsafe_allow_html=True)

    # TÍTULO
    st.markdown("<div class='titulo'>Inicio de Sesión</div>", unsafe_allow_html=True)

    # CAMPOS
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    # BOTÓN
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

