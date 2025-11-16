import streamlit as st
from modulos.login import login, mostrar_interfaz_unica
from modulos.promotora import interfaz_promotora
from modulos.directiva import interfaz_directiva

# --------------------------------------------------
# 🚪 FUNCIÓN PARA CERRAR SESIÓN
# --------------------------------------------------
def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

# --------------------------------------------------
# 🏠 APLICACIÓN PRINCIPAL
# --------------------------------------------------
def main():
    st.sidebar.title("📋 Menú principal")

    # Inicializar estado de sesión
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False
    if "rol" not in st.session_state:
        st.session_state["rol"] = ""

    # Si hay sesión activa → mostrar panel correspondiente
    if st.session_state["sesion_iniciada"]:
        usuario = st.session_state["usuario"]
        rol = st.session_state["rol"]

        st.sidebar.success(f"Sesión iniciada como: {usuario} ({rol})")
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)

        # Mostrar interfaz según el rol
        if rol == "Promotora":
            interfaz_promotora()
        elif rol == "Directiva":
            interfaz_directiva()
        elif rol == "Administrador":
            st.title("🛠️ Panel de Administrador")
            st.info("Visualiza el panorama completo de los distritos y grupos.")
            st.warning("🔧 Este módulo está en desarrollo.")
        else:
            st.warning("⚠️ Rol no reconocido, contacta al administrador.")
    else:
        # Si no hay sesión iniciada → mostrar login
        login()

# --------------------------------------------------
# 🚀 EJECUCIÓN PRINCIPAL
# --------------------------------------------------
if __name__ == "__main__":
    main()
