import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import io
import base64


# ---------------------------------------------------------
# OBTENER CICLO ACTIVO
# ---------------------------------------------------------
def obtener_ciclo_activo():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM ciclo_resumen
        WHERE fecha_cierre IS NULL
        ORDER BY id_ciclo_resumen DESC
        LIMIT 1
    """)

    ciclo = cur.fetchone()
    con.close()
    return ciclo


# ---------------------------------------------------------
# PRESTAMOS PENDIENTES
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# SALDO INICIAL
# ---------------------------------------------------------
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

    fila = cur.fetchone()
    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# SALDO FINAL
# ---------------------------------------------------------
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

    fila = cur.fetchone()
    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# TOTALES INGRESOS / EGRESOS
# ---------------------------------------------------------
def obtener_totales(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(ingresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    ingresos = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(egresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    egresos = cur.fetchone()[0]

    con.close()
    return ingresos, egresos


# ---------------------------------------------------------
# AHORROS POR SOCIA
# ---------------------------------------------------------
def obtener_ahorros_por_socia(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT S.Id_Socia, S.Nombre,
               COALESCE(SUM(A.`Monto del aporte`), 0) AS ahorro
        FROM Socia S
        LEFT JOIN Ahorro A ON A.Id_Socia = S.Id_Socia
            AND A.`Fecha del aporte` BETWEEN %s AND %s
        GROUP BY S.Id_Socia, S.Nombre
        ORDER BY S.Id_Socia
    """, (fecha_inicio, fecha_fin))

    data = cur.fetchall()
    con.close()
    return data


# ---------------------------------------------------------
# UTILIDAD (INTERESES + MULTAS)
# ---------------------------------------------------------
def calcular_utilidad(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(Interes_total), 0)
        FROM Prestamo
        WHERE `Fecha del préstamo` BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    intereses = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(Monto), 0)
        FROM Multa
        WHERE Fecha_aplicacion BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    multas = cur.fetchone()[0]

    con.close()
    return intereses + multas, intereses, multas


# ---------------------------------------------------------
# DISTRIBUCIÓN DE UTILIDAD
# ---------------------------------------------------------
def generar_tabla_distribucion(socias, utilidad_total):
    total_ahorros = sum(s["ahorro"] for s in socias)
    tabla = []

    for s in socias:
        porcentaje = (s["ahorro"] / total_ahorros) if total_ahorros > 0 else 0
        porcion = round(porcentaje * utilidad_total, 2)
        monto_final = round(s["ahorro"] + porcion, 2)

        tabla.append({
            "id": s["Id_Socia"],
            "nombre": s["Nombre"],
            "ahorro": s["ahorro"],
            "porcentaje": round(porcentaje * 100, 2),
            "porcion": porcion,
            "monto_final": monto_final
        })

    return tabla


# ---------------------------------------------------------
# ACTA HTML
# ---------------------------------------------------------
def generar_html_acta(inicio, fin, saldo_i, saldo_f, ingresos, egresos,
                      utilidad, intereses, multas, tabla):

    total_ahorros = sum(f["ahorro"] for f in tabla)

    html = f"""
    <h2>ACTA DE CIERRE DEL CICLO — SOLIDARIDAD CVX</h2>
    <hr>

    <h3>1. Información general</h3>
    <p><b>Fecha inicio:</b> {inicio}</p>
    <p><b>Fecha cierre:</b> {fin}</p>
    <p><b>Saldo inicial:</b> ${saldo_i:,.2f}</p>
    <p><b>Saldo final:</b> ${saldo_f:,.2f}</p>
    <p><b>Ingresos:</b> ${ingresos:,.2f}</p>
    <p><b>Egresos:</b> ${egresos:,.2f}</p>
    <p><b>Ahorro total del grupo:</b> ${total_ahorros:,.2f}</p>

    <h3>2. Utilidades del ciclo</h3>
    <p><b>Intereses generados:</b> ${intereses:,.2f}</p>
    <p><b>Multas aplicadas:</b> ${multas:,.2f}</p>
    <p><b>Utilidad total:</b> ${utilidad:,.2f}</p>

    <h3>3. Distribución proporcional</h3>
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>#</th>
            <th>Nombre</th>
            <th>Ahorro</th>
            <th>%</th>
            <th>Porción</th>
            <th>Monto final</th>
        </tr>
    """

    for f in tabla:
        html += f"""
        <tr>
            <td>{f['id']}</td>
            <td>{f['nombre']}</td>
            <td>${f['ahorro']:,.2f}</td>
            <td>{f['porcentaje']}%</td>
            <td>${f['porcion']:,.2f}</td>
            <td>${f['monto_final']:,.2f}</td>
        </tr>
        """

    html += """
    </table>

    <br><h3>4. Firmas</h3>
    Presidenta: ________________________ <br><br>
    Secretaria: ________________________ <br><br>
    Tesorera: _________________________ <br><br>
    """

    return html


