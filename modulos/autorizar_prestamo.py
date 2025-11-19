import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from modulos.config.conexion import obtener_conexion



# ---------------------------------------------------------
#   FUNCION PARA GENERAR PDF
# ---------------------------------------------------------
def generar_pdf(detalle, calculos):
    file_path = "/tmp/reporte_prestamo.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    contenido = []

    # --- TÍTULO ---
    contenido.append(Paragraph("Resumen del Préstamo Autorizado", styles["Title"]))

    # --- TABLA DETALLE ---
    tabla_detalle = Table(detalle, colWidths=[180, 300])
    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    contenido.append(tabla_detalle)

    contenido.append(Paragraph("<br/><br/>Cálculos del préstamo", styles["Heading2"]))

    # --- TABLA CÁLCULOS ---
    tabla_calculos = Table(calculos, colWidths=[180, 300])
    tabla_calculos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
    ]))
    contenido.append(tabla_calculos)

    doc.build(contenido)
    return file_path



# ---------------------------------------------------------
#   FUNCION PRINCIPAL PARA AUTORIZAR PRESTAMO
# ---------------------------------------------------------
def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    # --- FORMULARIO ---
    id_socia = st.number_input("ID de la socia:", min_value=1, step=1)
    monto = st.number_input("💵 Monto prestado ($):", min_value=1, step=1)
    tasa = st.number_input("📈 Tasa de interés (%)", min_value=1, step=1)
    plazo = st.number_input("🗓 Plazo (meses)", min_value=1, step=1)
    cuotas = st.number_input("📑 Número de cuotas", min_value=1, step=1)
    firma = st.text_input("✍️ Firma del directivo que autoriza")

    if st.button("✅ Autorizar préstamo"):

        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # ---------------------------------------------------------
            #   VALIDAR EXISTENCIA DE LA SOCIA
            # ---------------------------------------------------------
            cursor.execute("SELECT Nombre FROM Socia WHERE Id_Socia = %s", (id_socia,))
            row = cursor.fetchone()

            if row is None:
                st.error("❌ El ID de la socia no existe.")
                return

            nombre_socia = row[0]

            # ---------------------------------------------------------
            #   CALCULOS DE PRÉSTAMO
            # ---------------------------------------------------------
            interes_total = round(monto * (tasa / 100), 2)
            total_pagar = round(monto + interes_total, 2)
            pago_por_cuota = round(total_pagar / cuotas, 2)

            # ---------------------------------------------------------
            #   INSERTAR PRÉSTAMO EN LA BD
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Prestamo 
                (Fecha, Monto, Tasa, Plazo, Cuotas, Saldo, Estado, Id_Grupo, Id_Socia, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s, 'activo', 1, %s, 1)
            """, (
                date.today(),
                monto,
                tasa,
                plazo,
                cuotas,
                total_pagar,
                id_socia
            ))

            con.commit()

            st.success("✅ Préstamo registrado correctamente.")

            # ---------------------------------------------------------
            #   RESUMEN BONITO EN STREAMLIT
            # ---------------------------------------------------------
            st.subheader("📄 Resumen del préstamo autorizado")

            detalle = [
                ["Campo", "Valor"],
                ["ID Socia", id_socia],
                ["Nombre de la socia", nombre_socia],
                ["Monto prestado", f"${monto:.2f}"],
                ["Tasa de interés", f"{tasa}%"],
                ["Plazo", f"{plazo} meses"],
                ["Número de cuotas", cuotas],
                ["Fecha del préstamo", str(date.today())]
            ]

            calculos = [
                ["Campo", "Valor"],
                ["Interés total", f"${interes_total:.2f}"],
                ["Total a pagar", f"${total_pagar:.2f}"],
                ["Pago por cuota", f"${pago_por_cuota:.2f}"]
            ]

            st.table(detalle)
            st.table(calculos)

            # ---------------------------------------------------------
            #   GENERAR PDF
            # ---------------------------------------------------------
            pdf_path = generar_pdf(detalle, calculos)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar resumen en PDF",
                    data=f,
                    file_name="Resumen_Prestamo.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")
