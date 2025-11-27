import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import asegurar_reunion, registrar_movimiento


# ============================================================
# 💸 REGISTRAR GASTOS DEL GRUPO
# ============================================================
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del gasto:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Crear o reparar reunión de caja
    id_caja = asegurar_reunion(fecha)

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable del gasto").strip()

    # --------------------------------------------------------
    # DUI VALIDADO (solo 9 dígitos)
    # --------------------------------------------------------
    dui_raw = st.text_input("DUI (9 dígitos):", max_chars=9).strip()

    if dui_raw and (not dui_raw.isdigit() or len(dui_raw) != 9):
        st.warning("⚠ El DUI debe tener exactamente 9 dígitos numéricos.")
        return

    # --------------------------------------------------------
    # TIPO DE GASTO
    # --------------------------------------------------------
    categoria = st.text_input("Categoría del gasto (ejemplo: Materiales, Transporte)").strip()

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($):", min_value=0.00, step=0.25)

    if monto <= 0:
        st.info("Ingrese un monto mayor a cero.")
        return

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        # Registrar movimiento en caja como EGRESO
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Gasto – {categoria}",
            monto=monto
        )

        # Registrar gasto en tabla Gasto
        cursor.execute("""
            INSERT INTO Gasto (Responsable, DUI, Categoria, Monto, Fecha)
            VALUES (%s, %s, %s, %s, %s)
        """, (responsable, dui_raw, categoria, Decimal(str(monto)), fecha))

        # Actualizar caja general
        cursor.execute("""
            UPDATE caja_general
            SET saldo_actual = saldo_actual - %s
            WHERE id = 1
        """, (Decimal(str(monto)),))

        con.commit()

        st.success("Gasto registrado correctamente.")
        st.rerun()

    # --------------------------------------------------------
    # LISTADO DE GASTOS DEL DÍA
    # --------------------------------------------------------
    cursor.execute("""
        SELECT Id_Gasto, Responsable, Categoria, Monto
        FROM Gasto
        WHERE Fecha=%s
        ORDER BY Id_Gasto ASC
    """, (fecha,))

    registros = cursor.fetchall()

    if registros:
        st.subheader("📋 Gastos registrados en esta fecha")
        import pandas as pd
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
