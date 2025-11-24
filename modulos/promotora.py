import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion


# ================================================================
#   PANEL PRINCIPAL — PROMOTORA
# ================================================================
def interfaz_promotora():

    rol = st.session_state.get("rol", "")
    id_empleado = st.session_state.get("id_empleado", None)

    if rol != "Promotora" or id_empleado is None:
        st.title("Acceso denegado")
        st.warning("Solo una promotora autorizada puede acceder aquí.")
        return

    st.title("👩‍🦳 Panel de Promotora — Solidaridad CVX")
    st.caption("Supervisión, validación financiera y reportes del distrito asignado.")

    # Botón cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ------------------------------------------------------------
    # CONSULTAR DATOS BÁSICOS DE LA PROMOTORA
    # ------------------------------------------------------------
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT Id_Empleado, Nombres, Apellidos, Distrito
        FROM Empleado
        WHERE Id_Empleado = %s AND Id_Rol = 2
    """, (id_empleado,))
    promotora = cur.fetchone()

    if not promotora:
        st.error("❌ No se pudo cargar la información de la promotora.")
        return

    distrito_promotora = promotora["Distrito"]

    # ------------------------------------------------------------
    # MENÚ DE NAVEGACIÓN
    # ------------------------------------------------------------
    st.markdown("### Navegación")
    menu = st.radio(
        "", 
        ["Inicio", "Grupos", "Reportes", "Validaciones"],
        horizontal=True
    )

    if menu == "Inicio":
        mostrar_dashboard_inicio(distrito_promotora)

    elif menu == "Grupos":
        gestionar_grupos(distrito_promotora)

    elif menu == "Reportes":
        reportes_consolidados(distrito_promotora)

    elif menu == "Validaciones":
        validaciones_financieras(distrito_promotora)



# ================================================================
#   SECCIÓN 1 — DASHBOARD INICIAL
# ================================================================
def mostrar_dashboard_inicio(distrito):

    st.subheader("📊 Dashboard general del distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Total de grupos
    cur.execute("SELECT COUNT(*) AS total FROM Grupo WHERE Id_Distrito = %s", (distrito,))
    total_grupos = cur.fetchone()["total"]

    # Total de socias
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM Socia S
        JOIN Grupo G ON G.Id_Grupo = S.Id_Grupo
        WHERE G.Id_Distrito = %s
    """, (distrito,))
    total_socias = cur.fetchone()["total"]

    st.info(f"👥 **Grupos asignados:** {total_grupos}")
    st.info(f"👩‍🦰 **Socias totales en el distrito:** {total_socias}")

    st.success("Este dashboard puede ampliarse más adelante con métricas adicionales.")
