import streamlit as st
from modulos.login import login, mostrar_interfaz_unica

# ---------------------------------------------------------
# Función para cerrar sesión
# ---------------------------------------------------------
def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

# ---------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------
def main():
    st.sidebar.title("📋 Menú principal")

    # Inicializar variables de sesión si no existen
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""

    # Si la sesión está activa → mostrar interfaz según rol
    if st.session_state["sesion_iniciada"]:
        st.sidebar.success(f"Sesión iniciada como: {st.session_state['usuario']} ({st.session_state['rol']})")
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)
        mostrar_interfaz_unica()
    else:
        login()

# ---------------------------------------------------------
# Ejecución del programa
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
