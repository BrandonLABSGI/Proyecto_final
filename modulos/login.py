import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.markdown(
        """
        <style>
            .center-img {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🖼️ Imagen centrada correctamente
    st.markdown('<div class="center-img">', unsafe_allow_html=True)
    st.image("modulos/imagenes/senoras.png", width=260)
    st.markdown('</div>', unsafe_allow_html=True)

    # TÍTULO
    st.markdown(
        "<h1 style='text-align:center; margin-top:0px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    # FORMULARIO LOGIN
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario=%s AND contraseña=%s",
            (usuario, contrasena)
        )
        row = cursor.fetchone()

        if row:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = row["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
