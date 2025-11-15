import streamlit as st
from modulos.venta import mostrar_venta
from modulos.promotora import panel_promotora
from modulos.config.conexion import obtener_conexion

# --------------------------
# FUNCIÓN DE LOGIN
# --------------------------
def login():
    st.title("🔐 Inicio de Sesión")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    btn = st.button("Iniciar sesión")

    if btn:
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM Empleado WHERE Usuario = %s AND Contra = %s", (usuario, contrasena))
        datos = cur.fetchone()
        cur.close()
        con.close()

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = datos["Usuario"]
            st.session_state["rol"] = datos["Rol"]
            st.session_state["id_empleado"] = datos["Id_Empleado"]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")


# --------------------------
# FUNCIÓN PRINCIPAL SEGÚN ROL
# --------------------------
def mostrar_interfaz_unica():
    rol = st.session_state.get("rol", "").lower()

    if rol == "admin":
        st.success("✅ Bienvenido Administrador")
        mostrar_venta()

    elif rol == "promotora":
        panel_promotora(id_promotora=st.session_state["id_empleado"])

    else:
        st.warning("⚠️ Rol no reconocido, contacta al administrador.")
