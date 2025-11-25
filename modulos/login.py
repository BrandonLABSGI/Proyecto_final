import streamlit as st
import mysql.connector
from modulos.conexion import obtener_conexion

# ============================================================
# LOGIN — SISTEMA CVX
# ============================================================

def login():

    st.markdown(
        """
        <style>
        .login-box {
            background-color: #111418;
            padding: 25px;
            border-radius: 18px;
            width: 90%;
            max-width: 380px;
            margin: auto;
            box-shadow: 0px 0px 12px rgba(255,255,255,0.08);
        }
        .title {
            text-align: center;
            color: white;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 110px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown(
        "<img class='logo' src='https://i.imgur.com/B4HqfUU.png'>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='title'>Inicio de sesión</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # FORMULARIO
    # ----------------------------------------------------
    usuario = st.text_input("👤 Usuario")
    contra = st.text_input("🔒 Contraseña", type="password")

    if st.button("Ingresar", use_container_width=True):
        if usuario.strip() == "" or contra.strip() == "":
            st.warning("Debe ingresar usuario y contraseña.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor(dictionary=True)

                cursor.execute("""
                    SELECT Id_Empleado, Usuario, Contra, Rol
                    FROM Empleado
                    WHERE Usuario=%s AND Contra=%s
                    LIMIT 1
                """, (usuario, contra))

                row = cursor.fetchone()

                if row:
                    st.session_state["sesion_iniciada"] = True
                    st.session_state["usuario"] = row["Usuario"]
                    st.session_state["rol"] = row["Rol"]
                    st.session_state["id_empleado"] = row["Id_Empleado"]  # <<--- IMPORTANTE

                    st.success("Ingreso exitoso. Redirigiendo…")
                    st.rerun()

                else:
                    st.error("Usuario o contraseña incorrectos.")

            except mysql.connector.Error:
                st.error("Error al conectar con la base de datos.")

    st.markdown("</div>", unsafe_allow_html=True)
