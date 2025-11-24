import streamlit as st
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

    # ------------------------------------------------------------
    # BOTÓN CERRAR SESIÓN
    # ------------------------------------------------------------
    if st.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["rol"] = None
        st.rerun()

    st.markdown("---")

    # ============================================================
    # MENÚ HORIZONTAL (Opción B minimalista)
    # ============================================================
    opcion = st.radio(
        "Navegación",
        ["🏠 Inicio", "👥 Grupos", "📑 Reportes", "✔ Validaciones", "🚨 Alertas"],
        horizontal=True
    )

    # ============================================================
    # SECCIONES (vacías por ahora)
    # se llenan en la SECCIÓN 2, 3, 4, 5 y 6
    # ============================================================

    if opcion == "🏠 Inicio":
        st.subheader("Dashboard general del distrito")
        st.info("Aquí irá el Dashboard consolidado (SECCIÓN 2).")

    elif opcion == "👥 Grupos":
        st.subheader("Gestión de grupos supervisados")
        st.info("Aquí irá la vista de grupos (SECCIÓN 3).")

    elif opcion == "📑 Reportes":
        st.subheader("Reportes consolidados")
        st.info("Aquí irán los reportes PDF/Excel (SECCIÓN 5).")

    elif opcion == "✔ Validaciones":
        st.subheader("Validación de información financiera")
        st.info("Aquí irán las validaciones de caja, préstamos y ciclos (SECCIÓN 4).")

    elif opcion == "🚨 Alertas":
        st.subheader("Alertas automáticas")
        st.info("Aquí irán las alertas de mora, inconsistencias y cierres pendientes (SECCIÓN 6).")
# ============================================================
# SECCIÓN 2 — DASHBOARD (Inicio)
# ============================================================

