from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import io
import streamlit as st
import mysql.connector
from datetime import date
from modulos.conexion import obtener_conexion

# ============================================
#   VALIDACIÓN DE ACCESO PARA PROMOTORA
# ============================================
def interfaz_promotora():

    # Validar sesión
    if "sesion_iniciada" not in st.session_state or not st.session_state["sesion_iniciada"]:
        st.error("Debe iniciar sesión para acceder.")
        st.stop()

    # Validar rol
    rol = st.session_state.get("rol", "")
    id_empleado = st.session_state.get("id_empleado", None)

    if rol != "Promotora" or id_empleado is None:
        st.error("Acceso denegado. Solo la promotora puede ingresar.")
        st.stop()

    # Obtener datos del empleado (promotora)
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM Empleado WHERE Id_Empleado = %s", (id_empleado,))
    promotora = cur.fetchone()
    st.title("👩‍💼 Panel de Promotora — Solidaridad CVX")
    st.caption("Supervisión, validación financiera y reportes del distrito asignado.")
    st.button("Cerrar sesión", on_click=lambda: cerrar_sesion())
    st.markdown("---")
    menu = st.radio(
        "Navegación",
        ["Inicio", "Grupos", "Reportes", "Validaciones", "Alertas"],
        horizontal=True
    )
    st.markdown("---")
    if menu == "Inicio":
        mostrar_dashboard_distrito(promotora)

    elif menu == "Grupos":
        gestionar_grupos(promotora)

    elif menu == "Reportes":
        mostrar_reportes(promotora)

    elif menu == "Validaciones":
        validar_informacion(promotora)

    elif menu == "Alertas":
        mostrar_alertas(promotora)
def mostrar_dashboard_distrito(promotora):
    st.subheader("Dashboard general del distrito")

    st.info("Aquí irá el Dashboard consolidado del distrito.")
def gestionar_grupos(promotora):

    id_promotora = promotora["Id_Empleado"]

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT g.*, d.Nombre AS Distrito
        FROM Grupo g
        JOIN Distrito d ON d.Id_Distrito = g.Id_Distrito
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))

    grupos = cur.fetchall()

    st.subheader("Grupos asignados")
    st.write(f"Total grupos: {len(grupos)}")

    for g in grupos:
        with st.expander(f"📌 {g['Nombre_grupo']}"):
            st.write(f"**Fecha inicio:** {g['Fecha_inicio']}")
            st.write(f"**Tasa:** {g['Tasa_de_interes']}%")
            st.write(f"**Periodicidad:** {g['Periodicidad_reuniones']}")
            st.write(f"**Distrito:** {g['Distrito']}")
def mostrar_reportes(promotora):
    st.subheader("Reportes consolidados")
    st.info("Aquí se generarán reportes PDF y Excel.")
def validar_informacion(promotora):
    st.subheader("Validación de información")
    st.info("Aquí la promotora validará saldos, préstamos, caja y ciclos.")
def mostrar_alertas(promotora):
    st.subheader("Alertas del distrito")
    st.info("Alertas de morosidad, cierres pendientes y anomalías.")
def cerrar_sesion():
    st.session_state.clear()
    st.experimental_rerun()
