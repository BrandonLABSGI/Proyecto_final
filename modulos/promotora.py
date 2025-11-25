import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from modulos.conexion import obtener_conexion


# ============================================================
# VALIDAR ACCESO SOLO PARA PROMOTORA
# ============================================================
def validar_promotora():
    rol = st.session_state.get("rol", "")
    if rol != "Promotora":
        st.title("Acceso denegado")
        st.warning("Solo las Promotoras pueden acceder a esta sección.")
        st.stop()


# ============================================================
# INTERFAZ PRINCIPAL — MÓDULO DE PROMOTORA
# ============================================================
def interfaz_promotora():

    validar_promotora()

    st.title("👩‍💼 Panel de Promotora — Solidaridad CVX")
    st.write("Supervisión, validación financiera y reportes del distrito asignado.")

    id_promotora = st.session_state.get("id_empleado", None)
    if not id_promotora:
        st.error("No se pudo obtener el ID de la promotora. Vuelva a iniciar sesión.")
        st.stop()

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    opcion = st.radio(
        "Navegación",
        ["🏠 Inicio", "👥 Grupos", "📑 Reportes", "✔ Validaciones", "🚨 Alertas"],
        horizontal=True
    )

    if opcion == "🏠 Inicio":
        dashboard_inicio(id_promotora)

    elif opcion == "👥 Grupos":
        vista_grupos(id_promotora)

    elif opcion == "📑 Reportes":
        reportes_consolidados(id_promotora)

    elif opcion == "✔ Validaciones":
        validaciones_financieras(id_promotora)

    elif opcion == "🚨 Alertas":
        alertas_criticas(id_promotora)