def dashboard_inicio(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # 1. GRUPOS SUPERVISADOS POR LA PROMOTORA
    # ------------------------------------------------------------
    cursor.execute("""
        SELECT g.Id_Grupo, g.Nombre_grupo, g.Fecha_inicio, g.Id_Distrito
        FROM Grupo g
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No tienes grupos asignados todavía.")
        return

    # Lista de IDs de grupos
    ids = [g["Id_Grupo"] for g in grupos]

    # ------------------------------------------------------------
    # 2. SOCIAS
    # ------------------------------------------------------------
    cursor.execute(f"""
        SELECT Id_Grupo, COUNT(*) as total
        FROM Socia
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    socias_data = cursor.fetchall()
    dict_socias = {row["Id_Grupo"]: row["total"] for row in socias_data}

    # ------------------------------------------------------------
    # 3. PRÉSTAMOS (activos y en mora)
    # ------------------------------------------------------------
    cursor.execute(f"""
        SELECT Id_Grupo,
               SUM(CASE WHEN Estado = 'Activo' THEN 1 ELSE 0 END) AS activos,
               SUM(CASE WHEN Estado = 'Mora' THEN 1 ELSE 0 END) AS mora
        FROM Prestamo
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    prestamos_data = cursor.fetchall()
    dict_prestamos = {row["Id_Grupo"]: row for row in prestamos_data}

    # ------------------------------------------------------------
    # 4. AHORROS
    # ------------------------------------------------------------
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(Monto) AS total
        FROM Ahorro
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    ahorros_data = cursor.fetchall()
    dict_ahorros = {row["Id_Grupo"]: float(row["total"]) for row in ahorros_data}

    # ------------------------------------------------------------
    # 5. CAJA CONSOLIDADA (usando tabla caja_reunion)
    # ------------------------------------------------------------
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(saldo_final) AS caja
        FROM caja_reunion
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    caja_data = cursor.fetchall()
    dict_caja = {row["Id_Grupo"]: float(row["caja"]) for row in caja_data}

    cursor.close()
    con.close()

    # ============================================================
    # TARJETAS — KPIs PRINCIPALES
    # ============================================================
    total_grupos = len(grupos)
    total_socias = sum(dict_socias.values())
    total_prestamos_activos = sum(row["activos"] for row in dict_prestamos.values())
    total_prestamos_mora = sum(row["mora"] for row in dict_prestamos.values())
    total_caja = sum(dict_caja.values())
    total_ahorro = sum(dict_ahorros.values())

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("📌 Grupos Activos", total_grupos)
    col2.metric("👥 Total de Socias", total_socias)
    col3.metric("💰 Caja Consolidada", f"${total_caja:,.2f}")

    col4.metric("📘 Préstamos Activos", total_prestamos_activos)
    col5.metric("⚠ Préstamos en Mora", total_prestamos_mora)
    col6.metric("🏦 Total Ahorro", f"${total_ahorro:,.2f}")

    st.markdown("---")
    st.subheader("📋 Estado de los grupos supervisados")

    # ============================================================
    # TABLA RESUMIDA DE GRUPOS
    # ============================================================
    tabla = []

    for g in grupos:
        gid = g["Id_Grupo"]

        socias = dict_socias.get(gid, 0)
        caja = dict_caja.get(gid, 0)
        ahorros = dict_ahorros.get(gid, 0)

        prest = dict_prestamos.get(gid, {"activos": 0, "mora": 0})
        activos = prest["activos"]
        mora = prest["mora"]

        # Calcular porcentaje de mora
        total_pres = activos + mora
        mora_pct = (mora / total_pres * 100) if total_pres > 0 else 0

        # Estado visual
        estado = obtener_estado_grupo(mora_pct)

        tabla.append({
            "Grupo": g["Nombre_grupo"],
            "Miembros": socias,
            "Caja": f"${caja:,.2f}",
            "Ahorro": f"${ahorros:,.2f}",
            "Préstamos activos": activos,
            "Préstamos en mora": mora,
            "Mora (%)": f"{mora_pct:.1f}%",
            "Estado": estado
        })

    st.dataframe(tabla, hide_index=True)


# ============================================================
# FUNCIÓN PARA OBTENER EL ESTADO VISUAL DEL GRUPO
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

    # ------------------------------------------------------------
    # 1. GRUPOS SUPERVISADOS POR LA PROMOTORA
    # ------------------------------------------------------------
    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo, Fecha_inicio, Id_Distrito
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No tienes grupos asignados actualmente.")
        return

    # Selector de grupo
    opciones = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}
    nombre_sel = st.selectbox("Seleccione un grupo:", opciones.keys())
    id_grupo = opciones[nombre_sel]

    # ------------------------------------------------------------
    # Cargar datos principales del grupo
    # ------------------------------------------------------------
    cursor.execute("SELECT * FROM Grupo WHERE Id_Grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()

    # Obtener total de socias
    cursor.execute("SELECT COUNT(*) AS total FROM Socia WHERE Id_Grupo = %s", (id_grupo,))
    socias_total = cursor.fetchone()["total"]

    # Ahorro total del grupo
    cursor.execute("SELECT SUM(Monto) AS total FROM Ahorro WHERE Id_Grupo = %s", (id_grupo,))
    ahorro_total = cursor.fetchone()["total"] or 0

    # Caja total del grupo (suma de saldos finales)
    cursor.execute("SELECT SUM(saldo_final) AS total FROM caja_reunion WHERE Id_Grupo = %s", (id_grupo,))
    caja_total = cursor.fetchone()["total"] or 0

    # Préstamos activos y en mora
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN Estado = 'Activo' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN Estado = 'Mora' THEN 1 ELSE 0 END) AS mora,
            SUM(CASE WHEN Estado = 'Liquidado' THEN 1 ELSE 0 END) AS liquidados
        FROM Prestamo
        WHERE Id_Grupo = %s
    """, (id_grupo,))
    prest_data = cursor.fetchone()

    cursor.close()
    con.close()

    # ------------------------------------------------------------
    # RESUMEN DEL GRUPO
    # ------------------------------------------------------------
    st.markdown("### 📝 Resumen del grupo seleccionado")

    col1, col2, col3 = st.columns(3)
    col1.metric("Miembros", socias_total)
    col2.metric("Caja total", f"${caja_total:,.2f}")
    col3.metric("Ahorro total", f"${ahorro_total:,.2f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Préstamos activos", prest_data["activos"])
    col5.metric("En mora", prest_data["mora"])
    col6.metric("Liquidados", prest_data["liquidados"])

    st.markdown("---")

    # ============================================================
    # DETALLES DEL GRUPO — ACORDEÓN
    # ============================================================

    with st.expander("👥 Miembros y Ahorros"):
        mostrar_ahorros_grupo(id_grupo)

    with st.expander("📘 Préstamos del grupo"):
        mostrar_prestamos_grupo(id_grupo)

    with st.expander("💰 Caja y movimientos"):
        mostrar_caja_grupo(id_grupo)

    with st.expander("⚠ Multas aplicadas"):
        mostrar_multas_grupo(id_grupo)

    with st.expander("🗓 Asistencias y reuniones"):
        mostrar_asistencias_grupo(id_grupo)

    with st.expander("🔵 Estado del ciclo"):
        mostrar_ciclo_grupo(id_grupo)



# ============================================================
# SUBSECCIONES DE DETALLES
# ============================================================

def mostrar_ahorros_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre AS Socia, a.Monto, a.Fecha_aporte
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY a.Fecha_aporte DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay registros de ahorro.")
        return

    st.dataframe(datos, hide_index=True)



def mostrar_prestamos_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre AS Socia, p.Monto, p.Interes, p.Cuota,
               p.Estado, p.Fecha_inicio, p.Fecha_limite
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
        ORDER BY p.Fecha_inicio DESC
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
        SELECT s.Nombre AS Socia, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
        ORDER BY m.Fecha_aplicacion DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)



def mostrar_asistencias_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.fecha, s.Nombre AS Socia, a.estado_asistencia
        FROM Asistencia a
        JOIN Reunion r ON r.Id_Reunion = a.Id_Reunion
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY r.fecha DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)