import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# ================================================
#   PANEL PRINCIPAL DE PROMOTORA
# ================================================
def interfaz_promotora():

    # ---------------------------
    # Validación de sesión
    # ---------------------------
    if "sesion_iniciada" not in st.session_state or not st.session_state["sesion_iniciada"]:
        st.error("Debe iniciar sesión.")
        st.stop()

    rol = st.session_state.get("rol")
    id_empleado = st.session_state.get("id_empleado")

    if rol != "Promotora" or id_empleado is None:
        st.error("Acceso denegado.")
        st.stop()

    # ---------------------------
    # Datos completos de la promotora
    # ---------------------------
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM Empleado WHERE Id_Empleado = %s", (id_empleado,))
    promotora = cur.fetchone()

    # ---------------------------
    # Header del panel
    # ---------------------------
    st.title("👩‍💼 Panel de Promotora — Solidaridad CVX")
    st.caption("Supervisión, validación financiera y reportes del distrito asignado.")

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.experimental_rerun()

    st.markdown("---")

    # ---------------------------
    # Menú horizontal
    # ---------------------------
    menu = st.radio(
        "Navegación",
        ["Inicio", "Grupos", "Reportes", "Validaciones", "Alertas"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ---------------------------
    # Llamado a las secciones
    # ---------------------------
    if menu == "Inicio":
        dashboard_distrito(promotora)

    elif menu == "Grupos":
        gestionar_grupos(promotora)

    elif menu == "Reportes":
        reportes_consolidados(promotora)

    elif menu == "Validaciones":
        modulo_validaciones(promotora)

    elif menu == "Alertas":
        modulo_alertas(promotora)



# =====================================================
#   DASHBOARD GENERAL DEL DISTRITO (BÁSICO)
# =====================================================

def dashboard_distrito(promotora):
    st.subheader("📊 Dashboard general del distrito")
    st.info("Aquí irá el dashboard consolidado con KPIs, gráficas y estado financiero.")
# =====================================================
#   GESTIÓN DE GRUPOS ASIGNADOS A LA PROMOTORA
# =====================================================

def gestionar_grupos(promotora):

    st.subheader("📁 Grupos asignados a su distrito")

    id_promotora = promotora["Id_Empleado"]

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Obtener grupos asignados
    cur.execute("""
        SELECT g.*, d.Nombre AS Distrito
        FROM Grupo g
        JOIN Distrito d ON d.Id_Distrito = g.Id_Distrito
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))

    grupos = cur.fetchall()

    if not grupos:
        st.warning("No tiene grupos asignados.")
        return

    st.success(f"Total grupos asignados: {len(grupos)}")

    # Mostrar cada grupo
    for g in grupos:
        with st.expander(f"📌 {g['Nombre_grupo']}"):
            
            st.write(f"**Distrito:** {g['Distrito']}")
            st.write(f"**Fecha de inicio:** {g['Fecha_inicio']}")
            st.write(f"**Tasa de interés:** {g['Tasa_de_interes']}%")
            st.write(f"**Periodicidad reuniones:** {g['Periodicidad_reuniones']} días")

            # ---------------------------
            # RESUMEN FINANCIERO DEL GRUPO
            # ---------------------------
            st.markdown("### 💰 Resumen financiero")

            # Caja actual del grupo
            cur.execute("""
                SELECT saldo_final 
                FROM caja_reunion 
                WHERE fecha = (SELECT MAX(fecha) FROM caja_reunion)
            """)
            caja = cur.fetchone()

            saldo = caja["saldo_final"] if caja else 0
            st.write(f"**Saldo actual de caja:** ${saldo:,.2f}")

            # Préstamos vigentes
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM Prestamo
                WHERE Id_Grupo = %s AND Estado_del_prestamo = 'Activo'
            """, (g["Id_Grupo"],))
            prestamos = cur.fetchone()["total"]

            st.write(f"**Préstamos activos:** {prestamos}")

            # Multas aplicadas
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM Multa
                WHERE Id_Grupo = %s
            """, (g["Id_Grupo"],))
            multas = cur.fetchone()["total"]

            st.write(f"**Multas aplicadas:** {multas}")

            # Botón para expandir detalles
            st.markdown("### 📂 Acciones")

            cols = st.columns(4)

            with cols[0]:
                st.button(f"Socias — {g['Nombre_grupo']}", key=f"socia_{g['Id_Grupo']}")

            with cols[1]:
                st.button(f"Caja — {g['Nombre_grupo']}", key=f"caja_{g['Id_Grupo']}")

            with cols[2]:
                st.button(f"Ahorros — {g['Nombre_grupo']}", key=f"ahorros_{g['Id_Grupo']}")

            with cols[3]:
                st.button(f"Préstamos — {g['Nombre_grupo']}", key=f"prestamos_{g['Id_Grupo']}")
# =====================================================
#   REPORTES CONSOLIDADOS
# =====================================================

def reportes_consolidados(promotora):
    st.subheader("📄 Reportes consolidados del distrito")
    st.info("Aquí podrá generar reportes PDF y Excel por grupo o por distrito.")



# =====================================================
#   MÓDULO DE VALIDACIONES
# =====================================================

def modulo_validaciones(promotora):
    st.subheader("✔ Validación de información financiera")
    st.info("Validación de caja, préstamos, ciclos, ahorros y multas.")



# =====================================================
#   ALERTAS DEL DISTRITO
# =====================================================

def modulo_alertas(promotora):
    st.subheader("🔔 Alertas automáticas del distrito")
    st.info("Alertas de morosidad, cierres pendientes, anomalías financieras.")
import plotly.express as px
import pandas as pd

# =====================================================
#   DASHBOARD COMPLETO DEL DISTRITO
# =====================================================

def dashboard_distrito(promotora):

    st.subheader("📊 Dashboard del distrito asignado")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    distrito_id = promotora["Distrito"]
    id_promotora = promotora["Id_Empleado"]

    # ----------------------------------------------------
    # 1) TOTAL DE GRUPOS
    # ----------------------------------------------------
    cur.execute("""SELECT COUNT(*) AS total 
                   FROM Grupo 
                   WHERE Id_Promotora = %s""",
                   (id_promotora,))
    total_grupos = cur.fetchone()["total"]

    # ----------------------------------------------------
    # 2) TOTAL DE SOCIAS
    # ----------------------------------------------------
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM Socia s
        JOIN Grupo g ON g.Id_Grupo = s.Id_Grupo
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    total_socias = cur.fetchone()["total"]

    # ----------------------------------------------------
    # 3) AHORRO TOTAL DEL DISTRITO
    # ----------------------------------------------------
    cur.execute("""
        SELECT SUM(Monto_del_aporte) AS total
        FROM Ahorro a
        JOIN Grupo g ON g.Id_Grupo = a.Id_Grupo
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    ahorro_total = cur.fetchone()["total"] or 0

    # ----------------------------------------------------
    # 4) PRÉSTAMOS ACTIVOS
    # ----------------------------------------------------
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM Prestamo p
        JOIN Grupo g ON g.Id_Grupo = p.Id_Grupo
        WHERE g.Id_Promotora = %s
          AND p.Estado_del_prestamo = 'Activo'
    """, (id_promotora,))
    prestamos_activos = cur.fetchone()["total"]

    # ----------------------------------------------------
    # MOSTRAR TARJETAS KPI
    # ----------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Grupos activos", total_grupos)
    col2.metric("Total de socias", total_socias)
    col3.metric("Ahorro total ($)", f"{ahorro_total:,.2f}")
    col4.metric("Préstamos activos", prestamos_activos)

    st.markdown("---")

    # ----------------------------------------------------
    # 5) COMPORTAMIENTO DE CAJA (últimas 6 reuniones)
    # ----------------------------------------------------
    cur.execute("""
        SELECT fecha, saldo_final
        FROM caja_reunion
        ORDER BY fecha DESC
        LIMIT 6
    """)
    caja = cur.fetchall()

    if caja:
        df_caja = pd.DataFrame(caja).sort_values("fecha")
        fig = px.line(df_caja, x="fecha", y="saldo_final",
                      title="📈 Evolución reciente de la caja",
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos de caja para mostrar.")

    st.markdown("---")

    # ----------------------------------------------------
    # 6) DISTRIBUCIÓN DE PRÉSTAMOS
    # ----------------------------------------------------
    cur.execute("""
        SELECT Estado_del_prestamo, COUNT(*) AS total
        FROM Prestamo p
        JOIN Grupo g ON g.Id_Grupo = p.Id_Grupo
        WHERE g.Id_Promotora = %s
        GROUP BY Estado_del_prestamo
    """, (id_promotora,))
    prestamos_data = cur.fetchall()

    if prestamos_data:
        df_p = pd.DataFrame(prestamos_data)
        fig = px.pie(df_p, values="total", names="Estado_del_prestamo",
                     title="🧮 Distribución de préstamos")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de préstamos para mostrar.")

    st.markdown("---")

    # ----------------------------------------------------
    # 7) TOP 5 SOCIAS CON MÁS AHORRO
    # ----------------------------------------------------
    cur.execute("""
        SELECT s.Nombre, SUM(a.Monto_del_aporte) AS total
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        JOIN Grupo g ON g.Id_Grupo = a.Id_Grupo
        WHERE g.Id_Promotora = %s
        GROUP BY s.Id_Socia
        ORDER BY total DESC
        LIMIT 5
    """, (id_promotora,))
    top_socias = cur.fetchall()

    if top_socias:
        df_top = pd.DataFrame(top_socias)
        fig = px.bar(df_top, x="Nombre", y="total",
                     title="💎 Top 5 socias con mayor ahorro")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay movimientos de ahorro para mostrar.")
# =====================================================
#   MÓDULO COMPLETO DE VALIDACIONES PARA PROMOTORA
# =====================================================

def modulo_validaciones(promotora):

    st.subheader("✔ Validación financiera y operativa del distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Obtener grupos asignados a la promotora (Empleado)
    cur.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (promotora["Id_Empleado"],))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No tiene grupos asignados.")
        return

    grupos_dict = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    # Selector de grupo para validar
    grupo_sel = st.selectbox("Seleccione un grupo:", grupos_dict.keys())
    id_grupo = grupos_dict[grupo_sel]

    st.markdown("---")

    # Selector tipo de validación
    tipo = st.radio(
        "Seleccione el tipo de validación:",
        ["Caja", "Préstamos", "Multas", "Ahorros", "Ciclo"],
        horizontal=True
    )

    if tipo == "Caja":
        validar_caja(id_grupo, promotora["Id_Empleado"])

    elif tipo == "Préstamos":
        validar_prestamos(id_grupo, promotora["Id_Empleado"])

    elif tipo == "Multas":
        validar_multas(id_grupo, promotora["Id_Empleado"])

    elif tipo == "Ahorros":
        validar_ahorros(id_grupo, promotora["Id_Empleado"])

    elif tipo == "Ciclo":
        validar_ciclo(id_grupo, promotora["Id_Empleado"])

    cur.close()
    con.close()



# =====================================================
#   VALIDAR CAJA
# =====================================================

def validar_caja(id_grupo, id_promotora):

    st.subheader("💰 Validación de Caja por reunión")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
        ORDER BY fecha DESC
    """, (id_grupo,))
    datos = cur.fetchall()

    if not datos:
        st.info("No existen registros de caja para este grupo.")
        return

    st.dataframe(datos, hide_index=True)

    observ = st.text_area("Observaciones", "")

    if st.button("Validar Caja", type="primary"):
        cur.execute("""
            INSERT INTO Validaciones (Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES (%s, %s, 'Caja', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Caja validada exitosamente.")

    cur.close()
    con.close()



# =====================================================
#   VALIDAR PRÉSTAMOS
# =====================================================

def validar_prestamos(id_grupo, id_promotora):

    st.subheader("📘 Validación de Préstamos")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT s.Nombre AS Socia, p.Monto, p.Interes_porcentaje, p.Cuota,
               p.Estado_del_prestamo, p.Fecha_inicio, p.Fecha_limite
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
        ORDER BY p.Fecha_inicio DESC
    """, (id_grupo,))
    datos = cur.fetchall()

    st.dataframe(datos, hide_index=True)

    observ = st.text_area("Observaciones del préstamo", "")

    if st.button("Validar Préstamos", type="primary"):
        cur.execute("""
            INSERT INTO Validaciones (Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES (%s, %s, 'Prestamos', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Préstamos validados correctamente.")

    cur.close()
    con.close()



# =====================================================
#   VALIDAR MULTAS
# =====================================================

def validar_multas(id_grupo, id_promotora):

    st.subheader("⚠ Validación de Multas")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT s.Nombre AS Socia, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
        ORDER BY m.Fecha_aplicacion DESC
    """, (id_grupo,))
    datos = cur.fetchall()

    st.dataframe(datos, hide_index=True)

    observ = st.text_area("Observaciones de multas", "")

    if st.button("Validar Multas", type="primary"):
        cur.execute("""
            INSERT INTO Validaciones (Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES (%s, %s, 'Multas', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Multas validadas.")

    cur.close()
    con.close()



# =====================================================
#   VALIDAR AHORROS
# =====================================================

def validar_ahorros(id_grupo, id_promotora):

    st.subheader("🏦 Validación de Ahorros")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT s.Nombre AS Socia, SUM(a.Monto_del_aporte) AS Total_Ahorro
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        GROUP BY s.Id_Socia
        ORDER BY Total_Ahorro DESC
    """, (id_grupo,))
    datos = cur.fetchall()

    st.dataframe(datos, hide_index=True)

    observ = st.text_area("Observaciones del ahorro", "")

    if st.button("Validar Ahorros", type="primary"):
        cur.execute("""
            INSERT INTO Validaciones (Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES (%s, %s, 'Ahorros', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Ahorros validados.")

    cur.close()
    con.close()



# =====================================================
#   VALIDAR CICLO
# =====================================================

def validar_ciclo(id_grupo, id_promotora):

    st.subheader("🔵 Validación del Ciclo")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT Fecha_inicio, Fecha_fin, Estado
        FROM ciclo
        WHERE Id_Grupo = %s
        ORDER BY Fecha_inicio DESC
        LIMIT 1
    """, (id_grupo,))
    ciclo = cur.fetchone()

    if ciclo:
        st.write(ciclo)
    else:
        st.info("Este grupo no tiene ciclo registrado.")

    observ = st.text_area("Observaciones del ciclo", "")

    if st.button("Validar Ciclo", type="primary"):
        cur.execute("""
            INSERT INTO Validaciones (Id_Grupo, Id_Promotora, Tipo, Fecha_validacion, Estado, Observaciones)
            VALUES (%s, %s, 'Ciclo', NOW(), 'Validado', %s)
        """, (id_grupo, id_promotora, observ))
        con.commit()
        st.success("Ciclo validado correctamente.")

    cur.close()
    con.close()
# =====================================================
#   GESTIÓN COMPLETA DE GRUPOS PARA PROMOTORA
# =====================================================

def gestionar_grupos(promotora):

    # -------------------------------------------------
    # Si el usuario ya seleccionó un grupo → mostrar detalles
    # -------------------------------------------------
    if "grupo_seleccionado" in st.session_state:
        mostrar_detalle_grupo(st.session_state["grupo_seleccionado"])
        return

    st.subheader("📁 Grupos asignados a la Promotora")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ID del empleado que es promotora
    id_promotora = promotora["Id_Empleado"]

    # -------------------------------------------------
    # OBTENER TODOS LOS GRUPOS ASIGNADOS A ESTA PROMOTORA
    # -------------------------------------------------
    cur.execute("""
        SELECT g.*, d.Nombre AS Distrito
        FROM Grupo g
        JOIN Distrito d ON d.Id_Distrito = g.Id_Distrito
        WHERE g.Id_Promotora = %s
        ORDER BY g.Nombre_grupo ASC
    """, (id_promotora,))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No tiene grupos asignados actualmente.")
        return

    # -------------------------------------------------
    # RESUMEN GENERAL
    # -------------------------------------------------
    st.success(f"Total grupos asignados: {len(grupos)}")
    st.markdown("---")

    # -------------------------------------------------
    # MOSTRAR CADA GRUPO EN EXPANDER
    # -------------------------------------------------
    for g in grupos:
        with st.expander(f"📌 {g['Nombre_grupo']}"):

            # INFORMACIÓN GENERAL
            st.write(f"**Distrito:** {g['Distrito']}")
            st.write(f"**Fecha de inicio:** {g['Fecha_inicio']}")
            st.write(f"**Tasa de interés:** {g['Tasa_de_interes']}%")
            st.write(f"**Periodicidad:** {g['Periodicidad_reuniones']} días")

            # -------------------------------------------------
            # RESUMEN FINANCIERO (Caja, Préstamos, Multas)
            # -------------------------------------------------

            st.markdown("### 💰 Resumen financiero")

            # Caja (último saldo)
            cur.execute("""
                SELECT saldo_final 
                FROM caja_reunion
                WHERE Id_Grupo = %s
                ORDER BY fecha DESC LIMIT 1
            """, (g["Id_Grupo"],))
            caja = cur.fetchone()
            saldo = caja["saldo_final"] if caja else 0
            st.write(f"**Saldo de caja actual:** ${saldo:,.2f}")

            # Préstamos activos
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM Prestamo
                WHERE Id_Grupo = %s AND Estado_del_prestamo = 'Activo'
            """, (g["Id_Grupo"],))
            prestamos = cur.fetchone()["total"]
            st.write(f"**Préstamos activos:** {prestamos}")

            # Multas aplicadas
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM Multa
                WHERE Id_Grupo = %s
            """, (g["Id_Grupo"],))
            multas = cur.fetchone()["total"]
            st.write(f"**Multas aplicadas:** {multas}")

            # -------------------------------------------------
            # BOTÓN PARA ABRIR EL DETALLE DEL GRUPO
            # -------------------------------------------------

            st.markdown("### 📂 Acciones disponibles")

            if st.button(f"Ver detalles de {g['Nombre_grupo']}", key=f"ver_det_{g['Id_Grupo']}"):
                st.session_state["grupo_seleccionado"] = g["Id_Grupo"]
                st.experimental_rerun()

    cur.close()
    con.close()
