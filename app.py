import streamlit as st
from modulos.login import login

# Si NO hay sesión, pedir login
if not st.session_state.get("sesion_iniciada"):
    login()
    st.stop()  # Evita que el resto del código siga sin login


