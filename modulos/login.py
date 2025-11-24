import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.markdown("<h1 style='text-align:center; color:white;'>Bienvenida a Solidaridad CVX</h1>", unsafe_allow_html=True)
    st.write("")

    # ==========================================
    # MOSTRAR IMAGEN (LA QUE SUBISTE)
    # ==========================================
    st.image("/mnt/data/3671faac-4776-4a9c-8ab3-9c7ea0b36d84.png", width=300)

    st.write("")

    # ==========================================
    # FORMULARIO LOGIN
    # ==========================================
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s",
            (usuario, contrasena)
        )
        user = cursor.fetchone()

        if user:
            st.success("Inicio de sesión exitoso")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = user["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
