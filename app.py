import streamlit as st

from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
from modulos.administrador import interfaz_admin

# ============================================================
# ESTADO DE SESIÓN
# ============================================================

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None

if "id_empleado" not in st.session_state:
    st.session_state["id_empleado"] = None


# ============================================================
# VALIDACIÓN GENERAL
# ============================================================
def acceso_restringido(rol_requerido):
    rol_actual = st.session_state.get("rol", None)

    if not st.session_state.get("sesion_iniciada", False):
        st.error("Debe iniciar sesión primero.")
        st.session_state.clear()
        st.rerun()

    if rol_actual != rol_requerido:
        st.error("⛔ No tiene permisos para acceder a esta sección.")
        st.session_state.clear()
        st.rerun()


# ============================================================
# LÓGICA PRINCIPAL DE NAVEGACIÓN
# ============================================================

if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    # DIRECTOR
    if rol == "Director":
        acceso_restringido("Director")
        interfaz_directiva()

    # PROMOTORA
    elif rol == "Promotora":
        acceso_restringido("Promotora")
        interfaz_promotora()

    # ADMINISTRADOR
    elif rol == "Administrador":
        acceso_restringido("Administrador")
        interfaz_admin()

    # ROL DESCONOCIDO
    else:
        st.error(f"❌ Rol no reconocido: {rol}")
        st.session_state.clear()
        st.rerun()

    # BOTÓN CERRAR SESIÓN (SIEMPRE DISPONIBLE)
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

else:
    login()
