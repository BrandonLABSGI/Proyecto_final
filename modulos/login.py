import streamlit as st
import base64
import os
import mysql.connector

st.set_page_config(page_title="Login", page_icon="👥", layout="wide")


# =====================================================
# FUNCIÓN PARA CENTRAR IMAGEN LOCAL
# =====================================================
def centered_image(img_path, width=280):

    # RUTA ABSOLUTA SEGURA
    abs_path = os.path.join(os.path.dirname(__file__), img_path)

    if not os.path.exists(abs_path):
        st.error(f"No se encontró la imagen: {abs_path}")
        return

    with open(abs_path, "rb") as img_file:
        img_bytes = img_file.read()
        base64_img = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-top:15px; margin-bottom:5px;">
            <img src="data:image/png;base64,{base64_img}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# FUNCIÓN CORREGIDA PARA CONECTAR A MYSQL
# =====================================================
def obtener_conexion():
    try:
        con = mysql.connector.connect(
            host=os.getenv("MYSQL_ADDON_HOST"),
            user=os.getenv("MYSQL_ADDON_USER"),
            password=os.getenv("MYSQL_ADDON_PASSWORD"),
            database=os.getenv("MYSQL_ADDON_DB"),
            port=os.getenv("MYSQL_ADDON_PORT")
        )
        return con

    except mysql.connector.Error as err:
        st.error(f"❌ Error al conectar a la base de datos: {err}")
        return None


# =====================================================
# INTERFAZ DE LOGIN
# =====================================================
def login():

    # Imagen centrada
    centered_image("imagenes/senoras.png", width=260)

    # Título
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 40px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True,
    )

    field_width = 0.50  # → barras más cortas y centradas

    # ---------------- CAMPO USUARIO ----------------
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        usuario = st.text_input("Usuario")

    # ---------------- CAMPO CONTRASEÑA ----------------
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        contraseña = st.text_input("Contraseña", type="password")

    # ---------------- BOTÓN LOGIN ----------------
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        login_btn = st.button("Iniciar sesión")

    # ================= VALIDACIÓN ==================
    if login_btn:

        con = obtener_conexion()
        if con is None:
            return

        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND contrasenia = %s",
            (usuario, contraseña)
        )
        user = cursor.fetchone()

        if user:
            st.success("✅ Inicio de sesión exitoso.")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = user["rol"]
            st.rerun()

        else:
            st.error("❌ Usuario o contraseña incorrectos.")


# Ejecutar login
login()