# ============================================================
# SECCIÓN 2 — DASHBOARD (Inicio)
# ============================================================
def dashboard_inicio(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo, Fecha_inicio, Id_Distrito
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No tienes grupos asignados todavía.")
        return
# 1. VALIDAR GRUPOS ASIGNADOS
if not grupos:
    st.warning("No tienes grupos asignados todavía.")
    return

# Extraer lista de IDs
ids = [g["Id_Grupo"] for g in grupos]

# Validar que existan IDs válidos
if not ids:
    st.warning("No existen grupos para este usuario.")
    return

# Construir placeholders seguros para IN (%s, %s, %s)
formato_ids = ','.join(['%s'] * len(ids))


    # SOCIAS
    cursor.execute(f"""
        SELECT Id_Grupo, COUNT(*) AS total
        FROM Socia
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    socias_data = cursor.fetchall()
    dict_socias = {r["Id_Grupo"]: r["total"] for r in socias_data}

    # PRÉSTAMOS
    cursor.execute(f"""
        SELECT Id_Grupo,
               SUM(CASE WHEN Estado = 'Activo' THEN 1 ELSE 0 END) AS activos,
               SUM(CASE WHEN Estado = 'Mora' THEN 1 ELSE 0 END) AS mora
        FROM Prestamo
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    prest_data = cursor.fetchall()
    dict_prest = {r["Id_Grupo"]: r for r in prest_data}

    # AHORROS
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(Monto) AS total
        FROM Ahorro
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    ahorro_rows = cursor.fetchall()
    dict_ahorros = {r["Id_Grupo"]: float(r["total"]) for r in ahorro_rows}

    # CAJA
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(saldo_final) AS caja
        FROM caja_reunion
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    caja_rows = cursor.fetchall()
    dict_caja = {r["Id_Grupo"]: float(r["caja"]) for r in caja_rows}

    cursor.close()
    con.close()

    total_grupos = len(grupos)
    total_socias = sum(dict_socias.values())
    total_activos = sum(r["activos"] for r in dict_prest.values())
    total_mora = sum(r["mora"] for r in dict_prest.values())
    total_ahorro = sum(dict_ahorros.values())
    total_caja = sum(dict_caja.values())

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("📌 Grupos Activos", total_grupos)
    col2.metric("👥 Total de Socias", total_socias)
    col3.metric("💰 Caja Consolidada", f"${total_caja:,.2f}")

    col4.metric("📘 Préstamos Activos", total_activos)
    col5.metric("⚠ Préstamos en Mora", total_mora)
    col6.metric("🏦 Total Ahorro", f"${total_ahorro:,.2f}")

    st.markdown("---")
    st.subheader("📋 Estado de los grupos")

    tabla = []

    for g in grupos:
        gid = g["Id_Grupo"]

        soc = dict_socias.get(gid, 0)
        cah = dict_caja.get(gid, 0)
        aho = dict_ahorros.get(gid, 0)

        p = dict_prest.get(gid, {"activos": 0, "mora": 0})
        act = p["activos"]
        mor = p["mora"]

        total_pres = act + mor
        mora_pct = (mor / total_pres * 100) if total_pres > 0 else 0
        estado = obtener_estado_grupo(mora_pct)

        tabla.append({
            "Grupo": g["Nombre_grupo"],
            "Miembros": soc,
            "Caja": f"${cah:,.2f}",
            "Ahorro": f"${aho:,.2f}",
            "Préstamos activos": act,
            "Préstamos en mora": mor,
            "Mora (%)": f"{mora_pct:.1f}%",
            "Estado": estado
        })

    st.dataframe(tabla, hide_index=True)


# ============================================================
# ESTADO GRUPO
# ============================================================
def obtener_estado_grupo(mora_pct):
    if mora_pct >= 20:
        return "🔴 Alta mora"
    elif mora_pct >= 10:
        return "🟡 Mora moderada"
    else:
        return "🟢 Estable"


# ============================================================
# SECCIÓN 3 — VISTA DE GRUPOS
# ============================================================
def vista_grupos(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo, Fecha_inicio, Id_Distrito
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No tienes grupos asignados.")
        return

    opciones = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}
    sel = st.selectbox("Seleccione un grupo:", opciones.keys())
    gid = opciones[sel]

    cursor.execute("SELECT COUNT(*) AS total FROM Socia WHERE Id_Grupo = %s", (gid,))
    socias_total = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(Monto) AS total FROM Ahorro WHERE Id_Grupo = %s", (gid,))
    ahorro_total = cursor.fetchone()["total"] or 0

    cursor.execute("SELECT SUM(saldo_final) AS total FROM caja_reunion WHERE Id_Grupo = %s", (gid,))
    caja_total = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN Estado='Activo' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN Estado='Mora' THEN 1 ELSE 0 END) AS mora,
            SUM(CASE WHEN Estado='Liquidado' THEN 1 ELSE 0 END) AS liquidados
        FROM Prestamo
        WHERE Id_Grupo = %s
    """, (gid,))
    prest = cursor.fetchone()

    cursor.close()
    con.close()

    st.markdown("### 📝 Resumen del grupo")

    col1, col2, col3 = st.columns(3)
    col1.metric("Miembros", socias_total)
    col2.metric("Caja total", f"${caja_total:,.2f}")
    col3.metric("Ahorro total", f"${ahorro_total:,.2f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Préstamos activos", prest["activos"])
    col5.metric("En mora", prest["mora"])
    col6.metric("Liquidados", prest["liquidados"])

    st.markdown("---")

    with st.expander("👥 Miembros y Ahorros"):
        mostrar_ahorros_grupo(gid)

    with st.expander("📘 Préstamos del grupo"):
        mostrar_prestamos_grupo(gid)

    with st.expander("💰 Caja del grupo"):
        mostrar_caja_grupo(gid)

    with st.expander("⚠ Multas"):
        mostrar_multas_grupo(gid)

    with st.expander("🗓 Asistencia"):
        mostrar_asistencias_grupo(gid)


# ============================================================
# FUNCIONES DE DETALLE
# ============================================================
def mostrar_ahorros_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, a.Monto, a.Fecha_aporte
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)


def mostrar_prestamos_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, p.Monto, p.Interes, p.Cuota,
               p.Estado, p.Fecha_inicio, p.Fecha_limite
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)


def mostrar_caja_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
        ORDER BY fecha DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)


def mostrar_multas_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)


def mostrar_asistencias_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.Fecha, s.Nombre, a.Estado_asistencia
        FROM Asistencia a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY a.Fecha DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)


# ============================================================
# SECCIÓN 4 — VALIDACIONES FINANCIERAS
# ============================================================
def validaciones_financieras(id_promotora):

    st.write("### ✔ Validación de Información Financiera")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No hay grupos asignados.")
        return

    dict_g = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}
    sel = st.selectbox("Seleccione un grupo:", dict_g.keys())
    gid = dict_g[sel]

    tipo = st.radio(
        "Seleccione el tipo de validación:",
        ["Caja", "Préstamos", "Multas"],
        horizontal=True
    )

    if tipo == "Caja":
        validar_caja(gid, id_promotora)

    elif tipo == "Préstamos":
        validar_prestamos(gid, id_promotora)

    elif tipo == "Multas":
        validar_multas(gid, id_promotora)

    cursor.close()
    con.close()


# ============================================================
# VALIDAR CAJA
# ============================================================
def validar_caja(id_grupo, id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
        ORDER BY fecha DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    st.dataframe(datos, hide_index=True)

    obs = st.text_area("Observaciones:")

    if st.button("Marcar como validado"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s, %s, 'Caja', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, obs))
        con.commit()
        st.success("Validación registrada.")

    cursor.close()
    con.close()


# ============================================================
# VALIDAR PRÉSTAMOS
# ============================================================
def validar_prestamos(id_grupo, id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, p.Monto, p.Interes, p.Cuota, p.Estado
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    st.dataframe(datos, hide_index=True)

    obs = st.text_area("Observaciones:")

    if st.button("Validar"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s,%s,'Prestamos',NOW(),'Validado',%s)
        """, (id_grupo, id_promotora, obs))
        con.commit()
        st.success("Préstamos validados.")

    cursor.close()
    con.close()


