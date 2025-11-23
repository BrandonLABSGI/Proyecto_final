import streamlit as st
from datetime import date
from decimal import Decimal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ------------------------------------------------------------
# FUNCIÓN PARA GENERAR PDF DEL GASTO
# ------------------------------------------------------------
def generar_pdf_gasto(fecha, responsable, descripcion, monto, saldo_disponible, saldo_final):
    nombre_pdf = f"gasto_{fecha}.pdf"

    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)

    styles = getSampleStyleSheet()
    contenido = []

    titulo = Paragraph("<b>Comprobante de Gasto</b>", styles["Title"])
    contenido.append(titulo)

    tabla_datos = [
        ["Campo", "Detalle"],
        ["Fecha del gasto", fecha],
        ["Responsable", responsable],
        ["Descripción del gasto", descripcion],
        ["Monto del gasto", f"${monto:.2f}"],
        ["Saldo antes del gasto", f"${saldo_disponible:.2f}"],
        ["Saldo después del gasto", f"${saldo_final:.2f}"],
    ]

    tabla = Table(tabla_datos, colWidths=[180, 300])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    contenido.append(tabla)

    doc.build(contenido)

    return nombre_pdf


# ------------------------------------------------------------
# PANTALLA PRINCIPAL DE GASTOS
# ------------------------------------------------------------
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable del gasto").strip()

    # --------------------------------------------------------
    # DESCRIPCIÓN
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto").strip()

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto_raw = st.number_input(
        "Monto del gasto ($)",
        min_value=0.01,
        format="%.2f",
        step=0.01
    )
    monto = Decimal(str(monto_raw))

    # --------------------------------------------------------
    # SALDO DISPONIBLE
    # --------------------------------------------------------
    id_reunion = obtener_o_crear_reunion(fecha)

    cursor.execute(
        "SELECT saldo_final FROM caja_reunion WHERE id_caja = %s",
        (id_reunion,)
    )
    fila = cursor.fetchone()
    saldo_disponible = float(fila["saldo_final"]) if fila else 0.0

    st.info(f"📌 Saldo disponible: **${saldo_disponible:,.2f}**")

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------
    if monto > saldo_disponible:
        st.error(f"❌ No puedes registrar un gasto mayor al saldo disponible (${saldo_disponible:,.2f}).")
        return

    # --------------------------------------------------------
    # BOTÓN GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        try:
            registrar_movimiento(
                id_caja=id_reunion,
                tipo="egreso",
                monto=monto,
                descripcion=descripcion,
                responsable=responsable,
                fecha=fecha
            )

            # Obtener nuevo saldo luego del gasto
            cursor.execute(
                "SELECT saldo_final FROM caja_reunion WHERE id_caja = %s",
                (id_reunion,)
            )
            fila2 = cursor.fetchone()
            saldo_final = float(fila2["saldo_final"]) if fila2 else saldo_disponible - float(monto)

            # Generar PDF
            pdf_path = generar_pdf_gasto(
                fecha, responsable, descripcion,
                float(monto), saldo_disponible, saldo_final
            )

            st.success("✅ Gasto registrado correctamente.")
            st.download_button(
                "📄 Descargar comprobante PDF",
                data=open(pdf_path, "rb").read(),
                file_name=pdf_path,
                mime="application/pdf"
            )

        except Exception as e:
            st.error("❌ Ocurrió un error al registrar el gasto.")
            st.write(e)

    cursor.close()
    con.close()
