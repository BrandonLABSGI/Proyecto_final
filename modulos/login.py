import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.venta import mostrar_venta
from modulos.promotora import interfaz_promotora

# ------------------------------------------------------------
# Función para verificar usuario y rol
# ------------------------------------------------------------
def verificar_usuario(usuario, contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor(dictionary=True)
        consulta = "SELECT Usuario, Rol FROM Empleado WHERE Usuario = %s AND Contra = %s"
        cursor.execute(consulta, (usuario, contra))
        return cursor.fetchone()
    except Exception as e:
        st.error(f"❌ Error en la verificación: {e}")
        return None
    finally:
        cursor.close()
        con.close()

# ------------------------------------------------------------
# Pantalla de inicio de sesión
# ------------------------------------------------------------
def login():
    st.title("🔐 Inicio de sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        datos = verificar_usuario(usuario, contra)

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = datos["Usuario"]
            st.session_state["rol"] = datos["Rol"]
            st.success(f"✅ Bienvenido, {datos['Usuario']} ({datos['Rol']})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ------------------------------------------------------------
# Mostrar interfaz según el rol
# ------------------------------------------------------------
def mostrar_interfaz_unica():
    rol = st.session_state.get("rol", "").lower()

    if rol == "promotora":
        interfaz_promotora()

    elif rol == "admin":
        mostrar_venta()

    elif rol == "director":
        st.info("👔 Interfaz del Director (en desarrollo)")

    else:
        st.warning("⚠️ Rol no reconocido, contacta al administrador.")