# ============================================================
# VALIDAR MULTAS
# ============================================================
def validar_multas(id_grupo, id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    st.dataframe(datos, hide_index=True)

    obs = st.text_area("Observaciones:")

    if st.button("Validar multas"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s,%s,'Multas',NOW(),'Validado',%s)
        """, (id_grupo, id_promotora, obs))
        con.commit()
        st.success("Multas validadas.")

    cursor.close()
    con.close()


# ============================================================
# REPORTES CONSOLIDADOS
# ============================================================
def reportes_consolidados(id_promotora):

    st.write("### 📑 Reportes Consolidados del Distrito")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No hay grupos asignados.")
        return

    dict_g = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    sel = st.selectbox("Seleccione un grupo:", dict_g.keys())
    gid = dict_g[sel]

    tipo = st.radio(
        "Seleccione el reporte:",
        ["Caja", "Préstamos", "Ahorros", "Asistencia"],
        horizontal=True
    )

    if tipo == "Caja":
        generar_reporte_caja(gid)
    elif tipo == "Préstamos":
        generar_reporte_prestamos(gid)
    elif tipo == "Ahorros":
        generar_reporte_ahorro(gid)
    elif tipo == "Asistencia":
        generar_reporte_asistencia(gid)

    cursor.close()
    con.close()


# ============================================================
# REPORTES PDF & EXCEL
# ============================================================
def generar_reporte_caja(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay datos.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    # Excel
    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Caja")

    st.download_button("📥 Excel", excel.getvalue(),
                       file_name="Caja.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF
    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)
    c.setFont("Helvetica", 10)

    y = 750
    for _, row in df.iterrows():
        c.drawString(40, y, str(row.to_dict()))
        y -= 16
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750

    c.save()

    st.download_button("📄 PDF", pdf.getvalue(),
                       file_name="Caja.pdf",
                       mime="application/pdf")


def generar_reporte_prestamos(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, p.Monto, p.Interes, p.Cuota, p.Estado
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay datos.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Prestamos")

    st.download_button("📥 Excel", excel.getvalue(),
                       file_name="Prestamos.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)
    c.setFont("Helvetica", 10)

    y = 750
    for _, row in df.iterrows():
        c.drawString(40, y, str(row.to_dict()))
        y -= 16
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 750

    c.save()

    st.download_button("📄 PDF", pdf.getvalue(),
                       file_name="Prestamos.pdf",
                       mime="application/pdf")


def generar_reporte_ahorro(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, a.Monto, a.Fecha_aporte
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay datos.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Ahorro")

    st.download_button("📥 Excel", excel.getvalue(),
                       file_name="Ahorro.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)
    c.setFont("Helvetica", 10)

    y = 750
    for _, row in df.iterrows():
        c.drawString(40, y, str(row.to_dict()))
        y -= 16
        if y < 50:
            c.showPage()
            y = 750

    c.save()

    st.download_button("📄 PDF", pdf.getvalue(),
                       file_name="Ahorro.pdf",
                       mime="application/pdf")


def generar_reporte_asistencia(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.Fecha, s.Nombre, a.Estado_asistencia
        FROM Asistencia a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay datos.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Asistencia")

    st.download_button("📥 Excel", excel.getvalue(),
                       file_name="Asistencia.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)
    c.setFont("Helvetica", 10)

    y = 750
    for _, row in df.iterrows():
        c.drawString(40, y, str(row.to_dict()))
        y -= 16
        if y < 60:
            c.showPage()
            y = 750

    c.save()

    st.download_button("📄 PDF", pdf.getvalue(),
                       file_name="Asistencia.pdf",
                       mime="application/pdf")


# ============================================================
# SECCIÓN 6 — ALERTAS AUTOMÁTICAS
# ============================================================
def alertas_criticas(id_promotora):

    st.write("### 🚨 Alertas automáticas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos asignados.")
        return

    ids = [g["Id_Grupo"] for g in grupos]
    if len(ids) == 0:
        st.info("Sin grupos.")
        return

    formato_ids = ','.join(['%s'] * len(ids))

    # ALERTA MORA
    cursor.execute(f"""
        SELECT Id_Grupo,
               SUM(CASE WHEN Estado='Mora' THEN 1 ELSE 0 END) AS mora,
               COUNT(*) AS total
        FROM Prestamo
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    prest = cursor.fetchall()

    alerta_mora = []
    for r in prest:
        if r["total"] == 0:
            continue
        pct = r["mora"] / r["total"] * 100
        if pct >= 10:
            alerta_mora.append({
                "Grupo": r["Id_Grupo"],
                "Mora (%)": f"{pct:.1f}%"
            })

    st.subheader("🔴 Mora elevada")
    st.dataframe(alerta_mora, hide_index=True)

    cursor.close()
    con.close()
