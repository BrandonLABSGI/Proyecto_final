import streamlit as st
from modulos.conexion import obtener_conexion


# =====================================
#           PANTALLA DE LOGIN
# =====================================
def login():

    # ============================
    #      IMAGEN CENTRADA
    # ============================
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-top: 40px;">
            <img src="modulos/imagenes/senoras.png" width="260">
        </div>
        """,
        unsafe_allow_html=True
    )

    # ============================
    #        TÍTULO CENTRADO
    # ============================
    st.markdown(
        "<h1 style='text-align: center; margin-top: 10px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    # ============================
    #        CAMPOS DE LOGIN
    # ============================
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    # ============================
    #         BOTÓN LOGIN
    # ============================
    if st.button("Iniciar sesión"):

        if usuario == "" or contrasena == "":
            st.error("Por favor complete todos los campos.")
            return

        # Conexión a BD
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s",
            (usuario, contrasena)
        )
        resultado = cursor.fetchone()

        if resultado:
            st.success("Inicio de sesión exitoso.")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = resultado["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
