import streamlit as st
import base64

# =====================================================
# CONVERTIR IMAGEN A BASE64
# =====================================================
def load_image_base64():
    image_path = "modulos/imagenes/50513df8-1b40-4a28-a72d-1ab6a202cfc6.png"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return encoded


# =====================================================
# LOGIN
# =====================================================
def login():

    st.set_page_config(page_title="Ingreso — Solidaridad CVX", layout="centered")

    # Ocultar header/footer
    st.markdown("""
        <style>
            header, footer {visibility: hidden !important;}
            .block-container {padding-top: 30px !important;}
        </style>
    """, unsafe_allow_html=True)

    # Cargar la imagen en base64
    img_base64 = load_image_base64()

    # Mostrar imagen
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center;">
            <img src="data:image/png;base64,{img_base64}"
                 style="width:90%; max-width:900px; border-radius:20px;" />
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")  
    st.write("### Iniciar Sesión")

    # Campos de login
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

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
