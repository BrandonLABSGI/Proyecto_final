import streamlit as st
import base64
from modulos.conexion import obtener_conexion

def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # =========================
    # CARGAR IMAGEN EN BASE64
    # =========================
    # Imagen del ejemplo del login (socias sentadas)
    login_image_base64 = """
    iVBORw0KGgoAAAANSUhEUgAAA... (ACORTADO) ...
    """  # <<<< te la voy a colocar COMPLETA en el siguiente mensaje porque es muy larga

    # Convertimos la imagen en HTML
    login_html = f"""
    <div style="display:flex; justify-content:center; margin-top:40px;">
        <div style="
            width:900px;
            background:#ffffff;
            border-radius:18px;
            box-shadow:0px 4px 40px rgba(0,0,0,0.20);
            overflow:hidden;
            display:flex;
        ">
            <!-- PANEL IZQUIERDO -->
            <div style="width:50%; background:#fff;">
                <img src="data:image/png;base64,{login_image_base64}"
                     style="width:100%; height:100%; object-fit:cover;">
            </div>

            <!-- PANEL DERECHO -->
            <div style="width:50%; padding:45px 40px; background:#faf9f4;">
                <h1 style="font-size:32px; font-weight:800; color:#0a3161; margin-bottom:25px;">
                    Iniciar Sesión
                </h1>

                <div id="form-container"></div>
            </div>
        </div>
    </div>
    """

    st.markdown(login_html, unsafe_allow_html=True)

    # =============================
    # FORMULARIO DE LOGIN (REAL)
    # =============================
    with st.container():
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