def mostrar_ciclo_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Fecha_inicio, Fecha_fin, Estado
        FROM Ciclo
        WHERE Id_Grupo = %s
        ORDER BY Fecha_inicio DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    st.dataframe(datos, hide_index=True)
# ============================================================
# SECCIÓN 4 — VALIDACIONES FINANCIERAS
# ============================================================

def validaciones_financieras(id_promotora):

    st.write("### ✔ Validación de Información Financiera y Técnica")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # 1. GRUPOS DE LA PROMOTORA
    # ------------------------------------------------------------
    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No hay grupos asignados.")
        return

    grupos_dict = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    grupo_sel = st.selectbox("Seleccione un grupo para validar:", grupos_dict.keys())
    id_grupo = grupos_dict[grupo_sel]

    st.markdown("---")

    # Panel de validación
    tipo_validacion = st.radio(
        "Seleccione el tipo de validación:",
        ["Caja", "Préstamos", "Multas", "Cierre de ciclo"],
        horizontal=True
    )

    # ------------------------------------------------------------
    # VALIDAR CAJA
    # ------------------------------------------------------------
    if tipo_validacion == "Caja":
        validar_caja(id_grupo, id_promotora)

    # ------------------------------------------------------------
    # VALIDAR PRÉSTAMOS
    # ------------------------------------------------------------
    elif tipo_validacion == "Préstamos":
        validar_prestamos(id_grupo, id_promotora)

    # ------------------------------------------------------------
    # VALIDAR MULTAS
    # ------------------------------------------------------------
    elif tipo_validacion == "Multas":
        validar_multas(id_grupo, id_promotora)

    # ------------------------------------------------------------
    # VALIDAR CIERRE
    # ------------------------------------------------------------
    elif tipo_validacion == "Cierre de ciclo":
        validar_cierre(id_grupo, id_promotora)

    cursor.close()
    con.close()



