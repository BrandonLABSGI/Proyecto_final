import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

st.set_page_config(page_title="Gestión de Grupo", layout="wide")

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False
    st.session_state["rol"] = None

if not st.session_state["sesion_iniciada"]:
    login()
else:
    st.sidebar.title("📋 Menú principal")
    st.sidebar.success(f"Sesión iniciada como: {st.session_state['rol']}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.rerun()

    rol = st.session_state["rol"]

    if rol == "Admin" or rol == "Director":
        interfaz_directiva()
    elif rol == "Promotora":
        interfaz_promotora()
    else:
        st.warning("⚠️ Rol no reconocido.")
