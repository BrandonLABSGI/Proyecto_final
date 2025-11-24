import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.markdown(
        """
        <div style='text-align:center; margin-top: 40px;'>
            <img src='modulos/imagenes/senoras.png' style='width: 260px; border-radius: 15px;' />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1 style='text-align:center; margin-top: 20px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    st.write("")  
    st.write("")

    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contraseña = %s",
                       (usuario, contraseña))
        resultado = cursor.fetchone()

        if resultado:
            st.success("Inicio de sesión exitoso.")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = resultado["rol"]
        else:
            st.error("Usuario o contraseña incorrectos.")