# ================================================================
#   SECCIÓN 2 — GESTIÓN DE GRUPOS (solo lectura)
# ================================================================
def gestionar_grupos(distrito):

    st.subheader("👥 Grupos del distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # LISTAR GRUPOS DEL DISTRITO
    # ------------------------------------------------------------
    cur.execute("""
        SELECT Id_Grupo, Nombre_grupo, Fecha_inicio, Id_Promotora
        FROM Grupo
        WHERE Id_Distrito = %s
        ORDER BY Nombre_grupo ASC
    """, (distrito,))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No hay grupos registrados en este distrito.")
        return

    nombres = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    seleccionado = st.selectbox(
        "Selecciona un grupo",
        list(nombres.keys())
    )

    id_grupo = nombres[seleccionado]

    st.markdown("---")
    st.markdown(f"### 📌 Información general del grupo: **{seleccionado}**")

    # Obtener detalles del grupo
    cur.execute("""
        SELECT Nombre_grupo, Fecha_inicio, Tasa_de_interes, Periodicidad_reuniones
        FROM Grupo
        WHERE Id_Grupo = %s
    """, (id_grupo,))
    g = cur.fetchone()

    if g:
        st.write(f"📅 **Fecha inicio:** {g['Fecha_inicio']}")
        st.write(f"💰 **Tasa de interés:** {g['Tasa_de_interes']}%")
        st.write(f"🗓️ **Periodicidad:** {g['Periodicidad_reuniones']} días")

    st.markdown("---")

    # ------------------------------------------------------------
    # RESUMEN DE SOCIAS
    # ------------------------------------------------------------
    st.markdown("### 👩‍🦰 Miembros del grupo")

    cur.execute("""
        SELECT Nombre, DUI, Telefono, Sexo
        FROM Socia
        WHERE Id_Grupo = %s
        ORDER BY Nombre ASC
    """, (id_grupo,))

    socias = cur.fetchall()

    if socias:
        df_socias = pd.DataFrame(socias)
        st.dataframe(df_socias, use_container_width=True)
    else:
        st.info("Este grupo aún no tiene socias registradas.")

    st.markdown("---")

    # ------------------------------------------------------------
    # RESUMEN SIMPLE DE CAJA
    # ------------------------------------------------------------
    st.markdown("### 🧾 Resumen financiero del grupo")

    # Total ahorros
    cur.execute("""
        SELECT SUM(Monto_del_aporte) AS total
        FROM Ahorro WHERE Id_Grupo = %s
    """, (id_grupo,))
    total_ahorros = cur.fetchone()["total"] or 0

    # Total préstamos activos
    cur.execute("""
        SELECT SUM(Saldo_pendiente) AS total
        FROM Prestamo
        WHERE Id_Grupo = %s
    """, (id_grupo,))
    total_prestamos = cur.fetchone()["total"] or 0

    st.info(f"💵 **Ahorros acumulados:** ${total_ahorros:,.2f}")
    st.info(f"📉 **Préstamos vigentes:** ${total_prestamos:,.2f}")

    st.success("Puedes seguir navegando para ver reportes o validaciones.")
# ================================================================
#   SECCIÓN 3 — REPORTES CONSOLIDADOS (solo CSV)
# ================================================================
def reportes_consolidados(distrito):

    st.subheader("📑 Reportes consolidados del distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # CARGAR GRUPOS DEL DISTRITO
    # ------------------------------------------------------------
    cur.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Distrito = %s
        ORDER BY Nombre_grupo ASC
    """, (distrito,))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No hay grupos cargados para generar reportes.")
        return

    dict_grupos = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    tipo_reporte = st.radio(
        "Seleccione el tipo de reporte:",
        ["Reporte por grupo", "Reporte del distrito completo"],
        horizontal=True
    )

    # ============================================================
    #  REPORTE POR GRUPO
    # ============================================================
    if tipo_reporte == "Reporte por grupo":

        nombre = st.selectbox("Seleccione un grupo", list(dict_grupos.keys()))
        id_grupo = dict_grupos[nombre]

        st.markdown(f"### 📘 Reporte: **{nombre}**")

        # -------------------------------
        # AHORROS
        # -------------------------------
        cur.execute("""
            SELECT S.Nombre AS Socia, A.Monto_del_aporte AS Ahorro, A.Fecha_aporte
            FROM Ahorro A
            JOIN Socia S ON S.Id_Socia = A.Id_Socia
            WHERE A.Id_Grupo = %s
            ORDER BY A.Fecha_aporte ASC
        """, (id_grupo,))
        ahorros = cur.fetchall()

        df_ahorros = pd.DataFrame(ahorros)
        st.write("#### 💰 Ahorros")
        if df_ahorros.empty:
            st.info("No hay ahorros registrados.")
        else:
            st.dataframe(df_ahorros, use_container_width=True)

        # -------------------------------
        # PRÉSTAMOS
        # -------------------------------
        cur.execute("""
            SELECT S.Nombre AS Socia, P.Monto, P.Saldo_pendiente, P.Fecha_entrega
            FROM Prestamo P
            JOIN Socia S ON S.Id_Socia = P.Id_Socia
            WHERE P.Id_Grupo = %s
            ORDER BY P.Fecha_entrega ASC
        """, (id_grupo,))
        prestamos = cur.fetchall()

        df_prestamos = pd.DataFrame(prestamos)
        st.write("#### 📉 Préstamos")
        if df_prestamos.empty:
            st.info("No hay préstamos registrados.")
        else:
            st.dataframe(df_prestamos, use_container_width=True)

        # -------------------------------
        # DESCARGA CSV
        # -------------------------------
        if not df_ahorros.empty or not df_prestamos.empty:
            salida = pd.concat(
                [df_ahorros.assign(Tipo="Ahorro"), 
                 df_prestamos.assign(Tipo="Prestamo")],
                ignore_index=True
            )

            st.download_button(
                label="📥 Descargar reporte CSV",
                data=salida.to_csv(index=False).encode("utf-8"),
                file_name=f"Reporte_{nombre}.csv",
                mime="text/csv"
            )

    # ============================================================
    #  REPORTE GENERAL DEL DISTRITO
    # ============================================================
    else:

        st.markdown("### 🏙️ Reporte consolidado del distrito")

        # -------------------------------
        # AHORROS POR GRUPO
        # -------------------------------
        cur.execute("""
            SELECT G.Nombre_grupo, SUM(A.Monto_del_aporte) AS Total_ahorros
            FROM Grupo G
            LEFT JOIN Ahorro A ON A.Id_Grupo = G.Id_Grupo
            WHERE G.Id_Distrito = %s
            GROUP BY G.Id_Grupo
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))
        dist_ahorros = cur.fetchall()

        df_ah = pd.DataFrame(dist_ahorros)
        st.write("#### 💰 Ahorros por grupo")
        st.dataframe(df_ah, use_container_width=True)

        # -------------------------------
        # PRÉSTAMOS POR GRUPO
        # -------------------------------
        cur.execute("""
            SELECT G.Nombre_grupo, SUM(P.Saldo_pendiente) AS Prestamos_activos
            FROM Grupo G
            LEFT JOIN Prestamo P ON P.Id_Grupo = G.Id_Grupo
            WHERE G.Id_Distrito = %s
            GROUP BY G.Id_Grupo
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))
        dist_pres = cur.fetchall()

        df_pr = pd.DataFrame(dist_pres)
        st.write("#### 📉 Préstamos vigentes por grupo")
        st.dataframe(df_pr, use_container_width=True)

        # -------------------------------
        # DESCARGA CSV COMPLETO
        # -------------------------------
        df_full = df_ah.merge(df_pr, on="Nombre_grupo", how="outer")

        st.download_button(
            label="📥 Descargar reporte general (CSV)",
            data=df_full.to_csv(index=False).encode("utf-8"),
            file_name="Reporte_distrito.csv",
            mime="text/csv"
        )
# ================================================================
#   SECCIÓN 4 — VALIDACIONES FINANCIERAS (solo lectura)
# ================================================================
def validaciones_financieras(distrito):

    st.subheader("🧾 Validaciones financieras del distrito")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ------------------------------------------------------------
    # CARGAR GRUPOS DEL DISTRITO
    # ------------------------------------------------------------
    cur.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Distrito = %s
        ORDER BY Nombre_grupo ASC
    """, (distrito,))
    grupos = cur.fetchall()

    if not grupos:
        st.warning("No hay grupos para validar información financiera.")
        return

    dict_grupos = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}

    tipo = st.radio(
        "Seleccione el tipo de validación:",
        [
            "Préstamos en mora",
            "Ahorros inconsistentes",
            "Socias sin aportes",
            "Grupos sin reuniones registradas"
        ],
        horizontal=True
    )

    # ============================================================
    # 1) PRÉSTAMOS EN MORA
    # ============================================================
    if tipo == "Préstamos en mora":

        st.markdown("### 📉 Préstamos en mora")

        cur.execute("""
            SELECT 
                G.Nombre_grupo,
                S.Nombre AS Socia,
                P.Monto,
                P.Saldo_pendiente
            FROM Prestamo P
            JOIN Socia S ON S.Id_Socia = P.Id_Socia
            JOIN Grupo G ON G.Id_Grupo = S.Id_Grupo
            WHERE G.Id_Distrito = %s
              AND P.Saldo_pendiente > 0
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))

        datos = cur.fetchall()

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("No hay préstamos en mora en este distrito.")

    # ============================================================
    # 2) AHORROS INCONSISTENTES (aportes = 0)
    # ============================================================
    elif tipo == "Ahorros inconsistentes":

        st.markdown("### 💰 Ahorros inconsistentes (aportes en cero)")

        cur.execute("""
            SELECT 
                G.Nombre_grupo,
                S.Nombre AS Socia
            FROM Socia S
            JOIN Grupo G ON G.Id_Grupo = S.Id_Grupo
            LEFT JOIN (
                SELECT Id_Socia, SUM(Monto_del_aporte) AS total
                FROM Ahorro
                GROUP BY Id_Socia
            ) A ON A.Id_Socia = S.Id_Socia
            WHERE G.Id_Distrito = %s
              AND (A.total IS NULL OR A.total = 0)
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))

        datos = cur.fetchall()

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("Todos los miembros tienen registros de ahorro.")

    # ============================================================
    # 3) SOCIAS SIN APORTES
    # ============================================================
    elif tipo == "Socias sin aportes":

        st.markdown("### 👩‍🦰 Socias sin aportes registrados")

        cur.execute("""
            SELECT 
                G.Nombre_grupo,
                S.Nombre AS Socia,
                S.DUI
            FROM Socia S
            JOIN Grupo G ON G.Id_Grupo = S.Id_Grupo
            LEFT JOIN Ahorro A ON A.Id_Socia = S.Id_Socia
            WHERE G.Id_Distrito = %s
              AND A.Id_Ahorro IS NULL
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))

        datos = cur.fetchall()

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("Todas las socias tienen al menos un aporte registrado.")

    # ============================================================
    # 4) GRUPOS SIN REUNIONES
    # ============================================================
    elif tipo == "Grupos sin reuniones registradas":

        st.markdown("### 📅 Grupos sin reuniones registradas")

        cur.execute("""
            SELECT 
                G.Nombre_grupo
            FROM Grupo G
            LEFT JOIN Caja_Reunion R ON R.Id_Grupo = G.Id_Grupo
            WHERE G.Id_Distrito = %s
              AND R.Id_Caja IS NULL
            ORDER BY G.Nombre_grupo ASC
        """, (distrito,))

        datos = cur.fetchall()

        if datos:
            df = pd.DataFrame(datos)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("Todos los grupos tienen reuniones registradas.")

    cur.close()
    con.close()
# ================================================================
#   FUNCIONES AUXILIARES (SEGURIDAD Y CONSULTAS)
# ================================================================
def ejecutar_consulta(query, params=None):
    """
    Ejecuta consultas SELECT de forma segura.
    Devuelve un DataFrame o una lista de diccionarios.
    """
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        resultados = cur.fetchall()
        return resultados

    except Exception as e:
        st.error(f"Error al ejecutar consulta: {e}")
        return []

    finally:
        try:
            cur.close()
            con.close()
        except:
            pass


def df_or_empty(data):
    """
    Evita errores cuando el resultado está vacío.
    Devuelve un DataFrame o uno vacío.
    """
    if not data or data is None:
        return pd.DataFrame()
    return pd.DataFrame(data)


# ================================================================
#   MENSAJE FINAL — PIE DE PÁGINA
# ================================================================
def footer_promotora():
    st.markdown("---")
    st.caption("Sistema Solidaridad CVX — Módulo Promotora")
    st.caption("Desarrollado con Streamlit, compatible con MySQL y diseño modular.")


# Llamada automática del footer al final de cada vista
footer_promotora()
