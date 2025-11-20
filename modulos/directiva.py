import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# Módulos del sistema
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.asistencia import pagina_asistencia
from modulos.caja import obtener_saldo_por_fecha, mostrar_reporte_caja
from modulos.promotora import pagina_multas
from modulos.promotora import pagina_registro_socias


# ============================================================
# PANEL PRINCIPAL
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ============================================================
    # FECHA CENTRAL (todo depende de esta fecha)
    # ============================================================
    st.markdown("### 📅 Seleccione la fecha de reunión principal:")
    
    # Guardar fecha global en sesión
    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    nueva_fecha = st.date_input(
        "Fecha central de trabajo",
        value=pd.to_datetime(st.session_state["fecha_global"])
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = nueva_fecha

    # ============================================================
    # SALDO SUPERIOR (UNIFICADO CON REPORTE)
    # ============================================================
    try:
        saldo = obtener_saldo_por_fecha(st.session_state["fecha_global"])
        st.info(f"💰 Saldo actual de caja ({st.session_state['fecha_global']}): **${saldo:.2f}**")

    except Exception as e:
        st.error(f"Error al obtener saldo de caja: {e}")

    # ============================================================
    # BOTÓN CERRAR SESIÓN
    # ============================================================
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ============================================================
    # MENÚ LATERAL
    # ============================================================
    menu = st.sidebar.radio(
        "Selección rápida:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Reporte de caja"
        ]
    )

    # ============================================================
    # OPCIONES
    # ============================================================
    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Reporte de caja":
        mostrar_reporte_caja()
