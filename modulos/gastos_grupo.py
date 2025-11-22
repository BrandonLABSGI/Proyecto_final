import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


def gastos_grupo():

    st.title("🧾 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------------------------------------
    # FECHA DEL GASTO
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI (validación estricta: SOLO si es < 9 dígitos)
    # --------------------------------------------------------
    dui_input = st.text_input("DUI (9 dígitos)")

    if dui_input and (not dui_input.isdigit() or len(dui_input) < 9):
        st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
        return

    # Formatear DUI si está completo
    dui_formateado = dui_input[:8] + "-" + dui_input[8:] if len(dui_input) == 9 else None

    # --------------------------------------------------------
    # DESCRIPCIÓN DEL GASTO (opcional)
    # --------------------------------------------------------
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # --------------------------------------------------------
    # SALDO DISPONIBLE SEGÚN LA FECHA
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN PARA REGISTRAR
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # Validación: DUI requerido
        if not dui_formateado:
            st.error("❌ Debe ingresar un DUI válido de 9 dígitos.")
            return

        # Validación: saldo insuficiente
        if monto > saldo:
            st.error("❌ No se puede procesar el desembolso. El monto excede el saldo disponible.")
            return

        # Obtener o crear reunión del día
        id_caja = obtener_o_crear_reunion(fecha)

        try:
            # --------------------------------------------------------
            # INSERTAR EN TABLA GASTOS_GRUPO
            # --------------------------------------------------------
            cursor.execute("""
                INSERT INTO Gastos_grupo (Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, descripcion, monto, responsable, dui_formateado, id_caja))
            con.commit()

            # --------------------------------------------------------
            # REGISTRAR MOVIMIENTO DE EGRESO EN CAJA
            # --------------------------------------------------------
            registrar_movimiento(
                id_caja,
                "Egreso",
                f"Gasto – {descripcion if descripcion else 'Sin descripción'}",
                monto
            )

            st.success("✔ Gasto registrado exitosamente.")

            # --------------------------------------------------------
            # GENERAR PDF DE RESUMEN
            # --------------------------------------------------------
            if st.button("📄 Descargar resumen del gasto en PDF"):

                styles = getSampleStyleSheet()

                archivo_pdf = "resumen_gasto.pdf"
                doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)

                contenido = f"""
                <b>Resumen del gasto</b><br/><br/>
                <b>Fecha:</b> {fecha}<br/>
                <b>Responsable:</b> {responsable}<br/>
                <b>DUI:</b> {dui_formateado}<br/>
                <b>Concepto:</b> {descripcion if descripcion else "Sin descripción"}<br/>
                <b>Monto:</b> ${monto:.2f}<br/>
                <b>Caja ID:</b> {id_caja}<br/>
                """

                story = [Paragraph(contenido, styles["Normal"])]
                doc.build(story)

                with open(archivo_pdf, "rb") as f:
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=f,
                        file_name=archivo_pdf,
                        mime="application/pdf"
                    )

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error registrando el gasto: {e}")

        finally:
            cursor.close()
            con.close()
