import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.markdown("<h1 style='text-align:center; margin-bottom:10px;'>Bienvenida a Solidaridad CVX</h1>", unsafe_allow_html=True)

    # 🔥 IMAGEN CENTRADA Y DEL TAMAÑO CORRECTO
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin-top: -10px; margin-bottom:20px;">
            <img src="modulos/imagenes/senoras.png" width="260">
        </div>
        """,
        unsafe_allow_html=True
    )

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
        user = cursor.fetchone()

        if user:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = user["rol"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