# ============================================================
# VALIDAR CAJA
# ============================================================
def validar_caja(id_grupo, id_promotora):

    st.subheader("💰 Validación de Caja")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
        ORDER BY fecha DESC
    """, (id_grupo,))
    registros = cursor.fetchall()

    st.dataframe(registros, hide_index=True)

    observ = st.text_area("Observaciones:")

    if st.button("Marcar como validado", type="primary"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s, %s, 'Caja', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Caja validada exitosamente.")

    cursor.close()
    con.close()



# ============================================================
# VALIDAR PRÉSTAMOS
# ============================================================
def validar_prestamos(id_grupo, id_promotora):

    st.subheader("📘 Validación de Préstamos")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, p.Monto, p.Interes, p.Cuota, p.Estado, p.Fecha_inicio
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
    """, (id_grupo,))
    prestamos = cursor.fetchall()

    st.dataframe(prestamos, hide_index=True)

    observ = st.text_area("Observaciones:")

    if st.button("Validar préstamos", type="primary"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s, %s, 'Prestamos', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Préstamos validados correctamente.")

    cursor.close()
    con.close()



# ============================================================
# VALIDAR MULTAS
# ============================================================
def validar_multas(id_grupo, id_promotora):

    st.subheader("⚠ Validación de Multas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
    """, (id_grupo,))
    multas = cursor.fetchall()

    st.dataframe(multas, hide_index=True)

    observ = st.text_area("Observaciones:")

    if st.button("Validar multas", type="primary"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s, %s, 'Multas', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Multas validadas con éxito.")

    cursor.close()
    con.close()



# ============================================================
# VALIDAR CIERRE DE CICLO
# ============================================================
def validar_cierre(id_grupo, id_promotora):

    st.subheader("🔵 Validación de Cierre de Ciclo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Fecha_inicio, Fecha_fin, Estado
        FROM Ciclo
        WHERE Id_Grupo = %s
        ORDER BY Fecha_inicio DESC
        LIMIT 1
    """, (id_grupo,))
    ciclo = cursor.fetchone()

    if ciclo:
        st.write("### Estado del ciclo:")
        st.write(ciclo)
    else:
        st.info("Este grupo no tiene un ciclo registrado.")

    observ = st.text_area("Observaciones del cierre:")

    if st.button("Validar cierre de ciclo", type="primary"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s, %s, 'Ciclo', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Cierre de ciclo validado correctamente.")

    cursor.close()
    con.close()
# ============================================================
# SECCIÓN 5 — REPORTES PDF + EXCEL
# ============================================================

import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def reportes_consolidados(id_promotora):

    st.write("### 📑 Reportes Consolidados del Distrito")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # GRUPOS SUPERVISADOS
    # ------------------------------------------------------------
    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No tienes grupos asignados.")
        return

    grupos_dict = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    grupo_sel = st.selectbox("Seleccione un grupo:", grupos_dict.keys())
    id_grupo = grupos_dict[grupo_sel]

    st.markdown("---")

    # Tipo de reporte
    tipo = st.radio(
        "Seleccione el tipo de reporte:",
        ["Caja", "Préstamos", "Ahorros", "Asistencia"],
        horizontal=True
    )

    if tipo == "Caja":
        generar_reporte_caja(id_grupo)

    elif tipo == "Préstamos":
        generar_reporte_prestamos(id_grupo)

    elif tipo == "Ahorros":
        generar_reporte_ahorro(id_grupo)

    elif tipo == "Asistencia":
        generar_reporte_asistencia(id_grupo)

    cursor.close()
    con.close()


# ============================================================
# REPORTE CAJA (PDF y Excel)
# ============================================================
def generar_reporte_caja(id_grupo):

    st.subheader("💰 Reporte de Caja")

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

    if not datos:
        st.info("No existen registros de caja para este grupo.")
        return

    df = pd.DataFrame(datos)

    st.dataframe(df, hide_index=True)

    # ------------------------------------------------------------
    # DESCARGAR EXCEL
    # ------------------------------------------------------------
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Caja")

    st.download_button(
        "📥 Descargar Excel",
        data=excel_buffer.getvalue(),
        file_name="Reporte_Caja.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ------------------------------------------------------------
    # DESCARGAR PDF
    # ------------------------------------------------------------
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 760, "Reporte de Caja")

    c.setFont("Helvetica", 10)
    y = 730
    for _, row in df.iterrows():
        texto = f"{row['fecha']} | Inicial: {row['saldo_inicial']} | Ing: {row['ingresos']} | Egr: {row['egresos']} | Final: {row['saldo_final']}"
        c.drawString(50, y, texto)
        y -= 18
        if y < 50:
            c.showPage()
            y = 750

    c.save()

    st.download_button(
        "📄 Descargar PDF",
        data=pdf_buffer.getvalue(),
        file_name="Reporte_Caja.pdf",
        mime="application/pdf"
    )



# ============================================================
# REPORTE PRÉSTAMOS
# ============================================================
def generar_reporte_prestamos(id_grupo):

    st.subheader("📘 Reporte de Préstamos")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre AS Socia, p.Monto, p.Interes, p.Cuota, 
               p.Estado, p.Fecha_inicio, p.Fecha_limite
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
        ORDER BY p.Fecha_inicio DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No existen préstamos registrados.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Prestamos")

    st.download_button(
        "📥 Descargar Excel",
        data=buffer.getvalue(),
        file_name="Reporte_Prestamos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 760, "Reporte de Préstamos del Grupo")

    c.setFont("Helvetica", 10)
    y = 730
    for _, row in df.iterrows():
        texto = f"{row['Socia']} | ${row['Monto']} | {row['Estado']}"
        c.drawString(50, y, texto)
        y -= 18
        if y < 60:
            c.showPage()
            y = 750

    c.save()

    st.download_button(
        "📄 Descargar PDF",
        data=pdf_buffer.getvalue(),
        file_name="Reporte_Prestamos.pdf",
        mime="application/pdf"
    )



# ============================================================
# REPORTE AHORROS
# ============================================================
def generar_reporte_ahorro(id_grupo):

    st.subheader("🏦 Reporte de Ahorros")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre AS Socia, a.Monto, a.Fecha_aporte
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY a.Fecha_aporte DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No hay ahorros registrados.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Ahorro")

    st.download_button(
        "📥 Descargar Excel",
        data=buffer.getvalue(),
        file_name="Reporte_Ahorro.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF
    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 760, "Reporte de Ahorros del Grupo")

    c.setFont("Helvetica", 10)
    y = 730
    for _, row in df.iterrows():
        texto = f"{row['Fecha_aporte']} | {row['Socia']} | ${row['Monto']}"
        c.drawString(50, y, texto)
        y -= 18
        if y < 50:
            c.showPage()
            y = 750

    c.save()

    st.download_button(
        "📄 Descargar PDF",
        data=pdf.getvalue(),
        file_name="Reporte_Ahorro.pdf",
        mime="application/pdf"
    )



# ============================================================
# REPORTE ASISTENCIA
# ============================================================
def generar_reporte_asistencia(id_grupo):

    st.subheader("🗓 Reporte de Asistencias")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.fecha, s.Nombre AS Socia, a.estado_asistencia
        FROM Asistencia a
        JOIN Reunion r ON r.Id_Reunion = a.Id_Reunion
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY r.fecha DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()

    if not datos:
        st.info("No existen registros de asistencia.")
        return

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True)

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Asistencia")

    st.download_button(
        "📥 Descargar Excel",
        data=buffer.getvalue(),
        file_name="Reporte_Asistencia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF
    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=letter)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 760, "Reporte de Asistencia del Grupo")

    c.setFont("Helvetica", 10)
    y = 730
    for _, row in df.iterrows():
        texto = f"{row['fecha']} | {row['Socia']} | {row['estado_asistencia']}"
        c.drawString(50, y, texto)
        y -= 18
        if y < 60:
            c.showPage()
            y = 750

    c.save()

    st.download_button(
        "📄 Descargar PDF",
        data=pdf.getvalue(),
        file_name="Reporte_Asistencia.pdf",
        mime="application/pdf"
    )
# ============================================================
# SECCIÓN 6 — ALERTAS AUTOMÁTICAS
# ============================================================

def alertas_criticas(id_promotora):

    st.write("### 🚨 Alertas Automáticas del Distrito")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # 1. OBTENER GRUPOS ASIGNADOS
    # ------------------------------------------------------------
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

    # ============================================================
    # ALERTA 1 — MOROSIDAD
    # ============================================================
    st.subheader("🔴 Alta Mora / 🟡 Mora Moderada")

    cursor.execute(f"""
        SELECT Id_Grupo,
               SUM(CASE WHEN Estado = 'Mora' THEN 1 ELSE 0 END) AS mora,
               SUM(CASE WHEN Estado IN ('Mora','Activo') THEN 1 ELSE 0 END) AS total
        FROM Prestamo
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    mora_data = cursor.fetchall()

    alertas_mora = []
    for row in mora_data:
        total = row["total"] or 0
        if total == 0:
            continue
        pct = (row["mora"] / total * 100)
        if pct >= 20:
            estado = "🔴 Alta mora"
        elif pct >= 10:
            estado = "🟡 Mora moderada"
        else:
            continue
        alertas_mora.append({
            "Id_Grupo": row["Id_Grupo"],
            "Mora (%)": f"{pct:.1f}%",
            "Estado": estado
        })
    st.dataframe(alertas_mora, hide_index=True)

    st.markdown("---")

    # ============================================================
    # ALERTA 2 — CAJA NEGATIVA O INCONSISTENTE
    # ============================================================
    st.subheader("💰 Caja Inconsistente o Negativa")

    cursor.execute(f"""
        SELECT Id_Grupo, fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        ORDER BY fecha DESC
    """, ids)
    caja_rows = cursor.fetchall()

    alertas_caja = []
    for row in caja_rows:
        final = float(row["saldo_final"])
        calc = float(row["saldo_inicial"] + row["ingresos"] - row["egresos"])

        if final < 0 or abs(final - calc) > 0.01:
            alertas_caja.append({
                "Id_Grupo": row["Id_Grupo"],
                "Fecha": row["fecha"],
                "Saldo Final": final,
                "Esperado": calc,
                "Alerta": "❌ Caja inconsistente"
            })

    st.dataframe(alertas_caja, hide_index=True)

    st.markdown("---")

    # ============================================================
    # ALERTA 3 — GASTOS INUSUALES
    # ============================================================
    st.subheader("📉 Gastos Inusuales")

    cursor.execute(f"""
        SELECT Id_Grupo, SUM(Monto) AS total
        FROM Gastos_grupo
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    gastos = cursor.fetchall()
    dict_gastos = {row["Id_Grupo"]: float(row["total"]) for row in gastos}

    cursor.execute(f"""
        SELECT Id_Grupo, SUM(ingresos) AS ingresos
        FROM caja_reunion
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
        GROUP BY Id_Grupo
    """, ids)
    ingresos = cursor.fetchall()
    dict_ingresos = {row["Id_Grupo"]: float(row["ingresos"]) for row in ingresos}

    alertas_gastos = []
    for gid in ids:
        g_total = dict_gastos.get(gid, 0)
        i_total = dict_ingresos.get(gid, 0)

        if g_total > max(i_total * 0.8, 200):  # criterio simple
            alertas_gastos.append({
                "Id_Grupo": gid,
                "Gastos": g_total,
                "Ingresos": i_total,
                "Alerta": "⚠ Gastos excesivos"
            })

    st.dataframe(alertas_gastos, hide_index=True)

    st.markdown("---")

    # ============================================================
    # ALERTA 4 — CICLO PENDIENTE DE CIERRE
    # ============================================================
    st.subheader("🕒 Ciclos Pendientes de Cierre")

    cursor.execute(f"""
        SELECT Id_Grupo, Fecha_inicio, Fecha_fin, Estado
        FROM Ciclo
        WHERE Id_Grupo IN ({','.join(['%s']*len(ids))})
    """, ids)
    ciclos = cursor.fetchall()

    alertas_ciclo = []
    for c in ciclos:
        if c["Estado"] == "Pendiente":
            alertas_ciclo.append({
                "Id_Grupo": c["Id_Grupo"],
                "Fecha Inicio": c["Fecha_inicio"],
                "Fecha Fin": c["Fecha_fin"],
                "Estado": "🔵 Pendiente de cierre"
            })

    st.dataframe(alertas_ciclo, hide_index=True)

    cursor.close()
    con.close()
