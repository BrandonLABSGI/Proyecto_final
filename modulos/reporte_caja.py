import streamlit as st
import pandas as pd
from datetime import date

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import (
    obtener_o_crear_reunion,
    obtener_saldo_actual,
    actualizar_saldo_inicial_dia_siguiente
)
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA — AHORA CON SALDOS CORRECTOS
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ░░░ 1. Reglas internas
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ Debes registrar las reglas internas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    if not ciclo_inicio:
        st.error("⚠ Falta la fecha de inicio del ciclo en reglas internas.")
        return

    # ░░░ 2. Fechas disponibles
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas = [f["fecha"] for f in cur.fetchall()]

    if not fechas:
        st.warning("⚠ Aún no hay reuniones registradas.")
        return

    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ░░░ 3. Datos del día
    cur.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
    reunion = cur.fetchone()

    id_caja = reunion["id_caja"]
    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])
    dia_cerrado = reunion["dia_cerrado"]

    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    c2.metric("Ingresos", f"${ingresos:.2f}")
    c3.metric("Egresos", f"${egresos:.2f}")
    st.metric("💰 Saldo Final", f"${saldo_final:.2f}")

    st.markdown("---")

    # ░░░ 4. Movimientos del día
    cur.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (id_caja,))
    movimientos = cur.fetchall()

    if movimientos:
        st.dataframe(pd.DataFrame(movimientos), hide_index=True, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en esta reunión.")

    st.markdown("---")

    # ░░░ 5. Cierre del día
    st.subheader("🧾 Cierre del día")

    if dia_cerrado == 1:
        st.success("🔒 Día cerrado.")
    else:
        st.warning("⚠ Este día no está cerrado.")

        if st.button("✅ Cerrar este día definitivamente"):

            saldo_real = float(obtener_saldo_actual())
            saldo_calc = saldo_inicial + ingresos - egresos

            if abs(saldo_real - saldo_calc) > 0.01:
                st.error(
                    f"❌ No se puede cerrar el día.\n"
                    f"Saldo calculado: ${saldo_calc:.2f}\n"
                    f"Saldo real: ${saldo_real:.2f}"
                )
                return

            # Cerrar el día
            cur.execute("""
                UPDATE caja_reunion
                SET dia_cerrado = 1, saldo_final = %s
                WHERE id_caja = %s
            """, (saldo_real, id_caja))
            con.commit()

            # 🔥 Actualizar día siguiente
            actualizar_saldo_inicial_dia_siguiente(fecha_sel, saldo_real)

            st.success("🔒 Día cerrado correctamente.")
            st.rerun()

    st.markdown("---")

    # ░░░ 6. Resumen del ciclo
    st.subheader("📊 Resumen del ciclo")

    cur.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto END),0) AS total_ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto END),0) AS total_egresos
        FROM caja_movimientos cm
        JOIN caja_reunion cr ON cr.id_caja = cm.id_caja
        WHERE cr.fecha >= %s
    """, (ciclo_inicio,))
    tot = cur.fetchone()

    st.write(f"📥 Ingresos: **${tot['total_ingresos']:.2f}**")
    st.write(f"📤 Egresos: **${tot['total_egresos']:.2f}**")
    st.success(f"💼 Balance: **${(tot['total_ingresos']-tot['total_egresos']):.2f}**")

    st.markdown("---")

    # ░░░ 7. Exportación PDF
    st.subheader("📄 Exportar PDF del día")

    if st.button("📥 Descargar PDF"):

        nombre_pdf = f"reporte_caja_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        tabla = [
            ["Campo", "Valor"],
            ["Saldo inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Saldo final", f"${saldo_final:.2f}"],
            ["Día cerrado", "Sí" if dia_cerrado else "No"],
        ]

        t = Table(tabla)
        t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))
        contenido.append(t)

        doc.build(contenido)

        with open(nombre_pdf, "rb") as f:
            st.download_button(
                label="📄 Descargar PDF",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf"
            )

    cur.close()
    con.close()
