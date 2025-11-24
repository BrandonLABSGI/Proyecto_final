import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Login", layout="wide")

    # ==== CONTENEDOR GENERAL ====
    with st.container():
        st.markdown("""
            <div style='text-align:center; margin-top:20px;'>
                <img src='modulos/imagenes/senoras.png' style='width:280px; border-radius:15px;'/>
            </div>
        """, unsafe_allow_html=True)

        # Título centrado
        st.markdown(
            "<h2 style='text-align:center; margin-top:10px;'>Bienvenida a Solidaridad CVX</h2>",
            unsafe_allow_html=True
        )

        # FORMULARIO
        st.write("")
        st.write("")

        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):
            con = obtener_conexion()
            cursor = con.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario=%s AND contrasena=%s",
                (usuario, contraseña)
            )
            datos = cursor.fetchone()

            if datos:
                st.session_state["sesion_iniciada"] = True
                st.session_state["rol"] = datos["rol"]
                st.success("Inicio de sesión exitoso")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
