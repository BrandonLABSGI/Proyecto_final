import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from modulos.conexion import obtener_conexion


# ==========================================
# VALIDACIÓN (AHORA SOLO OCULTA ACCESO)
# ==========================================
def validar_promotora():
    # La promotora no crea ni modifica nada, solo ve reportes
    # Para directiva no bloqueamos esta vista
    rol = st.session_state.get("rol", "")
    if rol not in ["Promotora", "Director"]:
        st.title("Acceso denegado")
        st.warning("Solo la Promotora o Directiva pueden ver esta sección.")
        st.stop()


# ==========================================
# INTERFAZ GENERAL
# ==========================================
def interfaz_promotora():

    validar_promotora()

    st.title("👩‍💼 Panel de Promotora — Solidaridad CVX")
    st.write("Supervisión, validación financiera y reportes del distrito asignado.")

    # Como el sistema hoy solo usa un grupo, no dependemos de ID de promotora
    id_promotora = 1

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
        dashboard_inicio()

    elif opcion == "👥 Grupos":
        vista_grupos()

    elif opcion == "📑 Reportes":
        reportes_consolidados()

    elif opcion == "✔ Validaciones":
        validaciones_financieras()

    elif opcion == "🚨 Alertas":
        alertas_criticas()


# ==========================================
# REPORTES CONSOLIDADOS (placeholder)
# ==========================================
def reportes_consolidados():
    st.subheader("📑 Reportes Consolidados")
    st.info("Esta sección estará disponible próximamente.")


# ==========================================
# DASHBOARD — SOLO PARA GRUPO FOSFORITOS
# ==========================================
def dashboard_inicio():

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # El grupo actual del sistema
    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo, Fecha_inicio, Id_Distrito
        FROM Grupo
        WHERE Nombre_grupo = 'Fosforitos'
    """)
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No existe el grupo principal en la base de datos.")
        return

    ids = [g["Id_Grupo"] for g in grupos]
    gid = ids[0]

    formato_ids = ",".join(["%s"] * len(ids))

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
               SUM(CASE WHEN Estado_del_prestamo = 'Activo' THEN 1 ELSE 0 END) AS activos,
               SUM(CASE WHEN Estado_del_prestamo = 'Mora' THEN 1 ELSE 0 END) AS mora
        FROM Prestamo
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    prest_data = cursor.fetchall()
    dict_prest = {r["Id_Grupo"]: r for r in prest_data}

    # AHORROS
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(Monto_del_aporte) AS total
        FROM Ahorro
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    ahorro_rows = cursor.fetchall()
    dict_ahorros = {r["Id_Grupo"]: float(r["total"]) for r in ahorro_rows} if ahorro_rows else {gid: 0}

    # CAJA
    cursor.execute(f"""
        SELECT Id_Grupo, SUM(saldo_final) AS caja
        FROM caja_reunion
        WHERE Id_Grupo IN ({formato_ids})
        GROUP BY Id_Grupo
    """, ids)
    caja_rows = cursor.fetchall()
    dict_caja = {r["Id_Grupo"]: float(r["caja"]) for r in caja_rows} if caja_rows else {gid: 0}

    cursor.close()
    con.close()

    total_socias = dict_socias.get(gid, 0)
    activos = dict_prest.get(gid, {}).get("activos", 0)
    mora = dict_prest.get(gid, {}).get("mora", 0)
    ahorro = dict_ahorros.get(gid, 0)
    caja = dict_caja.get(gid, 0)

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("📌 Grupos Activos", 1)
    col2.metric("👥 Total de Socias", total_socias)
    col3.metric("💰 Caja Consolidada", f"${caja:,.2f}")

    col4.metric("📘 Préstamos Activos", activos)
    col5.metric("⚠ Préstamos en Mora", mora)
    col6.metric("🏦 Total Ahorro", f"${ahorro:,.2f}")

    st.markdown("---")
    st.subheader("📋 Estado del grupo")

    # Mostrar tabla resumen
    tabla = [{
        "Grupo": "Fosforitos",
        "Miembros": total_socias,
        "Caja": f"${caja:,.2f}",
        "Ahorro": f"${ahorro:,.2f}",
        "Préstamos activos": activos,
        "Préstamos en mora": mora,
        "Mora (%)": f"{(mora/activos*100 if activos else 0):.1f}%",
        "Estado": obtener_estado_grupo(mora)
    }]

    st.dataframe(tabla, hide_index=True)


def obtener_estado_grupo(mora):
    if mora >= 2:
        return "🔴 Alta mora"
    elif mora == 1:
        return "🟡 Mora moderada"
    return "🟢 Estable"


# ==========================================
# VISTA DE GRUPOS
# ==========================================
def vista_grupos():

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Nombre_grupo = 'Fosforitos'
    """)
    grupo = cursor.fetchone()

    if not grupo:
        st.warning("No existe el grupo.")
        return

    gid = grupo["Id_Grupo"]

    # Conteos
    cursor.execute("SELECT COUNT(*) AS total FROM Socia WHERE Id_Grupo = %s", (gid,))
    socias_total = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(Monto_del_aporte) AS total FROM Ahorro WHERE Id_Grupo = %s", (gid,))
    ahorro_total = cursor.fetchone()["total"] or 0

    cursor.execute("SELECT SUM(saldo_final) AS total FROM caja_reunion WHERE Id_Grupo = %s", (gid,))
    caja_total = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN Estado_del_prestamo='Activo' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN Estado_del_prestamo='Mora' THEN 1 ELSE 0 END) AS mora,
            SUM(CASE WHEN Estado_del_prestamo='Liquidado' THEN 1 ELSE 0 END) AS liquidados
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


