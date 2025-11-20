import streamlit as st
from modulos.conexion import obtener_conexion
import base64

# =========================================================
# Cargar imágenes en base64
# =========================================================
def load_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def login():
    logo = load_base64("modulos/imagenes/logo.png")
    ilustracion = load_base64("modulos/imagenes/ilustracion.png")

    # ======================================================
    # CSS limpio y 100% compatible con Streamlit Cloud
    # ======================================================
    st.markdown("""
    <style>

    .stApp {
        background-color: #F2F3EE !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Imagen izquierda */
    .img-ilustracion {
        width: 90%;
        border-radius: 20px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.17);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    /* Tarjeta */
    .login-card {
        background: white;
        padding: 40px 50px;
        border-radius: 25px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        width: 430px;
        margin: auto;
        text-align: center;
    }

    .logo-img {
        width: 160px;
        margin-bottom: 10px;
    }

    .title {
        font-size: 28px;
        font-weight: 600;
        color: #0F3A75;
        margin-bottom: 25px;
    }

    /* Inputs */
    label {
        color: #0F3A75 !important;
        font-weight: 500;
        font-size: 15px;
    }

    .stTextInput>div>div>input {
        color: #000 !important;
        background: #FFF !important;
        border-radius: 10px !important;
        border: 1px solid #777 !important;
        padding: 10px !important;
    }

    /* Botón */
    .stButton>button {
        background-color: #6FB43F !important;
        color: white !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        width: 100%;
        height: 48px;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # ======================================================
    # LAYOUT REAL STREAMLIT (no HTML grid)
    # ======================================================
    col1, col2 = st.columns([1.2, 1])

    # Columna izquierda
    with col1:
        st.markdown(
            f"<img src='data:image/png;base64,{ilustracion}' class='img-ilustracion'>",
            unsafe_allow_html=True
        )

    # Columna derecha: tarjeta
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
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT Usuario, Rol FROM Empleado WHERE Usuario=%s AND Contra=%s",
                        (usuario, password))
            datos = cur.fetchone()

            if datos:
                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Rol"]
                st.session_state["sesion_iniciada"] = True
                st.success("Ingreso exitoso ✔")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")

        st.markdown("</div>", unsafe_allow_html=True)