# ---------------------------------------------------------
# PDF
# ---------------------------------------------------------
def generar_pdf(html):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = [Paragraph(html, styles["Normal"])]
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# ---------------------------------------------------------
# INTERFAZ COMPLETA — CIERRE DEL CICLO
# ---------------------------------------------------------
def cierre_ciclo():
    st.title("🔒 Cierre de Ciclo — Solidaridad CVX")

    ciclo = obtener_ciclo_activo()
    if ciclo is None:
        st.warning("No existe un ciclo activo.")
        return

    fecha_inicio = ciclo["fecha_inicio"]
    fecha_fin = date.today().strftime("%Y-%m-%d")

    pendientes = prestamos_pendientes()

    # ---------------------------------------------------------
    # MODO PRUEBA (IGNORAR PRÉSTAMOS PENDIENTES)
    # ---------------------------------------------------------
    modo_prueba = st.toggle("🧪 Activar modo prueba (ignora préstamos pendientes)")

    if pendientes and not modo_prueba:
        st.error("❌ NO puedes cerrar: hay préstamos pendientes.")
        for p in pendientes:
            st.write(f"- Préstamo #{p['Id_Préstamo']} — Saldo pendiente: ${p['Saldo pendiente']}")
        return

    if pendientes and modo_prueba:
        st.warning("⚠️ MODO PRUEBA ACTIVADO. Los préstamos pendientes NO serán considerados.")

    ingresos, egresos = obtener_totales(fecha_inicio, fecha_fin)
    saldo_inicial = obtener_saldo_inicial(fecha_inicio)
    saldo_final = obtener_saldo_final(fecha_inicio, fecha_fin)

    utilidad_total, intereses, multas = calcular_utilidad(fecha_inicio, fecha_fin)
    socias = obtener_ahorros_por_socia(fecha_inicio, fecha_fin)
    tabla = generar_tabla_distribucion(socias, utilidad_total)

    # ---------------- resumen ----------------
    st.subheader("📘 Resumen del ciclo")

    st.write(f"**Saldo inicial:** ${saldo_inicial:,.2f}")
    st.write(f"**Saldo final:** ${saldo_final:,.2f}")
    st.write(f"**Ingresos:** ${ingresos:,.2f}")
    st.write(f"**Egresos:** ${egresos:,.2f}")
    st.write(f"**Intereses:** ${intereses:,.2f}")
    st.write(f"**Multas:** ${multas:,.2f}")
    st.write(f"**Utilidad total:** ${utilidad_total:,.2f}")

    # ---------------- cierre ----------------
    if st.button("🔐 Cerrar ciclo ahora"):
        con = obtener_conexion()
        cur = con.cursor()

        cur.execute("""
            UPDATE ciclo_resumen
            SET fecha_cierre=%s,
                saldo_inicial=%s,
                saldo_final=%s,
                total_ahorros=%s,
                total_prestamos_vigentes=0,
                total_intereses_pendientes=%s,
                total_multas_pendientes=0,
                utilidad_total=%s,
                monto_repartido=0,
                estado='Cerrado'
            WHERE id_ciclo_resumen=%s
        """, (
            fecha_fin,
            saldo_inicial,
            saldo_final,
            sum(s["ahorro"] for s in socias),
            intereses,
            utilidad_total,
            ciclo["id_ciclo_resumen"]
        ))

        con.commit()
        con.close()

        st.success("Ciclo cerrado correctamente.")
        st.balloons()

    # ---------------- actas ----------------
    st.subheader("📄 Acta")

    if st.button("📘 Ver Acta HTML"):
        html = generar_html_acta(
            fecha_inicio, fecha_fin,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            utilidad_total, intereses, multas,
            tabla
        )
        st.markdown(html, unsafe_allow_html=True)

    if st.button("⬇️ Descargar Acta PDF"):
        html = generar_html_acta(
            fecha_inicio, fecha_fin,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            utilidad_total, intereses, multas,
            tabla
        )
        pdf = generar_pdf(html)
        b64 = base64.b64encode(pdf).decode()
        st.markdown(
            f'<a href="data:application/pdf;base64,{b64}" download="Acta_Cierre_CVX.pdf">📥 Descargar PDF</a>',
            unsafe_allow_html=True
        )
