import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ==========================
    # IMAGEN DE LAS SOCIAS
    # ==========================
    st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png", use_column_width=True)

    # ==========================
    # MENSAJE DE BIENVENIDA
    # ==========================
    st.markdown("""
        <h1 style="text-align:center; color:#0a3161; font-weight:800;">
            Bienvenida a la Asociación Solidaridad CVX
        </h1>
        <p style="text-align:center; font-size:18px; margin-top:-10px; color:#444;">
            Inicia sesión para continuar
        </p>
    """, unsafe_allow_html=True)

    # ==========================
    # FORMULARIO DE LOGIN
    # ==========================
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
            st.success("Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
