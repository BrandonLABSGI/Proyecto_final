import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

# =====================================
# CONFIGURACIÓN GLOBAL (MÁS IMPORTANTE)
# =====================================
st.set_page_config(
    page_title="Solidaridad CVX",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ELIMINA EL SIDEBAR COMPLETAMENTE
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# EVITA CUALQUIER ESPACIO ARRIBA
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            margin-top: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =============================
# ESTADO DE SESIÓN
# =============================
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None


# =============================
# LÓGICA PRINCIPAL
# =============================
if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    if rol == "Directora":
        interfaz_directiva()

    elif rol == "Promotora":
        interfaz_promotora()

    else:
        st.error("Rol no reconocido.")
        st.session_state.clear()
        st.rerun()

else:
    login()
