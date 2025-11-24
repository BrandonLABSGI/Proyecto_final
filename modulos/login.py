import streamlit as st
import base64

def login():
    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # ============================
    # Cargar imagen embebida BASE64
    # ============================
    encoded_image = """
    iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgCAYAAADx...
    """  # ← Te pongo abajo la imagen real

    # Convertir a HTML IMG
    image_html = f"""
        <img src="data:image/png;base64,{encoded_image}"
             style="width:100%; border-radius:18px; box-shadow:0 4px 40px rgba(0,0,0,0.25);" />
    """

    # ============================
    # Estilos globales
    # ============================
    st.markdown("""
        <style>
            header, footer {visibility: hidden !important;}
            .block-container {padding-top: 10px !important;}
            label { font-size: 18px !important; color: white !important; }
            .stTextInput>div>div>input, .stPasswordInput>div>div>input {
                background: #ffffff !important;
                border-radius: 10px !important;
                height: 45px !important;
                font-size: 18px !important;
            }
            .stButton>button {
                width: 100%;
                background: #2e7d32;
                font-size: 18px;
                height: 45px;
                border-radius: 10px;
                color: white;
            }
            .stButton>button:hover {
                background: #1b5e20 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(image_html, unsafe_allow_html=True)

    st.write("### Iniciar Sesión")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        import mysql.connector
        from modulos.conexion import obtener_conexion

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
