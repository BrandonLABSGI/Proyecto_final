import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_saldo_por_fecha, obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# MÓDULO DE GASTOS DEL GRUPO
# ============================================================
def gastos_grupo():

    st.title("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    # Fecha
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Nombre responsable
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # DUI (9 dígitos)
    dui_input = st.text_input(
        "DUI (9 dígitos)",
        max_chars=9,
        placeholder="000000000"
    )

    # Validar DUI — solo números
    if dui_input and not dui_input.isdigit():
        st.warning("⚠ El DUI debe contener solo números.")
        return

    # Formatear DUI para guardarlo (00000000-0)
    dui_formateado = ""
    if len(dui_input) == 9:
        dui_formateado = f"{dui_input[:8]}-{dui_input[8]}"

    # Descripción
    descripcion = st.text_input("Descripción del gasto")

    # Monto
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # Obtener saldo actual
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # Botón registrar gasto
    if st.button("💾 Registrar gasto"):

        # Validar campos
        if responsable.strip() == "" or descripcion.strip() == "" or len(dui_input) != 9:
            st.error("⚠ Debe completar todos los campos y el DUI debe tener 9 dígitos.")
            return

        # Validar saldo suficiente
        if monto > saldo:
            st.error("❌ El monto del gasto NO puede ser mayor al saldo disponible.")
            return

        # Registrar gasto
        id_caja = obtener_o_crear_reunion(fecha)

        cursor.execute("""
            INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
            VALUES(%s, %s, %s, %s, %s, %s)
        """, (fecha, descripcion, monto, responsable, dui_formateado, id_caja))

        con.commit()

        # Registrar movimiento en caja (egreso)
        registrar_movimiento(id_caja, "Egreso", f"Gasto del grupo – {descripcion}", monto)

        st.success("✔ Gasto registrado correctamente.")

        # Recuperar ID del gasto
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_gasto = cursor.fetchone()[0]

        # Mostrar botón para descargar comprobante PDF
        generar_pdf_comprobante(id_gasto, fecha, responsable, dui_formateado, descripcion, monto, saldo - monto)

        st.stop()


# ============================================================
# FUNCIÓN PARA GENERAR COMPROBANTE PDF
# ============================================================
def generar_pdf_comprobante(id_gasto, fecha, responsable, dui, descripcion, monto, saldo_final):

    st.subheader("📄 Descargar comprobante del gasto")

    archivo_pdf = f"comprobante_gasto_{id_gasto}.pdf"

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    titulo = styles["Title"]

    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    contenido = []

    contenido.append(Paragraph("COMPROBANTE DE GASTO DEL GRUPO", titulo))
    contenido.append(Paragraph("<br/>", normal))

    contenido.append(Paragraph(f"<b>ID del Gasto:</b> {id_gasto}", normal))
    contenido.append(Paragraph(f"<b>Fecha:</b> {fecha}", normal))
    contenido.append(Paragraph(f"<b>Responsable:</b> {responsable}", normal))
    contenido.append(Paragraph(f"<b>DUI:</b> {dui}", normal))
    contenido.append(Paragraph(f"<b>Descripción:</b> {descripcion}", normal))
    contenido.append(Paragraph(f"<b>Monto gastado:</b> ${monto:.2f}", normal))
    contenido.append(Paragraph(f"<b>Saldo restante en caja:</b> ${saldo_final:.2f}", normal))
    contenido.append(Paragraph("<br/><br/>__________________________", normal))
    contenido.append(Paragraph("Firma del responsable", normal))

    doc.build(contenido)

    # Descargar PDF
    with open(archivo_pdf, "rb") as f:
        st.download_button(
            "📥 Descargar comprobante PDF",
            data=f,
            file_name=archivo_pdf,
            mime="application/pdf"
        )
