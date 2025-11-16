import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
from modulos.administrador import interfaz_administrador


# --------------------------------------------------------
# INICIALIZAR SESIÓN
# --------------------------------------------------------
if "session_iniciada" not in st.session_state:
    st.session_state["session_iniciada"] = False


# --------------------------------------------------------
# SI NO HAY SESIÓN → MOSTRAR LOGIN
# --------------------------------------------------------
if not st.session_state["session_iniciada"]:
    login()

else:
    # --------------------------------------------------------
    # BARRA LATERAL – MENÚ PRINCIPAL
    # --------------------------------------------------------
    st.sidebar.title("📑 Menú principal")

    usuario = st.session_state["usuario"]
    rol = st.session_state["rol"].lower()

    st.sidebar.success(f"Sesión iniciada como:\n**{usuario} ({st.session_state['rol']})**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["session_iniciada"] = False
        st.session_state["usuario"] = None
        st.session_state["rol"] = None
        st.rerun()

    # --------------------------------------------------------
    # REDIRECCIONAMIENTO SEGÚN ROL
    # --------------------------------------------------------
    if rol == "director":
        interfaz_directiva()

    elif rol == "promotora":
        interfaz_promotora()

    elif rol == "administrador":
        interfaz_administrador()

    else:
        st.error("❌ Rol desconocido. Contacte al administrador del sistema.")
