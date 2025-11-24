import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.markdown(
        """
        <style>
            .center {
                display: flex;
                justify-content: center;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------
    #   MOSTRAR SOLO LA IMAGEN
    # -------------------------------
    st.markdown('<div class="center">', unsafe_allow_html=True)
    st.image("modulos/imagenes/senoras.png", width=320)
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    #   TÍTULO
    # -------------------------------
    st.markdown(
        "<h2 style='text-align:center; color:white;'>Bienvenida a Solidaridad CVX</h2>",
        unsafe_allow_html=True
    )

    # -------------------------------
    #   FORMULARIO LOGIN
    # -------------------------------
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
            st.success("Inicio de sesión exitoso 🎉")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = datos["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
