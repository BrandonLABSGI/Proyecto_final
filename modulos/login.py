import streamlit as st
import base64
import os
import mysql.connector

st.set_page_config(page_title="Login", page_icon="👥", layout="wide")


# ----------------------------------------------
# CONEXIÓN A LA BASE DE DATOS
# ----------------------------------------------
def obtener_conexion():
    return mysql.connector.connect(
        host="btcfcbzptdyxq4f8afmu-mysql.services.clever-cloud.com",
        user="ur33wxlwydbj7zja",
        password="DqjzqFj2pA3j2eS4U7kF",
        database="btcfcbzptdyxq4f8afmu"
    )


# ----------------------------------------------
# FUNCIÓN PARA CENTRAR UNA IMAGEN LOCAL
# ----------------------------------------------
def centered_image(img_path, width=280):
    full_path = os.path.join("modulos", "imagenes", img_path)

    if not os.path.exists(full_path):
        st.error(f"No se encontró la imagen: {full_path}")
        return

    with open(full_path, "rb") as img_file:
        img_bytes = img_file.read()
        base64_img = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-top:10px; margin-bottom:5px;">
            <img src="data:image/png;base64,{base64_img}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )


# ----------------------------------------------
# VERIFICAR USUARIO EN BD
# ----------------------------------------------
def validar_usuario(usuario, contraseña):
    try:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        query = """
            SELECT * FROM usuarios
            WHERE usuario = %s AND contraseña = %s
        """
        cursor.execute(query, (usuario, contraseña))
        result = cursor.fetchone()

        cursor.close()
        con.close()

        return result  # None si no existe

    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None


# ----------------------------------------------
# INTERFAZ DE LOGIN
# ----------------------------------------------
def login():

    centered_image("senoras.png", width=280)

    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 40px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    # Tamaño reducido de los campos
    field_width = 0.70  

    # Usuario
    st.write("")
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        usuario = st.text_input("Usuario")

    # Contraseña
    st.write("")
    col1, col2, col3 = st.columns([1 - field_width, field_width, 1 - field_width])
    with col2:
        contraseña = st.text_input("Contraseña", type="password")

    # Botón centrado
    st.write("")
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        ingresar = st.button("Iniciar sesión")

    # --------------------------
    # VALIDAR LOGIN
    # --------------------------
    if ingresar:
        if usuario.strip() == "" or contraseña.strip() == "":
            st.warning("Por favor completa todos los campos.")
            return

        datos = validar_usuario(usuario, contraseña)

        if datos:
            st.success("Inicio de sesión exitoso 🎉")

            # guardar sesión
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = datos["usuario"]
            st.session_state["rol"] = datos["rol"]

            st.rerun()

        else:
            st.error("Usuario o contraseña incorrectos.")


# Ejecutar login
login()
