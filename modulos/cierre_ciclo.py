import streamlit as st
import pandas as pd
from datetime import date
import base64
import io

from modulos.conexion import obtener_conexion


# ==========================================================
# 1. OBTENER CICLO ACTIVO
# ==========================================================
def obtener_ciclo_activo():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM ciclo_resumen
        WHERE fecha_cierre IS NULL
        ORDER BY id_ciclo_resumen DESC
        LIMIT 1
    """)

    ciclo = cur.fetchone()
    con.close()
    return ciclo


# ==========================================================
# 2. PRESTAMOS PENDIENTES
# ==========================================================
def prestamos_pendientes():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT Id_Préstamo, `Saldo pendiente`, Id_Socia
        FROM Prestamo
        WHERE `Saldo pendiente` > 0
    """)

    data = cur.fetchall()
    con.close()
    return data


# ==========================================================
# 3. SALDO INICIAL
# ==========================================================
def obtener_saldo_inicial(fecha_inicio):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_inicial
        FROM caja_reunion
        WHERE fecha >= %s
        ORDER BY fecha ASC
        LIMIT 1
    """, (fecha_inicio,))

    row = cur.fetchone()
    con.close()
    return row[0] if row else 0


# ==========================================================
# 4. SALDO FINAL
# ==========================================================
def obtener_saldo_final(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha_inicio, fecha_fin))

    row = cur.fetchone()
    con.close()
    return row[0] if row else 0


# ==========================================================
# 5. TOTAL INGRESOS / EGRESOS
# ==========================================================
def obtener_totales(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(ingresos),0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    ingresos = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(egresos),0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    egresos = cur.fetchone()[0]

    con.close()
    return ingresos, egresos


# ==========================================================
# 6. DETALLE DIARIO (AUDITORÍA)
# ==========================================================
def obtener_detalle_diario(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT fecha, ingresos, egresos, saldo_inicial, saldo_final
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha ASC
    """, (fecha_inicio, fecha_fin))

    data = cur.fetchall()
    con.close()
    return data


