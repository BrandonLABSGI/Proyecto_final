import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # Ocultar header/footer
    hide_st = """
        <style>
            header, footer {visibility: hidden;}
            #MainMenu {visibility:hidden;}
        </style>
    """
    st.markdown(hide_st, unsafe_allow_html=True)

    # =============================
    # CONTENEDOR TOTAL
    # =============================
    st.markdown("""
        <style>
            .login-wrapper {
                position: relative;
                width: 900px;
                margin: auto;
            }

            .login-bg {
                width: 100%;
                border-radius: 20px;
            }

            /* FORMULARIO SUPERPUESTO */
            .form-container {
                position: absolute;
                top: 190px;      /* Ajusta la altura */
                left: 515px;     /* Ajusta la posición horizontal */
                width: 310px;
            }

            .form-container label {
                font-size: 16px !important;
                font-weight: 600;
            }

            .form-container .stTextInput>div>div>input,
            .form-container .stPasswordInput>div>div>input {
                height: 40px;
                font-size: 16px;
            }

            .form-container .stButton>button {
                width: 100%;
                height: 42px;
                background-color: #2e7d32;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

    # =============================
    # TARJETA + FORMULARIO
    # =============================
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

    # IMAGEN GRANDE DEL LOGIN
    st.markdown(
        """
        <img src="modulos/imagenes/9e001816-7c44-4523-8a27-4b5bb730a1fa.png"
             class="login-bg">
        """,
        unsafe_allow_html=True
    )

    # FORMULARIO SUPERPUESTO (REAL)
    st.markdown('<div class="form-container">', unsafe_allow_html=True)

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
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    st.markdown('</div></div>', unsafe_allow_html=True)
