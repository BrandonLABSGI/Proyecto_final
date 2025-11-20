import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.set_page_config(page_title="Inicio de Sesión", layout="centered")

    # =============================
    #  ESTILOS
    # =============================
    st.markdown("""
        <style>
        body {
            background-color: #f4f6f2;
        }
        .login-box {
            background-color: white;
            padding: 40px;
            border-radius: 18px;
            box-shadow: 0px 4px 18px rgba(0,0,0,0.15);
            width: 380px;
            margin-left: auto;
            margin-right: auto;
        }
        .login-title {
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            color: #0d3b66;
            margin-bottom: 25px;
        }
        .input-label {
            font-size: 16px;
            font-weight: 600;
            color: #0d3b66;
        }
        .stTextInput>div>div>input {
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # =============================
    #  LOGO CENTRADO
    # =============================
    st.image("modulos/imagenes/logo.png", width=140)

    # =============================
    #  CUADRO DE LOGIN
    # =============================
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">Inicio de Sesión</div>', unsafe_allow_html=True)

        st.markdown('<p class="input-label">Usuario</p>', unsafe_allow_html=True)
        usuario = st.text_input("", key="usuario_input")

        st.markdown('<p class="input-label">Contraseña</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", key="password_input")

        if st.button("Iniciar sesión", use_container_width=True):
            con = obtener_conexion()
            if not con:
                st.error("No se puede conectar a la base de datos.")
                return

            cursor = con.cursor(dictionary=True)
            cursor.execute("""
                SELECT Usuario, Rol FROM Empleado
                WHERE Usuario = %s AND Contra = %s
            """, (usuario, password))

            datos = cursor.fetchone()

            if datos:
                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Rol"]
                st.session_state["sesion_iniciada"] = True
                st.success("Ingreso exitoso.")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.markdown('</div>', unsafe_allow_html=True)
