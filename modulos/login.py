import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.venta import mostrar_venta

# ---------------------------------------------------------
# Función para verificar usuario con manejo de errores
# ---------------------------------------------------------
def verificar_usuario(usuario, contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None

    try:
        # ✅ Cursor con buffer para evitar errores de lectura
        cursor = con.cursor(buffered=True)
        query = "SELECT Usuario, Rol FROM Empleado WHERE Usuario = %s AND Contra = %s"
        cursor.execute(query, (usuario, contra))
        result = cursor.fetchone()
        return result  # Devuelve (Usuario, Rol) o None si no existe
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
# Módulo principal (por ahora, todos los roles ven ventas)
# ---------------------------------------------------------
def mostrar_interfaz_unica():
    st.sidebar.success(f"👤 Usuario: {st.session_state['usuario']} ({st.session_state['rol']})")
    mostrar_venta()
