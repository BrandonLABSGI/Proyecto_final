import streamlit as st
import base64
import os
import mysql.connector

st.set_page_config(page_title="Login", page_icon="👥", layout="wide")


# =====================================================
# FUNCIÓN PARA CENTRAR UNA IMAGEN LOCAL
# =====================================================
def centered_image(img_filename, width=280):

    img_path = os.path.join(os.path.dirname(__file__), "imagenes", img_filename)

    if not os.path.exists(img_path):
        st.error(f"No se encontró la imagen: {img_path}")
        return

    with open(img_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-top:20px;">
            <img src="data:image/png;base64,{img_base64}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# FUNCIÓN CORREGIDA DE CONEXIÓN A MYSQL
# **USANDO TUS CREDENCIALES NUEVAS**
# =====================================================
def obtener_conexion():
    try:
        con = mysql.connector.connect(
            host="btcfcbzptdyxq4f8afmu-mysql.services.clever-cloud.com",
            user="unruixx62rfqfqi5",
            password="tHsn5wIjxSzedGOsZmtL",
            database="btcfcbzptdyxq4f8afmu",
            port=3306  # Puerto correcto
        )
        return con
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
        return None


# =====================================================
# INTERFAZ DE LOGIN
# =====================================================
def login():

    centered_image("senoras.png", width=260)

    st.markdown(
        "<h1 style='text-align:center; margin-bottom: 25px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    # Campos más cortos
    field_width = 0.55  

    # ========== USUARIO ==========
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        usuario = st.text_input("Usuario")

    # ========== CONTRASEÑA ==========
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        contrasena = st.text_input("Contraseña", type="password")

    # ========== BOTÓN ==========
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        btn = st.button("Iniciar sesión")

    # ========== VALIDACIÓN ==========
    if btn:

        if usuario.strip() == "" or contrasena.strip() == "":
            st.warning("Por favor complete todos los campos.")
            return

        con = obtener_conexion()
        if con is None:
            return

        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND contrasenia = %s",
            (usuario, contrasena)
        )

        user = cursor.fetchone()

        cursor.close()
        con.close()

        if user:
            st.success("Inicio de sesión exitoso 🎉")

            # Guardar sesión
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = user["rol"]
            st.session_state["usuario"] = user["usuario"]

            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")


# =====================================================
# EJECUTAR LOGIN
# =====================================================
login()
