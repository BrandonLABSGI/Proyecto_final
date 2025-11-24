import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # Ocultar cabecera y pie
    st.markdown("""
        <style>
            header, footer {visibility: hidden;}
            .block-container {padding-top: 20px !important; max-width: 900px;}
            label { font-size: 18px !important; }
        </style>
    """, unsafe_allow_html=True)

    # Mostrar la imagen desde tu repositorio
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png", use_column_width=True)

    st.write("### Iniciar Sesión")

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
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
