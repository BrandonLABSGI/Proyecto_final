import streamlit as st
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion, obtener_saldo_actual


# ==========================================================
# 🔐 FUNCION CENTRAL → EVITA CREAR REUNIÓN PREMATURA
# ==========================================================
def asegurar_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha=%s", (fecha,))
    row = cursor.fetchone()
    if row:
        return row["id_caja"]
    return obtener_o_crear_reunion(fecha)


# ==========================================================
# 💸 REGISTRAR GASTOS
# ==========================================================
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    fecha_dt = st.date_input("Fecha del gasto:", date.today())
    fecha = fecha_dt.strftime("%Y-%m-%d")

    responsable = st.text_input("Responsable:").strip()
    descripcion = st.text_input("Descripción:").strip()

    monto_raw = st.number_input("Monto del gasto:", min_value=0.01, step=0.01)
    monto = Decimal(str(monto_raw))

    saldo_real = float(obtener_saldo_actual())

    if monto > saldo_real:
        st.error("❌ No puedes registrar un gasto mayor al saldo disponible.")
        return

    if st.button("Registrar gasto"):

        id_caja = asegurar_reunion(fecha)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"{descripcion} — Responsable: {responsable}",
            monto=monto
        )

        st.success("✔ Gasto registrado con éxito.")
        st.rerun()
