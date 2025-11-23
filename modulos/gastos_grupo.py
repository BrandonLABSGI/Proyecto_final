import streamlit as st
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_actual


# ------------------------------------------------------------
# PDF – Comprobante de gasto
# ------------------------------------------------------------
def generar_pdf_gasto(fecha, categoria, monto, saldo_antes, saldo_despues):
    nombre_pdf = f"gasto_{fecha}.pdf"
    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)

    estilos = getSampleStyleSheet()
    contenido = []

    titulo = Paragraph("<b>Comprobante de Gasto</b>", estilos["Title"])
    contenido.append(titulo)

    data = [
        ["Campo", "Detalle"],
        ["Fecha", fecha],
        ["Categoría", categoria],
        ["Monto del gasto", f"${monto:.2f}"],
        ["Saldo antes del gasto", f"${saldo_antes:.2f}"],
        ["Saldo después del gasto", f"${saldo_despues:.2f}"],
    ]

    tabla = Table(data, colWidths=[180, 300])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    contenido.append(tabla)
    doc.build(contenido)

    return nombre_pdf


# ------------------------------------------------------------
# Registrar gastos del grupo
# ------------------------------------------------------------
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA DEL GASTO
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE (lo guardamos dentro de categoría)
    # --------------------------------------------------------
    responsable = st.text_input("Responsable del gasto").strip()

    # --------------------------------------------------------
    # DESCRIPCIÓN (también va dentro de categoría)
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto").strip()

    # --------------------------------------------------------
    # CATEGORÍA FINAL PARA GUARDAR EN caja_movimientos
    # --------------------------------------------------------
    categoria = f"{descripcion} — Responsable: {responsable}" if responsable else descripcion

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto_raw = st.number_input(
        "Monto del gasto ($)",
        min_value=0.01,
        step=0.25,
        format="%.2f"
    )
    monto = Decimal(str(monto_raw))

    # --------------------------------------------------------
    # SALDO REAL (CAJA GENERAL)
    # --------------------------------------------------------
    saldo_antes = obtener_saldo_actual()
    st.info(f"📌 Saldo disponible: **${saldo_antes:,.2f}**")

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------
    if monto > saldo_antes:
        st.error(f"❌ No puedes gastar más del saldo disponible (${saldo_antes:,.2f}).")
        return

    # --------------------------------------------------------
    # REUNIÓN (solo para reporte)
    # --------------------------------------------------------
    id_reunion = obtener_o_crear_reunion(fecha)

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        try:
            # Registrar movimiento (tu función solo acepta estos 4)
            registrar_movimiento(
                id_caja=id_reunion,
                tipo="Egreso",
                categoria=categoria,
                monto=monto
            )

            # Nuevo saldo
            saldo_despues = obtener_saldo_actual()

            # PDF
            pdf_path = generar_pdf_gasto(
                fecha,
                categoria,
                float(monto),
                float(saldo_antes),
                float(saldo_despues)
            )

            st.success("✅ Gasto registrado correctamente.")

            st.download_button(
                "📄 Descargar comprobante PDF",
                data=open(pdf_path, "rb").read(),
                file_name=pdf_path,
                mime="application/pdf"
            )

        except Exception as e:
            st.error("❌ Error al registrar el gasto.")
            st.write(str(e))

    cursor.close()
    con.close()
