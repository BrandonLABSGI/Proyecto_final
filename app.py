import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

# Verificar sesión
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if not st.session_state["sesion_iniciada"]:
    login()
else:
    st.sidebar.title("📋 Menú principal")
    st.sidebar.success(f"Sesión iniciada como: {st.session_state['usuario']} ({st.session_state['rol']})")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    rol = st.session_state["rol"].lower()

    # Redirigir según rol
    if rol == "director":
        interfaz_directiva()

    elif rol == "promotora":
        interfaz_promotora()

    elif rol == "admin":
        st.title("Panel del Administrador")
        st.info("Aquí podrás gestionar usuarios y roles.")

