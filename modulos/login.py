import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.venta import mostrar_venta
from modulos.promotora import interfaz_promotora

# ---------------------------------------------------------
# Función para verificar usuario
# ---------------------------------------------------------
def verificar_usuario(usuario, contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        cursor = con.cursor()
        query = "SELECT Usuario, Rol FROM Empleado WHERE Usuario = %s AND Contra = %s"
        cursor.execute(query, (usuario, contra))
        result = cursor.fetchone()
        return result  # (Usuario, Rol)
    except Exception as e:
        st.error(f"❌ Error al verificar usuario: {e}")
        return None
    finally:
        con.close()

# ---------------------------------------------------------
# Interfaz de inicio de sesión
# ---------------------------------------------------------
def login():
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False

    st.title("🔐 Inicio de Sesión - SGI")
    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        resultado = verificar_usuario(usuario, contra)
        if resultado:
            st.session_state["usuario"] = resultado[0]
            st.session_state["rol"] = resultado[1]
            st.session_state["sesion_iniciada"] = True
            st.success(f"✅ Bienvenido {resultado[0]} ({resultado[1]})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ---------------------------------------------------------
# Interfaz según el rol del usuario
# ---------------------------------------------------------
def mostrar_interfaz_unica():
    rol = st.session_state.get("rol", "")

    # Redirección según el rol
    if rol == "promotora":
        interfaz_promotora()
    else:
        mostrar_venta()  # otros roles siguen viendo ventas por ahora
