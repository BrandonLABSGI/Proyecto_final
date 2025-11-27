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
# 6. DETALLE DIARIO
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
        SELECT 
            S.Id_Socia, 
            S.Nombre,
            COALESCE(SUM(A.Monto_del_aporte), 0) AS ahorro
        FROM Socia S
        LEFT JOIN Ahorro A 
            ON A.Id_Socia = S.Id_Socia
            AND A.Fecha_del_aporte BETWEEN %s AND %s
        GROUP BY S.Id_Socia, S.Nombre
        ORDER BY S.Id_Socia
    """, (fecha_inicio, fecha_fin))

    data = cur.fetchall()
    con.close()
    return data


# ==========================================================
# 8. UTILIDAD (INTERESES + MULTAS)
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
# 9. DISTRIBUCIÓN PROPORCIONAL — ***CORREGIDA***
# ==========================================================
def generar_tabla_distribucion(socias, fondo_total):
    # SOLO socias con ahorro > 0
    socias_con_ahorro = [s for s in socias if s["ahorro"] > 0]

    total_ahorros = sum(s["ahorro"] for s in socias_con_ahorro)

    tabla = []

    for s in socias_con_ahorro:
        ahorro = s["ahorro"]

        porcentaje = (ahorro / total_ahorros) if total_ahorros > 0 else 0
        porcion = round(porcentaje * fondo_total, 2)
        monto_final = round(ahorro + porcion, 2)

        tabla.append({
            "id": s["Id_Socia"],
            "nombre": s["Nombre"],
            "ahorro": ahorro,
            "porcentaje": round(porcentaje * 100, 2),
            "porcion": porcion,
            "monto_final": monto_final
        })

    return tabla


# ==========================================================
# 10. ACTA HTML
# ==========================================================
def generar_html_acta(inicio, fin, saldo_i, saldo_f, ingresos, egresos,
                      fondo_total, intereses, multas, tabla):
    total_ahorros = sum(f["ahorro"] for f in tabla)

    html = f"""
    <h2>ACTA DE CIERRE DEL CICLO — SOLIDARIDAD CVX</h2>
    <hr>

    <h3>1. Datos Generales</h3>
    <p><b>Inicio:</b> {inicio}</p>
    <p><b>Cierre:</b> {fin}</p>
    <p><b>Saldo inicial:</b> ${saldo_i:,.2f}</p>
    <p><b>Saldo final (antes de distribuir):</b> ${saldo_f:,.2f}</p>
    <p><b>Fondo total a repartir:</b> ${fondo_total:,.2f}</p>
    <p><b>Ingresos totales:</b> ${ingresos:,.2f}</p>
    <p><b>Egresos totales:</b> ${egresos:,.2f}</p>
    <p><b>Ahorro total del grupo:</b> ${total_ahorros:,.2f}</p>

    <h3>2. Utilidades</h3>
    <p><b>Intereses:</b> ${intereses:,.2f}</p>
    <p><b>Multas:</b> ${multas:,.2f}</p>
    <p><b>Nota:</b> Las utilidades están incluidas dentro del fondo total a repartir.</p>

    <h3>3. Distribución proporcional</h3>
    """
    return html


# ==========================================================
# 11. GENERAR PDF
# ==========================================================
def generar_pdf_acta(inicio, fin, saldo_i, saldo_f, ingresos, egresos,
                     fondo_total, intereses, multas, tabla_dist):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    story.append(Paragraph("<b>ACTA DE CIERRE DEL CICLO — SOLIDARIDAD CVX</b>", styles["Title"]))
    story.append(Spacer(1, 16))

    # Datos Generales
    story.append(Paragraph("<b>1. Datos Generales</b>", styles["Heading2"]))
    texto = f"""
    <b>Inicio:</b> {inicio}<br/>
    <b>Cierre:</b> {fin}<br/>
    <b>Saldo inicial:</b> ${saldo_i:,.2f}<br/>
    <b>Saldo final (antes de distribuir):</b> ${saldo_f:,.2f}<br/>
    <b>Fondo total a repartir:</b> ${fondo_total:,.2f}<br/>
    <b>Ingresos totales:</b> ${ingresos:,.2f}<br/>
    <b>Egresos totales:</b> ${egresos:,.2f}<br/>
    """
    story.append(Paragraph(texto, styles["Normal"]))
    story.append(Spacer(1, 16))

    # Utilidades
    story.append(Paragraph("<b>2. Utilidades</b>", styles["Heading2"]))
    texto2 = f"""
    <b>Intereses generados:</b> ${intereses:,.2f}<br/>
    <b>Multas generadas:</b> ${multas:,.2f}<br/>
    <b>Nota:</b> Las utilidades están ya incorporadas en el fondo total.<br/>
    """
    story.append(Paragraph(texto2, styles["Normal"]))
    story.append(Spacer(1, 16))

    # Distribución proporcional
    story.append(Paragraph("<b>3. Fórmula utilizada</b>", styles["Heading2"]))
    formula = """
    (Ahorro individual ÷ Ahorro total del grupo) × Fondo total del ciclo<br/><br/>
    Monto final = Ahorro individual + Porción proporcional
    """
    story.append(Paragraph(formula, styles["Normal"]))
    story.append(Spacer(1, 16))

    # Tabla de Ahorro individual
    story.append(Paragraph("<b>4. Ahorro individual por socia</b>", styles["Heading2"]))
    ahorro_data = [["ID", "Nombre", "Ahorro ($)"]]

    for f in tabla_dist:
        ahorro_data.append([f["id"], f["nombre"], f"${f['ahorro']:,.2f}"])

    tabla_ahorro = Table(ahorro_data, colWidths=[40, 200, 100])
    tabla_ahorro.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
    ]))

    story.append(tabla_ahorro)
    story.append(Spacer(1, 16))

    # Distribución final
    story.append(Paragraph("<b>5. Distribución proporcional</b>", styles["Heading2"]))

    encabezado = ["ID", "Nombre", "Ahorro", "% Porción", "Monto final"]
    data = [encabezado]

    for f in tabla_dist:
        data.append([
            f["id"],
            f["nombre"],
            f"${f['ahorro']:,.2f}",
            f"{f['porcentaje']:.2f}%",
            f"${f['monto_final']:,.2f}"
        ])

    tabla = Table(data, colWidths=[40, 180, 70, 70, 80])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))

    story.append(tabla)
    story.append(Spacer(1, 30))

    # Firmas
    story.append(Paragraph("<b>Firmas</b>", styles["Heading2"]))
    story.append(Spacer(1, 20))

    firmas_data = [
        ["_______________________", "_______________________", "_______________________"],
        ["Presidenta", "Tesorera", "Secretaria"]
    ]

    tabla_firmas = Table(firmas_data, colWidths=[170, 170, 170])
    tabla_firmas.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,1), (-1,1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,1), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),
        ("TOPPADDING", (0,1), (-1,1), 4),
    ]))

    story.append(tabla_firmas)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# ==========================================================
# 12. INTERFAZ PRINCIPAL
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
        st.warning("⚠ Modo prueba activado.")

    ingresos, egresos = obtener_totales(fecha_inicio, fecha_cierre)
    saldo_inicial = obtener_saldo_inicial(fecha_inicio)
    saldo_final = obtener_saldo_final(fecha_inicio, fecha_cierre)

    # 💥 FONDO TOTAL REAL A REPARTIR (saldo_final real de caja)
    fondo_total = saldo_final

    _, intereses, multas = calcular_utilidad(fecha_inicio, fecha_cierre)
    detalle_diario = obtener_detalle_diario(fecha_inicio, fecha_cierre)
    socias = obtener_ahorros_por_socia(fecha_inicio, fecha_cierre)

    tabla_dist = generar_tabla_distribucion(socias, fondo_total)

    # ================================
    # TABS
    # ================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📘 Resumen", "📋 Auditoría", "📅 Detalle Diario", "📊 Gráfica", "📄 Acta"]
    )

    with tab1:
        st.subheader("📘 Resumen del ciclo")
        st.write(f"**Fecha inicio:** {fecha_inicio}")
        st.write(f"**Fecha cierre:** {fecha_cierre}")
        st.write(f"**Saldo inicial:** ${saldo_inicial:,.2f}")
        st.write(f"**Saldo FINAL real (a repartir):** ${fondo_total:,.2f}")
        st.write(f"**Ingresos:** ${ingresos:,.2f}")
        st.write(f"**Egresos:** ${egresos:,.2f}")
        st.write(f"**Intereses:** ${intereses:,.2f}")
        st.write(f"**Multas:** ${multas:,.2f}")
        st.write(f"**Caja final después de repartir:** $0.00")

    with tab2:
        st.subheader("📋 Auditoría")
        if detalle_diario:
            st.dataframe(pd.DataFrame(detalle_diario))
        else:
            st.info("No hay movimientos.")

    with tab3:
        st.subheader("📅 Detalle diario")
        if detalle_diario:
            df = pd.DataFrame(detalle_diario)
            df["fecha"] = df["fecha"].astype(str)
            st.table(df)
        else:
            st.info("Sin movimientos.")

    with tab4:
        st.subheader("📊 Gráfica")
        if detalle_diario:
            df = pd.DataFrame(detalle_diario)
            df["fecha"] = df["fecha"].astype(str)
            st.line_chart(df[["fecha", "saldo_final"]], x="fecha", y="saldo_final")
        else:
            st.info("Sin datos.")

    with tab5:
        st.subheader("📄 Acta del ciclo")

        html = generar_html_acta(
            fecha_inicio, fecha_cierre,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            fondo_total, intereses, multas,
            tabla_dist
        )

        if st.button("📘 Ver acta"):
            st.markdown(html, unsafe_allow_html=True)

        if st.button("⬇ Descargar PDF"):
            pdf = generar_pdf_acta(
                fecha_inicio, fecha_cierre,
                saldo_inicial, saldo_final,
                ingresos, egresos,
                fondo_total, intereses, multas,
                tabla_dist
            )
            b64 = base64.b64encode(pdf).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{b64}" download="Acta_Cierre_CVX.pdf">📥 Descargar PDF</a>',
                unsafe_allow_html=True
            )

    st.markdown("---")

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
            fondo_total,
            ciclo["id_ciclo_resumen"]
        ))

        con.commit()
        con.close()

        st.success("Ciclo cerrado correctamente.")
        st.balloons()
        st.rerun()
