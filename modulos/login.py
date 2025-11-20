import streamlit as st
from modulos.conexion import obtener_conexion
import base64

def load_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def login():

    logo = load_base64("modulos/imagenes/logo.png")
    ilustracion = load_base64("modulos/imagenes/ilustracion.png")

    st.markdown("""
    <style>

    .stApp {
        background-color: #F4F5F0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .img-ilustracion {
        width: 94%;
        border-radius: 22px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.18);
    }

    .login-card {
        background: white;
        padding: 45px 55px;
        border-radius: 25px;
        width: 420px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.19);
    }

    .logo-img {
        width: 160px;
        margin-bottom: 5px;
    }

    .title {
        font-size: 28px;
        font-weight: 600;
        color: #123A75;
        margin-bottom: 25px;
        text-align: left;
    }

    label {
        color: #123A75 !important;
        font-weight: 500 !important;
    }

    .stTextInput>div>div>input {
        background: #FFF !important;
        border: 1px solid #888 !important;
        color: #000 !important;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }

    .stButton>button {
        background: #6FB43F !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 12px;
        width: 100%;
        height: 50px;
        border: none;
        margin-top: 8px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ===== LAYOUT REAL =====
    col1, col2 = st.columns([1.1, 1])

    # Ilustración
    with col1:
        st.markdown(
            f"<img src='data:image/png;base64,{ilustracion}' class='img-ilustracion'>",
            unsafe_allow_html=True
        )

    # Tarjeta
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        st.markdown(
            f"<img src='data:image/png;base64,{logo}' class='logo-img'>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='title'>Inicio de Sesión</div>", unsafe_allow_html=True)

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):
            con = obtener_conexion()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT Usuario, Rol FROM Empleado WHERE Usuario=%s AND Contra=%s",
                (usuario, password)
            )
            datos = cursor.fetchone()

            if datos:
                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Rol"]
                st.session_state["sesion_iniciada"] = True
                st.success("Inicio exitoso ✔")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")

        st.markdown("</div>", unsafe_allow_html=True)
