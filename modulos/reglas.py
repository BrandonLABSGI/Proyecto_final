import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.reglas_utils import obtener_reglas, guardar_reglas


# ============================================================
# 📘 GESTIONAR REGLAS INTERNAS DEL GRUPO — VERSIÓN FINAL
# ============================================================
def gestionar_reglas():

    st.title("📘 Reglas Internas del Grupo")

    id_grupo = 1  # Tu sistema actual trabaja con un único grupo

    reglas = obtener_reglas(id_grupo)

    ciclo_inicio = reglas.get("ciclo_inicio", "")
    ciclo_fin = reglas.get("ciclo_fin", "")
    monto_ahorro = reglas.get("monto_ahorro", 0.00)
    multa_inasistencia = reglas.get("multa_inasistencia", 0.00)
    multa_mora = reglas.get("multa_mora", 0.00)

    # --------------------------------------------------------
    # FORMULARIO
    # --------------------------------------------------------
    st.subheader("📅 Fechas del ciclo")
    col1, col2 = st.columns(2)
    f_inicio = col1.date_input("Fecha inicio del ciclo:", 
                               value=date.fromisoformat(ciclo_inicio) if ciclo_inicio else date.today())
    f_fin = col2.date_input("Fecha fin del ciclo:", 
                            value=date.fromisoformat(ciclo_fin) if ciclo_fin else date.today())

    st.subheader("💵 Parametrización financiera")
    ahorro = st.number_input("Monto de ahorro obligatorio ($):", min_value=0.00, value=float(monto_ahorro))
    multa_ina = st.number_input("Multa por inasistencia ($):", min_value=0.00, value=float(multa_inasistencia))
    multa_mora_v = st.number_input("Multa por mora ($):", min_value=0.00, value=float(multa_mora))

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Guardar reglas"):

        guardar_reglas(
            id_grupo=id_grupo,
            ciclo_inicio=f_inicio.strftime("%Y-%m-%d"),
            ciclo_fin=f_fin.strftime("%Y-%m-%d"),
            monto_ahorro=ahorro,
            multa_inasistencia=multa_ina,
            multa_mora=multa_mora_v
        )

        st.success("✔ Reglas internas guardadas exitosamente.")
        st.rerun()

    # --------------------------------------------------------
    # MOSTRAR REGLAS ACTUALES
    # --------------------------------------------------------
    st.markdown("### 📋 Reglas actuales")

    st.info(f"""
    **Ciclo:** {f_inicio} → {f_fin}

    **Ahorro obligatorio:** ${ahorro:,.2f}  
    **Multa por inasistencia:** ${multa_ina:,.2f}  
    **Multa por mora:** ${multa_mora_v:,.2f}  
    """)
