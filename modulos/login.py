import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # Quitar header/footer para que no genere duplicados
    st.markdown("""
        <style>
        header, footer {visibility: hidden;}
        .block-container {padding-top: 0rem;}
        </style>
    """, unsafe_allow_html=True)

    # 📌 MOSTRAR SOLO LA IMAGEN PRINCIPAL ARRIBA
    st.image(
        "modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png",
        use_column_width=True
    )

    # 📌 FORMULARIO DE LOGIN (DEBAJO DE LA IMAGEN)
    st.markdown("## Iniciar Sesión")

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
