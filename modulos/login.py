import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
        <style>
            .card {
                width: 850px;
                margin: 50px auto;
                background: #ffffff;
                border-radius: 18px;
                padding: 25px;
                box-shadow: 0px 4px 40px rgba(0,0,0,0.20);
            }

            .welcome {
                font-size: 30px;
                font-weight: 800;
                color: #0a3161;
                text-align: center;
                margin-top: 20px;
                margin-bottom: 10px;
            }

            .subtitle {
                font-size: 18px;
                text-align: center;
                color: #444444;
                margin-bottom: 25px;
            }

            .login-box {
                margin-top: 25px;
            }

            .stTextInput>div>div>input,
            .stPasswordInput>div>div>input {
                background-color: white !important;
                border-radius: 8px;
                height: 45px;
                border: 1px solid #cccccc;
                color: #000 !important;
            }

            .stButton>button {
                width: 100%;
                height: 45px;
                background-color: #2e7d32;
                color: white;
                border-radius: 8px;
                font-size: 17px;
                margin-top: 18px;
            }

            .stButton>button:hover {
                background-color: #1b5e20 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ============================
    # TARJETA CENTRAL
    # ============================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Imagen
    st.image("modulos/imagenes/ilustracion.png", use_column_width=True)

    # Bienvenida
    st.markdown('<div class="welcome">Bienvenida a Solidaridad CVX</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Sistema exclusivo para socias</div>', unsafe_allow_html=True)

    # ============================
    # FORMULARIO PARA INGRESO
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

    st.markdown('</div>', unsafe_allow_html=True)
