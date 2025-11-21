import streamlit as st
from datetime import date, datetime
from modulos.conexion import obtener_conexion

# Caja por reunión
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


def gastos_grupo():

    st.header("🧾 Registro de otros gastos del grupo")

    # ---------------------------------------------
    # FECHA DEL GASTO
    # ---------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del gasto", date.today())
    fecha_gasto = fecha_raw.strftime("%Y-%m-%d")

    # ---------------------------------------------
    # DATOS DEL GASTO
    # ---------------------------------------------
    concepto = st.text_input("📝 Concepto del gasto (ej. 'Refrigerio', 'Materiales')")
    responsable = st.text_input("👤 Responsable del gasto (opcional)")
    monto = st.number_input("💵 Monto del gasto ($)", min_value=0.25, step=0.25)

    if st.button("➖ Registrar gasto"):

        if concepto.strip() == "":
            st.warning("⚠ Debe escribir un concepto del gasto.")
            return

        try:
            # -------------------------------------------------
            # 1️⃣ Obtener o crear reunión/caja del día
            # -------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_gasto)

            # Obtener saldo anterior
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute("""
                SELECT saldo_final 
                FROM caja_reunion 
                WHERE id_caja = %s
            """, (id_caja,))
            row = cursor.fetchone()
            saldo_anterior = row[0] if row else 0

            # -------------------------------------------------
            # 2️⃣ Registrar el movimiento (EGRESO)
            # -------------------------------------------------
            descripcion = f"Gasto del grupo – {concepto}"
            if responsable.strip() != "":
                descripcion += f" (Responsable: {responsable})"

            registrar_movimiento(
                id_caja,
                "Egreso",
                descripcion,
                monto
            )

            # Obtener nuevo saldo
            cursor.execute("""
                SELECT saldo_final
                FROM caja_reunion
                WHERE id_caja = %s
            """, (id_caja,))
            saldo_nuevo = cursor.fetchone()[0]

            con.close()

            # -------------------------------------------------
            # 3️⃣ Generar PDF
            # -------------------------------------------------
            nombre_pdf = f"gasto_{id_caja}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            tabla = [
                ["Detalle", "Valor"],
                ["Fecha del gasto", fecha_gasto],
                ["Concepto", concepto],
                ["Responsable", responsable if responsable else "N/A"],
                ["Monto del gasto", f"${monto:.2f}"],
                ["Saldo anterior", f"${saldo_anterior:.2f}"],
                ["Saldo después del gasto", f"${saldo_nuevo:.2f}"],
                ["ID de caja del día", str(id_caja)],
                ["Hora de registro", datetime.now().strftime("%H:%M:%S")],
            ]

            doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
            tabla_pdf = Table(tabla)
            tabla_pdf.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.darkgray),
                ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID", (0,0), (-1,-1), 1, colors.black),
            ]))

            doc.build([tabla_pdf])

            st.success("✔ Gasto registrado, descontado de caja y PDF generado.")

            # -------------------------------------------------
            # 4️⃣ Botón de descarga del PDF
            # -------------------------------------------------
            with open(nombre_pdf, "rb") as f:
                st.download_button(
                    "📥 Descargar comprobante en PDF",
                    f,
                    file_name=nombre_pdf,
                    mime="application/pdf"
                )

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar gasto: {e}")
