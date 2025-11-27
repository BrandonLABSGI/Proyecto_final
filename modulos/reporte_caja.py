import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion


# ============================================================
# 📊 REPORTE DE CAJA COMPLETO — CON GRÁFICAS RESTAURADAS
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Obtener todas las fechas registradas en caja_reunion
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas = [row["fecha"] for row in cur.fetchall()]

    if not fechas:
        st.warning("⚠ No hay datos registrados en la caja.")
        return

    fecha_sel = st.selectbox("📅 Seleccione la fecha del reporte:", fechas)
    fecha_str = fecha_sel.strftime("%Y-%m-%d")

    # ============================================================
    # DATOS DE LA REUNIÓN
    # ============================================================
    cur.execute("""
        SELECT saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha_str,))
    reunion = cur.fetchone()

    if not reunion:
        st.error("⚠ No existe un registro de caja para esta fecha.")
        return

    saldo_inicial = Decimal(reunion["saldo_inicial"])
    ingresos = Decimal(reunion["ingresos"])
    egresos = Decimal(reunion["egresos"])
    saldo_final = Decimal(reunion["saldo_final"])

    # ============================================================
    # MOSTRAR RESUMEN
    # ============================================================
    st.subheader(f"📘 Resumen del día — {fecha_str}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos", f"${ingresos:.2f}")
    col3.metric("Egresos", f"${egresos:.2f}")

    st.metric("💰 Saldo Final", f"${saldo_final:.2f}")

    st.info(
        f"🔵 Saldo inicial + ingresos – egresos\n"
        f"= {saldo_inicial} + {ingresos} – {egresos}\n"
        f"= ${saldo_final:.2f}"
    )

    # ============================================================
    # MOVIMIENTOS DEL DÍA
    # ============================================================
    st.subheader("📄 Movimientos registrados")

    cur.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = (
            SELECT id_caja FROM caja_reunion WHERE fecha=%s
        )
        ORDER BY id_mov ASC
    """, (fecha_str,))

    movimientos = cur.fetchall()

    if movimientos:
        df = pd.DataFrame(movimientos)
        st.dataframe(df, use_container_width=True)

        # ============================================================
        # 🔵 GRÁFICAS RESTAURADAS (Versión Streamlit)
        # ============================================================
        st.subheader("📊 Gráfica de Ingresos vs Egresos")

        graf_df = pd.DataFrame({
            "Tipo": ["Ingresos", "Egresos"],
            "Monto": [float(ingresos), float(egresos)]
        })

        st.bar_chart(graf_df.set_index("Tipo"))

        # Gráfica detallada por categorías
        st.subheader("📊 Distribución por categorías")

        cat_df = pd.DataFrame(movimientos)
        if not cat_df.empty:
            pivot = cat_df.groupby("categoria").sum(numeric_only=True)
            st.bar_chart(pivot)

    else:
        st.info("📭 No hay movimientos registrados en este día.")

    # ============================================================
    # DESCARGA DEL PDF
    # ============================================================
    st.subheader("📄 Descargar reporte en PDF")

    if st.button("📥 Generar PDF"):

        nombre_pdf = f"Reporte_Caja_{fecha_str}.pdf"
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        story.append(Paragraph(f"Reporte de Caja — {fecha_str}", styles["Title"]))
        story.append(Spacer(1, 12))

        # Tabla resumen
        data_resumen = [
            ["Saldo Inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Saldo Final", f"${saldo_final:.2f}"],
        ]
        t = Table(data_resumen)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("GRID", (0, 0), (-1, -1), 1, colors.gray)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Movimientos
        if movimientos:
            story.append(Paragraph("Movimientos del día:", styles["Heading2"]))
            data = [["Tipo", "Categoría", "Monto"]] + [
                [m["tipo"], m["categoria"], f"${m['monto']}"] for m in movimientos
            ]
            tabla_mov = Table(data)
            tabla_mov.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 1, colors.gray)
            ]))
            story.append(tabla_mov)

        doc.build(story)
        st.success("📄 PDF generado correctamente. Descargando...")
        st.download_button("Descargar PDF", open(nombre_pdf, "rb"), file_name=nombre_pdf)
