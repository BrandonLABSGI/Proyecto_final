import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ======= CSS SEGURO =======
    st.markdown("""
        <style>
        .login-box {
            background-color: #1F232A;
            padding: 30px;
            border-radius: 15px;
            width: 350px;
            margin-left: auto;
            margin-right: auto;
            margin-top: 80px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.45);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .login-title {
            font-size: 30px;
            color: #FFD43B;
            text-align: center;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .login-sub {
            font-size: 15px;
            color: #ffffff;
            text-align: center;
            margin-bottom: 20px;
        }

        .stTextInput input {
            background-color: #2C3038 !important;
            color: white !important;
            border-radius: 8px !important;
        }

        .stButton button {
            width: 100%;
            background-color: #FFD43B !important;
            color: black !important;
            border-radius: 8px;
            height: 45px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # ========= CONTENIDO =========
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.markdown('<div class="login-title">🔒 Solidaridad CVX</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Bienvenido a tu sistema Solidaridad CVX</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub" style="font-size:13px; margin-top:-10px;">Ingrese sus credenciales para acceder</div>', unsafe_allow_html=True)

    usuario = st.text_input("👤 Usuario")
    password = st.text_input("🔑 Contraseña", type="password")

    iniciar = st.button("Iniciar sesión")

    st.markdown("</div>", unsafe_allow_html=True)

    # ========= LÓGICA =========
    if iniciar:
        con = obtener_conexion()
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
            st.success("Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")
