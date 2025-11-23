import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, obtener_saldo_actual
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA COMPLETO + CIERRE DE DÍA + GRÁFICAS PDF
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ LEER REGLAS DEL CICLO
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ Debes registrar las reglas internas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    if not ciclo_inicio:
        st.error("⚠ Falta la fecha de inicio del ciclo.")
        return

    # crear reunión si no existe hoy
    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ============================================================
    # 2️⃣ LISTA DE FECHAS
    # ============================================================
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cur.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas.")
        return

    fechas = [f["fecha"] for f in fechas_raw]
    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 3️⃣ LEER RESUMEN DEL DÍA
    # ============================================================
    cur.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
    reunion = cur.fetchone()

    if not reunion:
        st.warning("⚠ No hay datos para esta fecha.")
        return

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

    st.metric("💰 Saldo Final del Día", f"${saldo_final:.2f}")

    st.markdown("---")

    # ============================================================
    # 4️⃣ MOVIMIENTOS DEL DÍA
    # ============================================================
    st.subheader("📋 Movimientos del día")

    cur.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (id_caja,))

    movimientos = cur.fetchall()

    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        st.dataframe(df_mov, hide_index=True, use_container_width=True)
    else:
        st.info("No hay movimientos registrados para este día.")

    st.markdown("---")

    # ============================================================
    # 5️⃣ CIERRE DEL DÍA
    # ============================================================
    st.subheader("🧾 Cierre del día")

    if dia_cerrado:
        st.success("🔒 Este día ya está CERRADO.")
    else:
        st.warning("⚠ Este día NO está cerrado.")

        if st.button("✅ Cerrar este día definitivamente"):

            saldo_real = float(obtener_saldo_actual())
            saldo_calc = saldo_inicial + ingresos - egresos

            if abs(saldo_calc - saldo_real) > 0.01:
                st.error(
                    f"❌ No se puede cerrar el día.\n\n"
                    f"Saldo calculado: ${saldo_calc:.2f}\n"
                    f"Saldo real: ${saldo_real:.2f}\n"
                    f"Los valores no coinciden."
                )
                return

            cur.execute("""
                UPDATE caja_reunion
                SET dia_cerrado = 1, saldo_final = %s
                WHERE id_caja = %s
            """, (saldo_real, id_caja))

            con.commit()
            st.success("🔒 Día cerrado correctamente.")
            st.experimental_rerun()

    st.markdown("---")

    # ============================================================
    # 6️⃣ GRÁFICAS POR FECHA (3 GRÁFICAS SEPARADAS)
    # ============================================================
    st.subheader("📈 Gráficas del día")

    graf_df = pd.DataFrame({
        "Tipo": ["Ingresos", "Egresos", "Balance"],
        "Monto": [ingresos, egresos, ingresos - egresos]
    })

    # ---- gráfica ingresos ----
    st.write("📥 **Ingresos del día**")
    st.bar_chart(pd.DataFrame({"Ingresos": [ingresos]}))

    # ---- gráfica egresos ----
    st.write("📤 **Egresos del día**")
    st.bar_chart(pd.DataFrame({"Egresos": [egresos]}))

    # ---- gráfica balance ----
    st.write("💼 **Balance del día**")
    st.bar_chart(pd.DataFrame({"Balance": [ingresos - egresos]}))

    st.markdown("---")

    # ============================================================
    # 7️⃣ PDF DE LAS 3 GRÁFICAS + RESUMEN DEL DÍA
    # ============================================================
    st.subheader("📄 Descargar PDF del día")

    if st.button("📥 Descargar PDF del reporte del día"):

        nombre_pdf = f"reporte_dia_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        tabla_resumen = [
            ["Campo", "Valor"],
            ["Saldo Inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Balance", f"${(ingresos - egresos):.2f}"],
            ["Saldo Final", f"${saldo_final:.2f}"],
            ["Día Cerrado", "Sí" if dia_cerrado else "No"]
        ]

        t1 = Table(tabla_resumen)
        t1.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(t1)

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