# ==========================================================
# 7. APORTES DE AHORRO POR SOCIA
# ==========================================================
def obtener_ahorros_por_socia(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT S.Id_Socia, S.Nombre,
               COALESCE(SUM(A.`Monto del aporte`),0) AS ahorro
        FROM Socia S
        LEFT JOIN Ahorro A ON A.Id_Socia = S.Id_Socia
            AND A.`Fecha del aporte` BETWEEN %s AND %s
        GROUP BY S.Id_Socia, S.Nombre
        ORDER BY S.Id_Socia
    """, (fecha_inicio, fecha_fin))

    data = cur.fetchall()
    con.close()
    return data


# ==========================================================
# 8. INTERESES + MULTAS = UTILIDAD
# ==========================================================
def calcular_utilidad(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(Interes_total),0)
        FROM Prestamo
        WHERE `Fecha del préstamo` BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    intereses = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(Monto),0)
        FROM Multa
        WHERE Fecha_aplicacion BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    multas = cur.fetchone()[0]

    con.close()
    return intereses + multas, intereses, multas


# ==========================================================
# 9. DISTRIBUCIÓN PROPORCIONAL (NEGATIVOS CORREGIDOS)
# ==========================================================
def generar_tabla_distribucion(socias, utilidad_total):
    total_ahorros = sum(s["ahorro"] for s in socias)

    tabla = []

    for s in socias:
        ahorro = s["ahorro"]

        # -------------------------------------
        # CORRECCIÓN: AHORRO NEGATIVO → CERO
        # -------------------------------------
        if ahorro < 0:
            porcentaje = 0
            porcion = 0
            monto_final = 0
            ahorro_visible = 0
        else:
            porcentaje = (ahorro / total_ahorros) if total_ahorros > 0 else 0
            porcion = round(porcentaje * utilidad_total, 2)
            monto_final = round(ahorro + porcion, 2)
            ahorro_visible = ahorro

        tabla.append({
            "id": s["Id_Socia"],
            "nombre": s["Nombre"],
            "ahorro": ahorro_visible,
            "porcentaje": round(porcentaje * 100, 2),
            "porcion": porcion,
            "monto_final": monto_final
        })

    return tabla



# ==========================================================
# 10. ACTA EN HTML
# ==========================================================
def generar_html_acta(inicio, fin, saldo_i, saldo_f, ingresos, egresos,
                      utilidad, intereses, multas, tabla):

    total_ahorros = sum(f["ahorro"] for f in tabla)

    html = f"""
    <h2>ACTA DE CIERRE DEL CICLO — SOLIDARIDAD CVX</h2>
    <hr>

    <h3>1. Datos Generales</h3>
    <p><b>Inicio:</b> {inicio}</p>
    <p><b>Cierre:</b> {fin}</p>
    <p><b>Saldo inicial:</b> ${saldo_i:,.2f}</p>
    <p><b>Saldo final:</b> ${saldo_f:,.2f}</p>
    <p><b>Ingresos totales:</b> ${ingresos:,.2f}</p>
    <p><b>Egresos totales:</b> ${egresos:,.2f}</p>
    <p><b>Ahorro total del grupo:</b> ${total_ahorros:,.2f}</p>

    <h3>2. Utilidades</h3>
    <p><b>Intereses:</b> ${intereses:,.2f}</p>
    <p><b>Multas:</b> ${multas:,.2f}</p>
    <p><b>Utilidad total:</b> ${utilidad:,.2f}</p>

    <h3>3. Distribución proporcional</h3>

    <table border=1 cellpadding=5 cellspacing=0>
        <tr>
            <th>ID</th><th>Nombre</th><th>Ahorro</th>
            <th>%</th><th>Porción</th><th>Monto final</th>
        </tr>
    """

    for f in tabla:
        html += f"""
        <tr>
            <td>{f["id"]}</td>
            <td>{f["nombre"]}</td>
            <td>${f["ahorro"]:,.2f}</td>
            <td>{f["porcentaje"]}%</td>
            <td>${f["porcion"]:,.2f}</td>
            <td>${f["monto_final"]:,.2f}</td>
        </tr>
        """

    html += "</table>"
    return html



# ==========================================================
# 11. GENERAR PDF
# ==========================================================
def generar_pdf(html):
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    story = [Paragraph(html, styles["Normal"])]
    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf



# ==========================================================
# 12. INTERFAZ PRINCIPAL — CIERRE DE CICLO
# ==========================================================
def cierre_ciclo():

    st.title("🔒 Cierre de Ciclo — Solidaridad CVX")

    ciclo = obtener_ciclo_activo()
    if ciclo is None:
        st.warning("No existe un ciclo activo.")
        return

    fecha_inicio = ciclo["fecha_inicio"]
    fecha_cierre = date.today().strftime("%Y-%m-%d")

    pendientes = prestamos_pendientes()
    modo_prueba = st.toggle("🧪 Modo prueba (ignorar préstamos pendientes)")

    if pendientes and not modo_prueba:
        st.error("❌ No puedes cerrar el ciclo porque hay préstamos pendientes.")
        for p in pendientes:
            st.write(f"- Préstamo #{p['Id_Préstamo']} — Pendiente: ${p['Saldo pendiente']}")
        return

    if pendientes and modo_prueba:
        st.warning("⚠ MODO PRUEBA ACTIVADO: Los préstamos pendientes serán ignorados.")

    ingresos, egresos = obtener_totales(fecha_inicio, fecha_cierre)
    saldo_inicial = obtener_saldo_inicial(fecha_inicio)
    saldo_final = obtener_saldo_final(fecha_inicio, fecha_cierre)

    utilidad_total, intereses, multas = calcular_utilidad(fecha_inicio, fecha_cierre)
    detalle_diario = obtener_detalle_diario(fecha_inicio, fecha_cierre)
    socias = obtener_ahorros_por_socia(fecha_inicio, fecha_cierre)

    tabla_dist = generar_tabla_distribucion(socias, utilidad_total)

    # ======================================================
    # TABS
    # ======================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📘 Resumen", "📋 Auditoría", "📅 Detalle Diario", "📊 Gráfica", "📄 Acta"]
    )

    # TAB 1 — RESUMEN
    with tab1:
        st.subheader("📘 Resumen del ciclo")
        st.write(f"**Fecha inicio:** {fecha_inicio}")
        st.write(f"**Fecha cierre:** {fecha_cierre}")
        st.write(f"**Saldo inicial:** ${saldo_inicial:,.2f}")
        st.write(f"**Saldo final:** ${saldo_final:,.2f}")
        st.write(f"**Ingresos:** ${ingresos:,.2f}")
        st.write(f"**Egresos:** ${egresos:,.2f}")
        st.write(f"**Intereses:** ${intereses:,.2f}")
        st.write(f"**Multas:** ${multas:,.2f}")
        st.write(f"**Utilidad total:** ${utilidad_total:,.2f}")

    # TAB 2 — AUDITORÍA
    with tab2:
        st.subheader("📋 Auditoría de ingresos y egresos por día")
        if detalle_diario:
            st.dataframe(pd.DataFrame(detalle_diario), use_container_width=True)
        else:
            st.info("No hay movimientos en este ciclo.")

    # TAB 3 — DETALLE DIARIO
    with tab3:
        st.subheader("📅 Detalle diario de caja")
        if detalle_diario:
            df = pd.DataFrame(detalle_diario)
            df["fecha"] = df["fecha"].astype(str)
            st.table(df)
        else:
            st.info("Sin movimientos para mostrar.")

    # TAB 4 — GRÁFICA
    with tab4:
        st.subheader("📊 Gráfica del ciclo")
        if detalle_diario:
            df = pd.DataFrame(detalle_diario)
            df["fecha"] = df["fecha"].astype(str)
            st.line_chart(df[["fecha", "saldo_final"]], x="fecha", y="saldo_final")
        else:
            st.info("No hay datos para graficar.")

    # TAB 5 — ACTA
    with tab5:
        st.subheader("📄 Acta del ciclo")
        html = generar_html_acta(
            fecha_inicio, fecha_cierre,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            utilidad_total, intereses, multas,
            tabla_dist
        )

        if st.button("📘 Ver Acta en pantalla"):
            st.markdown(html, unsafe_allow_html=True)

        if st.button("⬇️ Descargar Acta en PDF"):
            pdf = generar_pdf(html)
            b64 = base64.b64encode(pdf).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{b64}" download="Acta_Cierre_CVX.pdf">📥 Descargar PDF</a>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # BOTÓN FINAL — CERRAR CICLO
    if st.button("🔐 Cerrar ciclo ahora (definitivo)"):

        con = obtener_conexion()
        cur = con.cursor()

        cur.execute("""
            UPDATE ciclo_resumen
            SET fecha_cierre=%s,
                saldo_inicial=%s,
                saldo_final=%s,
                total_ingresos=%s,
                total_egresos=%s,
                total_utilidad=%s,
                estado='Cerrado'
            WHERE id_ciclo_resumen=%s
        """, (
            fecha_cierre,
            saldo_inicial,
            saldo_final,
            ingresos,
            egresos,
            utilidad_total,
            ciclo["id_ciclo_resumen"]
        ))

        con.commit()
        con.close()

        st.success("✅ Ciclo cerrado correctamente.")
        st.balloons()
        st.rerun()
