import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================
    #       ESTILOS CSS
    # ============================
    st.markdown("""
        <style>

            /* Importar tipografía */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

            html, body, * {
                font-family: 'Poppins', sans-serif !important;
            }

            /* Fondo oscuro */
            body {
                background-color: #0e1117 !important;
            }

            /* Contenedor principal centrado */
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 20px;
            }

            /* Eliminar recuadro molesto superior */
            .st-emotion-cache-1dp5vir, .st-emotion-cache-1m2q0ib {
                display: none !important;
            }

            /* Caja del login */
            .login-box {
                background: #161a23;
                padding: 30px;
                border-radius: 18px;
                width: 90%;
                max-width: 380px;
                box-shadow: 0px 4px 18px rgba(0,0,0,0.45);
                margin-top: 10px;
            }

            /* Logo centrado */
            .logo-container img {
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 150px;
            }

            h2 {
                color: #e3e6ed !important;
                text-align: center;
                font-weight: 600;
                margin-top: 10px;
            }

            /* Input */
            .stTextInput > div > div > input {
                background-color: #1f2430 !important;
                color: #ffffff !important;
                border: 1px solid #3d4352 !important;
                padding: 10px 40px 10px 35px !important;
                border-radius: 8px;
                font-size: 15px;
            }

            /* Iconos dentro del input */
            .icon {
                position: relative;
                top: -35px;
                left: 10px;
                color: #9aa0ad;
                font-size: 18px;
            }

            /* Botón */
            .stButton > button {
                width: 100%;
                background-color: #2e7d32 !important;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }

            .stButton > button:hover {
                background-color: #42a043 !important;
            }

        </style>
    """, unsafe_allow_html=True)


    # ============================
    #        CONTENIDO
    # ============================
    st.markdown("<div class='container'>", unsafe_allow_html=True)

    # LOGO CENTRADO
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png")
    st.markdown("</div>", unsafe_allow_html=True)

    # CAJA DEL LOGIN
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<h2>Inicio de Sesión</h2>", unsafe_allow_html=True)

    # ICONOS E INPUTS
    usuario = st.text_input("Usuario")
    st.markdown("<div class='icon'>👤</div>", unsafe_allow_html=True)

    password = st.text_input("Contraseña", type="password")
    st.markdown("<div class='icon'>🔒</div>", unsafe_allow_html=True)

    # BOTÓN
    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        if not con:
            st.error("❌ No se pudo conectar a la base de datos.")
            return

        cursor = con.cursor(dictionary=True)
        cursor.execute("""
            SELECT Usuario, Rol 
            FROM Empleado
            WHERE Usuario = %s AND Contra = %s
        """, (usuario, password))

        datos = cursor.fetchone()

        if datos:
            st.session_state["usuario"] = datos["Usuario"]
            st.session_state["rol"] = datos["Rol"]
            st.session_state["sesion_iniciada"] = True
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
