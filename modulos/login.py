import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # Estilos
    # ============================
    st.markdown("""
        <style>
            .center-img {
                display: flex;
                justify-content: center;
                margin-top: 30px;
                margin-bottom: 10px;
            }
            .welcome {
                text-align: center;
                font-size: 32px;
                font-weight: 800;
                color: #0a3161;
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # Imagen recortada de las señoras
    # ============================
    st.markdown('<div class="center-img">', unsafe_allow_html=True)
    st.image("modulos/imagenes/senoras_recortada.png", width=380)
    st.markdown('</div>', unsafe_allow_html=True)

    # ============================
    # MENSAJE
    # ============================
    st.markdown('<div class="welcome">Bienvenida a Solidaridad CVX</div>', unsafe_allow_html=True)

    # ============================
    # FORMULARIO LOGIN
    # ============================
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
