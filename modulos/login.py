import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # Quitar header/footer que Streamlit agrega
    st.markdown("""
        <style>
            header, footer {visibility: hidden;}
            .block-container {padding: 0 !important; margin: 0 auto !important; max-width: 900px;}
        </style>
    """, unsafe_allow_html=True)

    # ================================
    #  IMAGEN PRINCIPAL DEL LOGIN
    # ================================
    st.image("/mnt/data/A_2D_digital_illustration_login_screen_for_Solidar.png", use_column_width=True)

    # ================================
    #  FORMULARIO POSICIONADO DEBAJO
    #  (NO se duplica, NO se mueve)
    # ================================
    st.write("")  # pequeño espacio invisible
    st.write("")  

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
