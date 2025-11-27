import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion
from modulos.caja import (
    obtener_o_crear_reunion,
    obtener_saldo_actual,
)

# ====================================================================
# 🔵 OBTENER MOVIMIENTOS DEL DÍA
# ====================================================================
def obtener_movimientos_dia(id_caja):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja=%s
        ORDER BY id_mov ASC
    """, (id_caja,))

    return cursor.fetchall()


# ====================================================================
# 🔵 OBTENER RESUMEN DEL DÍA
# ====================================================================
def obtener_resumen_dia(fecha):

    # 🔥 Esta función también corrige el saldo_inicial si estaba incorrecto
    id_caja = obtener_o_crear_reunion(fecha)

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT saldo_inicial, ingresos, egresos, saldo_final, dia_cerrado
        FROM caja_reunion
        WHERE id_caja=%s
    """, (id_caja,))
    resumen = cursor.fetchone()

    return id_caja, resumen


# ====================================================================
# 📊 PANTALLA PRINCIPAL — REPORTE DE CAJA
# ====================================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Obtener todas las fechas existentes
    cursor.execute("SELECT fecha FROM caja_reunion ORDER BY fecha ASC")
    fechas = [str(f["fecha"]) for f in cursor.fetchall()]

    if not fechas:
        st.warning("⚠ No hay registros en la caja todavía.")
        return

    # Selección de fecha
    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas, index=len(fechas)-1)

    # Obtener datos del día
    id_caja, resumen = obtener_resumen_dia(fecha_sel)

    saldo_inicial = float(resumen["saldo_inicial"])
    ingresos = float(resumen["ingresos"])
    egresos = float(resumen["egresos"])
    saldo_final = float(resumen["saldo_final"])
    dia_cerrado = resumen["dia_cerrado"]

    # ============================================================
    # 🔵 Mostrar resumen del día
    # ============================================================
    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Saldo Inicial", f"${saldo_inicial:,.2f}")
    with col2:
        st.metric("Ingresos", f"${ingresos:,.2f}")
    with col3:
        st.metric("Egresos", f"${egresos:,.2f}")

    st.info(f"💰 Saldo Final del día: **${saldo_final:,.2f}**")

    # ============================================================
    # 🔵 Movimientos del día
    # ============================================================
    st.markdown("---")
    st.subheader("📄 Movimientos del día")

    movimientos = obtener_movimientos_dia(id_caja)

    if movimientos:
        df = pd.DataFrame(movimientos)
        st.dataframe(df, hide_index=True)
    else:
        st.warning("No hay movimientos registrados en este día.")

    # ============================================================
    # 🔵 CIERRE DEL DÍA (FUNCIONA CON COLUMNA dia_cerrado)
    # ============================================================
    st.markdown("---")
    st.subheader("🧾 Cierre del día")

    if dia_cerrado == 0:
        st.warning("⚠ Este día no está cerrado.")

        if st.button("🔒 Cerrar este día definitivamente"):

            cursor.execute("""
                UPDATE caja_reunion
                SET dia_cerrado = 1
                WHERE id_caja = %s
            """, (id_caja,))
            con.commit()

            st.success("🎉 Día cerrado correctamente.")
            st.rerun()

    else:
        st.success("✔ Este día ya está cerrado.")

    # ============================================================
    # 🔵 Mostrar saldo actual general
    # ============================================================
    st.markdown("---")
    saldo_actual = obtener_saldo_actual()
    st.info(f"⭐ **Saldo actual de la caja: ${saldo_actual:,.2f}**")
