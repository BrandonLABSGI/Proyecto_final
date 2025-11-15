import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.venta import mostrar_venta
from modulos.promotora import interfaz_promotora

# ------------------------------------------------------------
# Función para verificar usuario y mostrar interfaz según rol
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
# Interfaz de inicio de sesión
# ------------------------------------------------------------
def login():
    st.title("🔐 Inicio de Sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")
    iniciar = st.button("Iniciar sesión")

    if iniciar:
        datos = verificar_usuario(usuario, contra)

        if datos:
            st.session_state["sesion_iniciada"] = True
            st.session_state["usuario"] = datos["Usuario"]
            st.session_state["rol"] = datos["Rol"]
            st.success(f"Bienvenido, {datos['Usuario']} ({datos['Rol']})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ------------------------------------------------------------
# Redirección según el rol
# ------------------------------------------------------------
def mostrar_interfaz():
    if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
        rol = st.session_state.get("rol")

        if rol == "promotora":
            interfaz_promotora()
        elif rol == "director":
            st.info("👔 Interfaz del Director (en construcción)")
        elif rol == "admin":
            mostrar_venta()  # Por ahora el admin usa el módulo de ventas
        else:
            st.warning("Rol desconocido.")
    else:
        login()
