import streamlit as st
import os
import base64

# ---------------------------------------------------------
# FUNCION PARA MOSTRAR UNA IMAGEN CENTRADA
# ---------------------------------------------------------
def centered_image(relative_path, width=280):
    # Ruta absoluta correcta del archivo dentro del proyecto
    img_path = os.path.join(os.path.dirname(__file__), relative_path)

    # Leer imagen en base64
    with open(img_path, "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # HTML centrado
    st.markdown(
        f"""
        <div style="text-align:center; margin-top: 10px; margin-bottom: 25px;">
            <img src="data:image/png;base64,{img_base64}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# PANTALLA DE LOGIN
# ---------------------------------------------------------
def login():

    st.set_page_config(page_title="CVX", layout="wide")

    # Mostrar imagen centrada
    centered_image("imagenes/senoras.png", width=260)

    # Título centrado
    st.markdown(
        """
        <h1 style="text-align:center; color:white;">Bienvenida a Solidaridad CVX</h1>
        """,
        unsafe_allow_html=True
    )

    # Campos de login
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        st.success("Intentando iniciar sesión…")
