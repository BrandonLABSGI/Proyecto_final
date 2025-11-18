import streamlit as st

from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
# Cuando agregues administrador:
# from modulos.administrador import interfaz_admin

# ----------------------------------------------
# ESTADOS DE SESIÓN
# ----------------------------------------------

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None

# ----------------------------------------------
# REDIRECCIÓN POR ROL
# ----------------------------------------------

if st.session_state["sesion_iniciada"]:

    if st.session_state["rol"] == "directiva":
        interfaz_directiva()

    elif st.session_state["rol"] == "promotora":
        interfaz_promotora()

    elif st.session_state["rol"] == "admin":
        st.write("Panel de administrador (falta agregar módulo).")

    else:
        st.error("⚠ Rol no reconocido.")

else:
    login()
