import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# PAGO DE PRÉSTAMO – SISTEMA CVX
# ============================================================
def pago_prestamo():

    st.title("💰 Registrar pago de préstamo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    opciones = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("👩 Seleccione una socia", list(opciones.keys()))
    id_socia = opciones[socia_sel]

    # ======================================================
    # PRÉSTAMO ACTIVO
    # ======================================================
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    prestamo = cursor.fetchone()

    if not prestamo:
        st.info("ℹ La socia no tiene un préstamo activo.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    monto = prestamo["Monto prestado"]
    interes_total = prestamo["Interes_total"]
    cuotas = prestamo["Cuotas"]
    saldo_pendiente = float(prestamo["Saldo pendiente"])

    total_a_pagar = monto + interes_total
    cuota_fija = round(total_a_pagar / cuotas, 2)
    interes_por_cuota = round(interes_total / cuotas, 2)

    # ======================================================
    # MOSTRAR DETALLE
    # ======================================================
    st.subheader("📄 Detalle del préstamo")

    info = {
        "ID Préstamo": id_prestamo,
        "Monto prestado": f"${monto:.2f}",
        "Interés total": f"${interes_total:.2f}",
        "Total a pagar": f"${total_a_pagar:.2f}",
        "Cuotas quincenales": cuotas,
        "Cuota fija": f"${cuota_fija:.2f}",
        "Interés por cuota": f"${interes_por_cuota:.2f}",
        "Saldo pendiente": f"${saldo_pendiente:.2f}"
    }

    st.table(pd.DataFrame(info.items(), columns=["Detalle", "Valor"]))

    # ======================================================
    # FORMULARIO DE PAGO
    # ======================================================
    fecha_pago_raw = st.date_input("📅 Fecha del pago", date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    if st.button("💵 Registrar pago"):

        capital_pagado = round(cuota_fija - interes_por_cuota, 2)
        nuevo_saldo = round(saldo_pendiente - cuota_fi
