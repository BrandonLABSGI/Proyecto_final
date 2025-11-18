import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva


if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False


if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    # 🔵 DIRECTOR
    if rol == "Director":
        interfaz_directiva()

    # 🔴 ADMIN
    elif rol == "Administrador":
        st.title("🛠 Panel del Administrador")
        st.info("Acceso limitado. El administrador no puede gestionar asistencia ni multas.")

    # 🟣 PROMOTORA
    elif rol == "Promotora":
        st.title("👩‍💼 Panel de la Promotora")
        st.info("Acceso limitado. La promotora no puede gestionar asistencia ni multas.")

    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

else:
    login()