# =====================================================
#   REPORTES COMPLETOS PARA PROMOTORA
# =====================================================

def reportes_consolidados(promotora):

    st.subheader("📄 Generación de Reportes")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Obtener grupos de la promotora
    cur.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
        ORDER BY Nombre_grupo ASC
    """, (promotora["Id_Empleado"],))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No tiene grupos asignados.")
        return

    grupos_dict = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    tipo_reporte = st.radio(
        "Seleccione el tipo de reporte:",
        ["Reporte del Distrito", "Reporte por Grupo"],
        horizontal=True
    )

    if tipo_reporte == "Reporte del Distrito":
        reporte_distrito(promotora)

    else:
        grupo_sel = st.selectbox("Seleccione el grupo:", grupos_dict.keys())
        id_grupo = grupos_dict[grupo_sel]
        reporte_grupo(id_grupo, grupo_sel)
# =====================================================
#   REPORTE CONSOLIDADO DEL DISTRITO
# =====================================================

def reporte_distrito(promotora):

    st.markdown("### 📊 Reporte consolidado del Distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    id_promotora = promotora["Id_Empleado"]

    # 1) Socias totales
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM Socia s
        JOIN Grupo g ON g.Id_Grupo = s.Id_Grupo
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    total_socias = cur.fetchone()["total"]

    # 2) Ahorro total
    cur.execute("""
        SELECT SUM(a.Monto_del_aporte) AS total
        FROM Ahorro a
        JOIN Grupo g ON g.Id_Grupo = a.Id_Grupo
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    ahorro_total = cur.fetchone()["total"] or 0

    # 3) Préstamos activos
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM Prestamo p
        JOIN Grupo g ON g.Id_Grupo = p.Id_Grupo
        WHERE g.Id_Promotora = %s AND p.Estado_del_prestamo='Activo'
    """, (id_promotora,))
    prestamos_activos = cur.fetchone()["total"]

    st.write(f"**Total de socias:** {total_socias}")
    st.write(f"**Ahorro total:** ${ahorro_total:,.2f}")
    st.write(f"**Préstamos activos:** {prestamos_activos}")

    st.markdown("---")

    # -------------------------------
    #  BOTONES DE EXPORTACIÓN
    # -------------------------------

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Exportar PDF del Distrito"):
            pdf = generar_pdf_distrito(promotora, total_socias, ahorro_total, prestamos_activos)
            st.download_button(
                label="Descargar PDF",
                data=pdf,
                file_name="Reporte_Distrito.pdf",
                mime="application/pdf"
            )

    with col2:
        if st.button("📊 Exportar Excel del Distrito"):
            excel = generar_excel_distrito(promotora["Id_Empleado"])
            st.download_button(
                label="Descargar Excel",
                data=excel,
                file_name="Reporte_Distrito.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
def generar_pdf_distrito(promotora, total_socias, ahorro_total, prestamos_activos):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elementos = []

    titulo = Paragraph(f"<b>Reporte Consolidado del Distrito</b>", styles["Title"])
    elementos.append(titulo)

    elementos.append(Paragraph(f"Promotora: {promotora['Nombre_empleado']}", styles["Normal"]))
    elementos.append(Paragraph(f"Correo: {promotora['Correo']}", styles["Normal"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    data = [
        ["Indicador", "Valor"],
        ["Total Socias", total_socias],
        ["Ahorro Total ($)", f"{ahorro_total:,.2f}"],
        ["Préstamos Activos", prestamos_activos]
    ]

    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))

    elementos.append(tabla)

    doc.build(elementos)
    buffer.seek(0)
    return buffer
def generar_excel_distrito(id_promotora):

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"

    # Datos de socias
    cur.execute("""
        SELECT s.Nombre, s.Telefono, s.Fecha_ingreso, g.Nombre_grupo
        FROM Socia s
        JOIN Grupo g ON g.Id_Grupo = s.Id_Grupo
        WHERE g.Id_Promotora = %s
    """, (id_promotora,))
    socias = cur.fetchall()

    ws.append(["Nombre", "Telefono", "Fecha de ingreso", "Grupo"])
    for s in socias:
        ws.append([s["Nombre"], s["Telefono"], s["Fecha_ingreso"], s["Nombre_grupo"]])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
# =====================================================
#   REPORTE COMPLETO POR GRUPO
# =====================================================

def reporte_grupo(id_grupo, nombre_grupo):

    st.markdown(f"### 📘 Reporte completo del grupo: {nombre_grupo}")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # --------------------------------------------------
    # 1) Caja
    # --------------------------------------------------
    cur.execute("""
        SELECT fecha, saldo_inicial, ingresos, egresos, saldo_final
        FROM caja_reunion
        WHERE Id_Grupo = %s
        ORDER BY fecha ASC
    """, (id_grupo,))
    caja = cur.fetchall()

    df_caja = pd.DataFrame(caja)

    # --------------------------------------------------
    # 2) Ahorros
    # --------------------------------------------------
    cur.execute("""
        SELECT s.Nombre AS Socia, a.Monto_del_aporte, a.Fecha
        FROM Ahorro a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY a.Fecha DESC
    """, (id_grupo,))
    ahorros = cur.fetchall()

    df_ahorros = pd.DataFrame(ahorros)

    # --------------------------------------------------
    # 3) Préstamos
    # --------------------------------------------------
    cur.execute("""
        SELECT s.Nombre AS Socia, p.Monto, p.Interes_porcentaje,
               p.Cuota, p.Estado_del_prestamo,
               p.Fecha_inicio, p.Fecha_limite
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        WHERE p.Id_Grupo = %s
        ORDER BY p.Fecha_inicio DESC
    """, (id_grupo,))
    prest = cur.fetchall()

    df_prest = pd.DataFrame(prest)

    # --------------------------------------------------
    # 4) Multas
    # --------------------------------------------------
    cur.execute("""
        SELECT s.Nombre AS Socia, t.Tipo_de_multa, m.Monto, m.Fecha_aplicacion
        FROM Multa m
        JOIN Socia s ON s.Id_Socia = m.Id_Socia
        JOIN Tipo_de_multa t ON t.Id_Tipo_multa = m.Id_Tipo_multa
        WHERE m.Id_Grupo = %s
        ORDER BY m.Fecha_aplicacion DESC
    """, (id_grupo,))
    multas = cur.fetchall()

    df_multas = pd.DataFrame(multas)

    # --------------------------------------------------
    # 5) Asistencias
    # --------------------------------------------------
    cur.execute("""
        SELECT a.Fecha_asistencia, s.Nombre AS Socia, a.Estado
        FROM Asistencia a
        JOIN Socia s ON s.Id_Socia = a.Id_Socia
        WHERE a.Id_Grupo = %s
        ORDER BY a.Fecha_asistencia DESC
    """, (id_grupo,))
    asist = cur.fetchall()

    df_asist = pd.DataFrame(asist)

    st.success("Datos recopilados correctamente.")

    st.markdown("---")

    # --------------------------------------------------
    #  BOTONES DE EXPORTACIÓN PDF / EXCEL
    # --------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Exportar PDF del Grupo"):
            pdf = generar_pdf_grupo(nombre_grupo, df_caja, df_ahorros, df_prest, df_multas, df_asist)
            st.download_button(
                label="Descargar PDF",
                data=pdf,
                file_name=f"Reporte_{nombre_grupo}.pdf",
                mime="application/pdf"
            )

    with col2:
        if st.button("📊 Exportar Excel del Grupo"):
            excel = generar_excel_grupo(nombre_grupo, df_caja, df_ahorros, df_prest, df_multas, df_asist)
            st.download_button(
                label="Descargar Excel",
                data=excel,
                file_name=f"Reporte_{nombre_grupo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
def generar_pdf_grupo(nombre_grupo, df_caja, df_ahorros, df_prest, df_multas, df_asist):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    # Título
    elementos.append(Paragraph(f"<b>Reporte del Grupo: {nombre_grupo}</b>", styles["Title"]))
    elementos.append(Paragraph("<br/>", styles["Normal"]))

    # Función utilidad para convertir DF a tabla
    def tabla_desde_df(df, titulo):
        if df.empty:
            return Paragraph(f"<b>{titulo}:</b> No hay datos.<br/><br/>", styles["Normal"])

        elementos.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
        data = [df.columns.tolist()] + df.values.tolist()
        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
        ]))
        return tabla

    # Agregar tablas
    for titulo, df in [
        ("Caja del Grupo", df_caja),
        ("Ahorros", df_ahorros),
        ("Préstamos", df_prest),
        ("Multas", df_multas),
        ("Asistencias", df_asist)
    ]:
        elementos.append(tabla_desde_df(df, titulo))
        elementos.append(Paragraph("<br/>", styles["Normal"]))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
def generar_excel_grupo(nombre_grupo, df_caja, df_ahorros, df_prest, df_multas, df_asist):

    wb = Workbook()

    # Crear hoja por cada módulo
    hojas = {
        "Caja": df_caja,
        "Ahorros": df_ahorros,
        "Prestamos": df_prest,
        "Multas": df_multas,
        "Asistencia": df_asist
    }

    for nombre, df in hojas.items():
        ws = wb.create_sheet(nombre)
        if df.empty:
            ws.append(["No hay datos"])
        else:
            ws.append(df.columns.tolist())
            for row in df.values.tolist():
                ws.append(row)

    # Eliminar hoja vacía inicial
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
# =====================================================
#   MÓDULO DE ALERTAS AUTOMÁTICAS
# =====================================================

def modulo_alertas(promotora):

    st.subheader("🔔 Alertas del Distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    id_promotora = promotora["Id_Empleado"]

    st.info("Las siguientes alertas se generan automáticamente con base en los datos reales del distrito.")

    st.markdown("---")

    # =====================================================
    #   ALERTA 1 — MOROSIDAD ALTA
    # =====================================================
    st.markdown("### 🔴 Morosidad alta")

    cur.execute("""
        SELECT g.Nombre_grupo, s.Nombre AS Socia, p.Monto, 
               p.Fecha_limite, p.Estado_del_prestamo
        FROM Prestamo p
        JOIN Socia s ON s.Id_Socia = p.Id_Socia
        JOIN Grupo g ON g.Id_Grupo = s.Id_Grupo
        WHERE g.Id_Promotora = %s
          AND p.Estado_del_prestamo = 'En mora'
        ORDER BY p.Fecha_limite ASC
    """, (id_promotora,))
    moras = cur.fetchall()

    if moras:
        st.error("Existen préstamos en mora.")
        st.dataframe(moras, hide_index=True)
    else:
        st.success("No hay préstamos en mora.")

    st.markdown("---")

    # =====================================================
    #   ALERTA 2 — CAJA ANÓMALA
    # =====================================================
    st.markdown("### 🟠 Caja inconsistente")

    cur.execute("""
        SELECT g.Nombre_grupo,
               c.fecha,
               c.saldo_inicial,
               c.saldo_final,
               c.ingresos,
               c.egresos
        FROM caja_reunion c
        JOIN Grupo g ON g.Id_Grupo = c.Id_Grupo
        WHERE g.Id_Promotora = %s
        ORDER BY c.fecha DESC
    """, (id_promotora,))
    cajas = cur.fetchall()

    alertas_caja = []
    for c in cajas:
        # Caja negativa
        if c["saldo_final"] < 0:
            alertas_caja.append(c)
        # Saltos bruscos (más del 40%)
        if c["saldo_inicial"] > 0:
            variacion = abs(c["saldo_final"] - c["saldo_inicial"]) / c["saldo_inicial"]
            if variacion > 0.40:
                alertas_caja.append(c)

    if alertas_caja:
        st.warning("Se encontraron anomalías en la caja.")
        st.dataframe(alertas_caja, hide_index=True)
    else:
        st.success("No hay alertas de caja.")

    st.markdown("---")

    # =====================================================
    #   ALERTA 3 — AHORROS BAJOS
    # =====================================================
    st.markdown("### 🟡 Ahorros insuficientes o nulos")

    cur.execute("""
        SELECT g.Nombre_grupo, s.Nombre AS Socia
        FROM Socia s
        JOIN Grupo g ON g.Id_Grupo = s.Id_Grupo
        LEFT JOIN Ahorro a ON a.Id_Socia = s.Id_Socia
        WHERE g.Id_Promotora = %s
        GROUP BY s.Id_Socia
        HAVING SUM(a.Monto_del_aporte) IS NULL
           OR SUM(a.Monto_del_aporte) = 0
    """, (id_promotora,))
    ahorros_bajos = cur.fetchall()

    if ahorros_bajos:
        st.warning("Hay socias sin ahorros registrados.")
        st.dataframe(ahorros_bajos, hide_index=True)
    else:
        st.success("Todas las socias tienen algún ahorro registrado.")

    st.markdown("---")

    # =====================================================
    #   ALERTA 4 — REUNIONES NO REGISTRADAS
    # =====================================================
    st.markdown("### 🔵 Grupos sin reuniones recientes")

    cur.execute("""
        SELECT g.Nombre_grupo, MAX(r.Fecha_reunion) AS ultima
        FROM Grupo g
        LEFT JOIN Reunion r ON r.Id_Grupo = g.Id_Grupo
        WHERE g.Id_Promotora = %s
        GROUP BY g.Id_Grupo
    """, (id_promotora,))
    reuniones = cur.fetchall()

    sin_reunion = []
    for r in reuniones:
        if not r["ultima"]:
            sin_reunion.append({"Nombre_grupo": r["Nombre_grupo"], "ultima": "Sin registros"})
        else:
            dias = (date.today() - r["ultima"]).days
            if dias > 30:
                sin_reunion.append(r)

    if sin_reunion:
        st.warning("Hay grupos sin reuniones recientes.")
        st.dataframe(sin_reunion, hide_index=True)
    else:
        st.success("Todos los grupos llevan reuniones al día.")

    st.markdown("---")

    # =====================================================
    #   ALERTA 5 — CICLOS PRÓXIMOS A CERRAR
    # =====================================================
    st.markdown("### 🟣 Ciclos próximos a cerrar")

    cur.execute("""
        SELECT g.Nombre_grupo, c.Fecha_fin, c.Estado
        FROM ciclo c
        JOIN Grupo g ON g.Id_Grupo = c.Id_Grupo
        WHERE g.Id_Promotora = %s
        ORDER BY c.Fecha_fin ASC
    """, (id_promotora,))
    ciclos = cur.fetchall()

    proximos = []
    for c in ciclos:
        if c["Fecha_fin"]:
            dias = (c["Fecha_fin"] - date.today()).days
            if 0 <= dias <= 15:
                proximos.append(c)

    if proximos:
        st.warning("Ciclos próximos a cerrar.")
        st.dataframe(proximos, hide_index=True)
    else:
        st.success("No hay ciclos por cerrar en el corto plazo.")
# =====================================================
#   SECCIÓN 7 — SEGURIDAD Y MANEJO DE ERRORES
# =====================================================

import pandas as pd
import streamlit as st
import traceback


# =====================================================
#   7.1 — EJECUTOR SEGURO DE CONSULTAS SQL
# =====================================================

def safe_query(query, params=None, fetch="all", error_msg="Error al obtener datos"):
    """
    Ejecuta consultas SQL con manejo de excepciones y conexión segura.
    fetch = "all" → fetchall()
    fetch = "one" → fetchone()
    """

    try:
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)

        cur.execute(query, params or ())

        if fetch == "one":
            result = cur.fetchone()
        else:
            result = cur.fetchall()

        cur.close()
        con.close()
        return result

    except Exception as e:
        st.error(f"❌ {error_msg}")
        st.caption(f"Detalles del error: {str(e)}")
        st.stop()


# =====================================================
#   7.2 — DATAFRAME SEGURO
#   (prevenir errores cuando la BD devuelve vacío)
# =====================================================

def safe_df(data, empty_msg="No hay datos disponibles."):
    """
    Convierte un resultado SQL en DataFrame seguro.
    Si está vacío, muestra mensaje sin romper el flujo.
    """
    if not data:
        st.info(empty_msg)
        return pd.DataFrame()  # DF vacío pero válido

    return pd.DataFrame(data)


# =====================================================
#   7.3 — GENERADOR PDF SEGURO
# =====================================================

def safe_pdf(builder_function, *args, **kwargs):
    """
    Envuelve funciones que generan PDFs para evitar errores de datos vacíos.
    """
    try:
        pdf = builder_function(*args, **kwargs)
        return pdf
    except Exception as e:
        st.error("❌ Error al generar PDF.")
        st.caption(str(e))
        st.code(traceback.format_exc())
        return None


# =====================================================
#   7.4 — GENERADOR EXCEL SEGURO
# =====================================================

def safe_excel(builder_function, *args, **kwargs):
    """
    Envuelve funciones que generan Excel para evitar errores silenciosos.
    """
    try:
        excel = builder_function(*args, **kwargs)
        return excel
    except Exception as e:
        st.error("❌ Error al generar archivo Excel.")
        st.caption(str(e))
        st.code(traceback.format_exc())
        return None


# =====================================================
#   7.5 — VALIDAR ROL Y SESIÓN
# =====================================================

def validar_acceso_promotora():
    """
    Evita accesos no autorizados o sesiones caducadas.
    """
    if "sesion_iniciada" not in st.session_state or not st.session_state["sesion_iniciada"]:
        st.error("Debe iniciar sesión.")
        st.stop()

    if st.session_state.get("rol") != "Promotora":
        st.error("Acceso denegado.")
        st.stop()

    if not st.session_state.get("id_empleado"):
        st.error("No se encontró el ID del empleado.")
        st.stop()


# =====================================================
#   7.6 — LIMPIEZA DEL ESTADO DE NAVEGACIÓN
# =====================================================

def limpiar_estado_grupo():
    """Limpia la selección de grupo al cambiar de sección."""
    if "grupo_seleccionado" in st.session_state:
        del st.session_state["grupo_seleccionado"]


# =====================================================
#   7.7 — PROTECCIÓN DEL MÓDULO DE REPORTES
# =====================================================

def validar_dataset_para_reporte(df, tipo="Reporte"):
    """Evita que se genere PDF/Excel cuando no hay datos."""
    if df.empty:
        st.warning(f"⚠ No hay datos suficientes para generar el {tipo}.")
        return False
    return True


# =====================================================
#   7.8 — CONTROL DE ERRORES PARA TABS DEL GRUPO
# =====================================================

def safe_show_tab(func, *args):
    """
    Envuelve cada tab (Caja, Ahorros, Préstamos...) para evitar que un error interno
    colapse toda la página.
    """
    try:
        func(*args)
    except Exception as e:
        st.error("❌ Ocurrió un error al cargar esta sección.")
        st.caption(str(e))
        st.code(traceback.format_exc())


# =====================================================
#   7.9 — FUNCIONES SEGURO PARA SECCIONES DEL GRUPO
# =====================================================

def safe_section(query, params, empty_msg):
    """Consulta y muestra tabla segura en una sola línea."""
    data = safe_query(query, params)
    df = safe_df(data, empty_msg)
    if not df.empty:
        st.dataframe(df, hide_index=True)
    return df  # Para reportes si se necesita
