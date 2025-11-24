import streamlit as st
import base64

# ==============================
# FUNCIÓN PARA CENTRAR IMAGEN
# ==============================
def centered_image(img_path, width=260):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-top:40px;">
            <img src="data:image/png;base64,{base64.b64encode(open(img_path, "rb").read()).decode()}" 
                 width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================
# LOGIN
# ==============================
def login():

    # --- RUTA CORRECTA ---
    centered_image("imagenes/senoras.png", width=280)

    st.markdown(
        "<h1 style='text-align:center; margin-top:15px;'>Bienvenida a Solidaridad CVX</h1>",
        unsafe_allow_html=True
    )

    st.write("")  

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        st.success("Procesando...")
