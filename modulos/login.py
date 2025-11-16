import streamlit as st
import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="bftcfbzptdyxq4f8afmu-mysql.services.clever-cloud.com",  # host de Clever Cloud
        user="uXXXXXX",        # tu usuario real de Clever Cloud
        password="pXXXXXX",    # tu contraseña real de Clever Cloud
        database="btfcfbzptdyxq4f8afmu",  # nombre exacto de tu base
        port=3306
    )

def login():
    st.title("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        try:
            con = obtener_conexion()
            cur = con.cursor()
            cur.execute("SELECT Usuario, Contra, Rol FROM Empleado WHERE Usuario=%s AND Contra=%s", (usuario, contrasena))
            fila = cur.fetchone()
            con.close()

            if fila:
                st.session_state["sesion_iniciada"] = True
                st.session_state["usuario"] = fila[0]
                st.session_state["rol"] = fila[2]
                st.success("✅ Inicio de sesión exitoso")
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

        except Exception as e:
            st.error(f"Error al conectar con la base de datos: {e}")
