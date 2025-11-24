import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS PROFESIONALES
    # ============================
    st.markdown("""
        <style>
            .login-box {
                width: 880px;
                max-width: 95%;
                margin: 60px auto;
                display: flex;
                background: #faf9f4;
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0px 4px 40px rgba(0,0,0,0.15);
            }

            .left-panel {
                width: 50%;
                background-color: #ffffff;
            }
            .left-panel img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-right: 1px solid #ececec;
            }

            .right-panel {
                padding: 45px 40px;
                width: 50%;
                background-color: #faf9f4;
            }

            .cvx-title {
                font-size: 30px;
                font-weight: 700;
                color: #0a3161;
                margin-bottom: 30px;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 10px;
                height: 45px;
            }

            .stButton>button {
                background-color: #2e7d32;
                color: white;
                font-size: 17px;
                height: 45px;
                border-radius: 8px;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #1b5e20;
            }
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # CONTENEDOR PRINCIPAL
    # ============================
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    left, right = st.columns([1, 1])

    # ============================
    # PANEL IZQUIERDO – IMAGEN
    # ============================
    with left:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)
        st.image("modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png")
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================
    # PANEL DERECHO – FORMULARIO
    # ============================
    with right:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)

        st.markdown('<div class="cvx-title">Iniciar Sesión</div>', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
