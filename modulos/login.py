import streamlit as st
import base64
import os

st.set_page_config(page_title="Login", page_icon="👥", layout="wide")


# ----------------------------------------------
# FUNCIÓN PARA CENTRAR UNA IMAGEN LOCAL
# ----------------------------------------------
def centered_image(img_path, width=280):
    if not os.path.exists(img_path):
        st.error(f"No se encontró la imagen: {img_path}")
        return

    with open(img_path, "rb") as img_file:
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
# INTERFAZ DE LOGIN
# ----------------------------------------------
def login():

    centered_image("modulos/imagenes/senoras.png", width=280)

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
        st.button("Iniciar sesión")


# Ejecutar login
login()