# ==========================================
# FUNCIONES DETALLE (100% compatibles)
# ==========================================
def mostrar_ahorros_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.Nombre, a.Monto_del_aporte AS Monto, a.Fecha_del_aporte
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
        SELECT 
            s.Nombre, 
            p.`Monto prestado` AS Monto,
            p.Interes_total,
            p.Cuotas,
            p.Estado_del_prestamo AS Estado,
            p.`Fecha del préstamo` AS Fecha_inicio
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

    sql = """
        SELECT 
            s.Nombre,
            t.`Tipo de multa` AS Tipo,
            m.Monto,
            m.Fecha_aplicacion,
            m.Estado
        FROM Multa m
        JOIN `Tipo de multa` t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Asistencia a ON a.Id_Asistencia = m.Id_Asistencia
        JOIN Reunion r ON r.Id_Reunion = a.Id_Reunion
        WHERE r.Id_Grupo = %s
        ORDER BY m.Id_Multa DESC
    """

    cursor.execute(sql, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()
    st.dataframe(datos, hide_index=True)


def mostrar_asistencias_grupo(id_grupo):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT 
            a.Fecha,
            s.Nombre,
            a.Estado_asistencia
        FROM Asistencia a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        JOIN Reunion r ON r.Id_Reunion = a.Id_Reunion
        WHERE r.Id_Grupo = %s
        ORDER BY a.Fecha DESC
    """

    cursor.execute(sql, (id_grupo,))
    datos = cursor.fetchall()

    cursor.close()
    con.close()
    st.dataframe(datos, hide_index=True)


# ==========================================
# VALIDACIONES
# ==========================================
def validaciones_financieras():

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Nombre_grupo = 'Fosforitos'
    """)
    grupo = cursor.fetchone()

    if not grupo:
        st.warning("No existe el grupo principal.")
        return

    gid = grupo["Id_Grupo"]

    tipo = st.radio(
        "Seleccione el tipo de validación:",
        ["Caja", "Préstamos", "Multas"],
        horizontal=True
    )

    if tipo == "Caja":
        validar_caja(gid)

    elif tipo == "Préstamos":
        validar_prestamos(gid)

    elif tipo == "Multas":
        validar_multas(gid)

    cursor.close()
    con.close()


def validar_caja(id_grupo):

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
            VALUES(%s, 1, 'Caja', NOW(), 'Validado', %s)
        """, (id_grupo, obs))
        con.commit()
        st.success("Validación registrada.")

    cursor.close()
    con.close()


def validar_prestamos(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            s.Nombre, 
            p.`Monto prestado` AS Monto, 
            p.Interes_total, 
            p.Cuotas,
            p.Estado_del_prestamo AS Estado
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
            VALUES(%s,1,'Prestamos',NOW(),'Validado',%s)
        """, (id_grupo, obs))
        con.commit()
        st.success("Préstamos validados.")

    cursor.close()
    con.close()


def validar_multas(id_grupo):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            s.Nombre,
            t.`Tipo de multa` AS Tipo,
            m.Monto,
            m.Fecha_aplicacion,
            m.Estado
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN `Tipo de multa` t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        JOIN Asistencia a ON a.Id_Asistencia = m.Id_Asistencia
        JOIN Reunion r ON r.Id_Reunion = a.Id_Reunion
        WHERE r.Id_Grupo = %s
        ORDER BY m.Id_Multa DESC
    """, (id_grupo,))
    datos = cursor.fetchall()

    st.dataframe(datos, hide_index=True)

    obs = st.text_area("Observaciones:")

    if st.button("Validar multas"):
        cursor.execute("""
            INSERT INTO Validaciones(Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES(%s,1,'Multas',NOW(),'Validado',%s)
        """, (id_grupo, obs))
        con.commit()
        st.success("Multas validadas.")

    cursor.close()
    con.close()


# ==========================================
# ALERTAS
# ==========================================
def alertas_criticas():

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo
        FROM Grupo
        WHERE Nombre_grupo = 'Fosforitos'
    """)
    g = cursor.fetchone()

    if not g:
        st.info("No existe el grupo.")
        return

    gid = g["Id_Grupo"]

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN Estado_del_prestamo='Mora' THEN 1 ELSE 0 END) AS mora,
            COUNT(*) AS total
        FROM Prestamo
        WHERE Id_Grupo = %s
    """, (gid,))
    prest = cursor.fetchone()

    alerta = []

    if prest["total"] > 0:
        pct = prest["mora"] / prest["total"] * 100
        if pct >= 10:
            alerta.append({"Grupo": "Fosforitos", "Mora (%)": f"{pct:.1f}%"})

    st.subheader("🔴 Mora elevada")
    st.dataframe(alerta, hide_index=True)

    cursor.close()
    con.close()
