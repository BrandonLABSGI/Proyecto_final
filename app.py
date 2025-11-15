import streamlit as st
from modulos.login import login, mostrar_interfaz_unica

def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

def main():
    st.sidebar.title("📋 Menú principal")

    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False

    if st.session_state["sesion_iniciada"]:
        st.sidebar.success(f"Sesión iniciada como: {st.session_state['usuario']} ({st.session_state['rol']})")
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)
        mostrar_interfaz_unica()
    else:
        login()

if __name__ == "__main__":
    main()
