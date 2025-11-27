import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
import os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import asegurar_reunion, obtener_saldo_actual


# ============================================================
# 🔍 OBTENER MOVIMIENTOS DEL DÍA
# ============================================================
def obtener_movimientos_dia(id_caja):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja=%s
        ORDER BY id_mov ASC
    """, (id_caja,))

    return cur.fetchall()


# ============================================================
# 📦 REPORTE DE CAJA PRINCIPAL
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # 📅 Fechas disponibles
    # ============================================================
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha ASC")
    fechas = [str(f["fecha"]) for f in cur.fetchall()]

    if not fechas:
        st.warning("⚠ No existen reuniones registradas.")
        return

    fecha_sel = st.selectbox("Seleccione fecha del reporte:", fechas, index=len(fechas) - 1)

    # Asegurar que la reunión del día esté corregida
    id_caja = asegurar_reunion(fecha_sel)

    # ============================================================
    # 📘 Resumen del día
    # ============================================================
    cur.execute("""
        SELECT saldo_inicial, ingresos, egresos, saldo_final, dia_cerrado
        FROM caja_reunion
        WHERE id_caja=%s
    """, (id_caja,))
    reunion = cur.fetchone()

    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])
    dia_cerrado = reunion["dia_cerrado"]

    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:,.2f}")
    col2.metric("Ingresos", f"${ingresos:,.2f}")
    col3.metric("Egresos", f"${egresos:,.2f}")

    st.metric("💰 Saldo Final", f"${saldo_final:,.2f}")

    st.info(f"""
        🔵 Saldo inicial + ingresos – egresos  
        = {saldo_inicial:.2f} + {ingresos:.2f} – {egresos:.2f}  
        = **${saldo_final:.2f}**
    """)

    st.markdown("---")

    # ============================================================
    # 📄 Movimientos del día
    # ============================================================
    st.subheader("📄 Movimientos registrados")

    movimientos = obtener_movimientos_dia(id_caja)

    if movimientos:
        df = pd.DataFrame(movimientos)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No existen movimientos en esta fecha.")

    st.markdown("---")

    # ============================================================
    # 🔒 Cierre del día (sin modificar estructura de BD)
    # ============================================================
    st.subheader("🔒 Cierre del día")

    if dia_cerrado == 1:
        st.success("✔ Este día ya se encuentra cerrado.")
    else:
        st.warning("⚠ Este día NO está cerrado aún.")

        if st.button("🔐 Cerrar día definitivamente"):

            saldo_real = obtener_saldo_actual()
            saldo_calc = saldo_inicial + ingresos - egresos

            if abs(saldo_real - saldo_calc) > 0.01:
                st.error(f"""
                ❌ No se puede cerrar.
                Saldo real: ${saldo_real:.2f}  
                Saldo calculado: ${saldo_calc:.2f}
                """)
                return

            cur.execute("""
                UPDATE caja_reunion
                SET dia_cerrado = 1, saldo_final = %s
                WHERE id_caja=%s
            """, (saldo_calc, id_caja))

            con.commit()
            st.success("🎉 Día cerrado correctamente.")
            st.rerun()

    st.markdown("---")

    # ============================================================
    # 📈 GRÁFICAS — Restauradas como antes
    # ============================================================
    st.subheader("📈 Gráficas del día")

    df_mov = pd.DataFrame(movimientos)

    if not df_mov.empty:

        df_mov["monto"] = df_mov["monto"].astype(float)

        # ▬▬▬▬ Gráfica de ingresos ▬▬▬▬
        st.write("### 📈 Ingresos del día")
        df_ing = df_mov[df_mov["tipo"] == "Ingreso"]
        st.line_chart(df_ing["monto"]) if not df_ing.empty else st.info("No hubo ingresos.")

        # ▬▬▬▬ Gráfica de egresos ▬▬▬▬
        st.write("### 📉 Egresos del día")
        df_egr = df_mov[df_mov["tipo"] == "Egreso"]
        st.line_chart(df_egr["monto"]) if not df_egr.empty else st.info("No hubo egresos.")

        # ▬▬▬▬ Comparación del día ▬▬▬▬
        st.write("### 📊 Comparación general")
        df_comp = pd.DataFrame({
            "Ingresos": [ingresos],
            "Egresos": [egresos],
            "Saldo Final": [saldo_final]
        })
        st.bar_chart(df_comp)

    st.markdown("---")

    # ============================================================
    # 📄 EXPORTAR PDF
    # ============================================================
    st.subheader("📥 Exportar reporte en PDF")

    if st.button("⬇️ Descargar PDF"):

        nombre_pdf = f"reporte_caja_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        tabla_data = [
            ["Campo", "Valor"],
            ["Saldo Inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Saldo Final", f"${saldo_final:.2f}"],
            ["Día Cerrado", "Sí" if dia_cerrado else "No"],
        ]

        tabla = Table(tabla_data)
        tabla.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
        ]))

        contenido.append(tabla)
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
