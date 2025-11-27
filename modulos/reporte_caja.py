import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
import matplotlib.pyplot as plt
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, obtener_saldo_actual
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📌 REPORTE COMPLETO DE CAJA — VERSIÓN DEFINITIVA
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ REGLAS INTERNAS DE CICLO (Opcional)
    # ============================================================
    reglas = obtener_reglas()

    if reglas:
        st.info(
            f"📌 Ciclo iniciado el **{reglas.get('ciclo_inicio', '---')}**, "
            f"termina el **{reglas.get('ciclo_fin', '---')}**"
        )

    # ============================================================
    # 2️⃣ Selección de fecha de reporte
    # ============================================================
    fecha_raw = st.date_input("📅 Seleccione fecha a consultar:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Garantizar reunión para mostrar datos correctos
    id_caja = obtener_o_crear_reunion(fecha)

    # ============================================================
    # 3️⃣ Cargar datos de caja para la fecha
    # ============================================================
    cursor.execute("""
        SELECT *
        FROM caja_reunion
        WHERE fecha=%s
    """, (fecha,))
    reunion = cursor.fetchone()

    if not reunion:
        st.warning("⚠ No hay información de caja registrada para este día.")
        return

    saldo_inicial = Decimal(str(reunion["saldo_inicial"]))
    ingresos = Decimal(str(reunion["ingresos"]))
    egresos = Decimal(str(reunion["egresos"]))
    saldo_final = Decimal(str(reunion["saldo_final"]))

    # ============================================================
    # 4️⃣ Resumen superior (en números grandes)
    # ============================================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saldo inicial", f"${saldo_inicial:,.2f}")
    col2.metric("Ingresos", f"${ingresos:,.2f}")
    col3.metric("Egresos", f"${egresos:,.2f}")
    col4.metric("Saldo final", f"${saldo_final:,.2f}")

    # ============================================================
    # 5️⃣ Mostrar movimientos del día
    # ============================================================
    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja=%s
        ORDER BY id_movimiento ASC
    """, (id_caja,))

    movimientos = cursor.fetchall()

    st.markdown("### 📋 Movimientos del día")
    if movimientos:
        df = pd.DataFrame(movimientos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay movimientos registrados para este día.")

    # ============================================================
    # 6️⃣ Gráfica restaurada (como tu versión original)
    # ============================================================
    try:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(["Ingresos", "Egresos"], [float(ingresos), float(egresos)])
        ax.set_title("Comparación de movimientos del día")
        ax.set_ylabel("Monto ($)")
        st.pyplot(fig)
    except:
        st.warning("⚠ No se pudo generar la gráfica. Verifica matplotlib.")

    # ============================================================
    # 7️⃣ BOTÓN PARA GENERAR PDF
    # ============================================================
    def generar_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Reporte de Caja — Solidaridad CVX", styles["Title"]))
        story.append(Spacer(1, 12))

        # Tabla resumen
        tabla_resumen = [
            ["Saldo Inicial", f"${saldo_inicial:,.2f}"],
            ["Ingresos", f"${ingresos:,.2f}"],
            ["Egresos", f"${egresos:,.2f}"],
            ["Saldo Final", f"${saldo_final:,.2f}"],
        ]

        t = Table(tabla_resumen, colWidths=[150, 150])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER")
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Movimientos
        if movimientos:
            story.append(Paragraph("Movimientos del día", styles["Heading2"]))
            mov_table = [["Tipo", "Categoría", "Monto"]]

            for m in movimientos:
                mov_table.append([m["tipo"], m["categoria"], f"${m['monto']:,.2f}"])

            t2 = Table(mov_table, colWidths=[120, 250, 100])
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT")
            ]))
            story.append(t2)

        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_buffer = generar_pdf()
    st.download_button(
        label="📄 Descargar reporte en PDF",
        data=pdf_buffer,
        file_name=f"Reporte_Caja_{fecha}.pdf",
        mime="application/pdf",
    )
