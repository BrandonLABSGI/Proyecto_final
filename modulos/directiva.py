import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS (no generan import loops)
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.gastos_grupo import gastos_grupo
from modulos.reglas import gestionar_reglas
from modulos.cierre_ciclo import cierre_ciclo

# CAJA
from modulos.caja import asegurar_reunion, obtener_saldo_actual


# ============================================================
# PANEL PRINCIPAL — DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de Directiva — Solidaridad CVX")

    # Cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Mostrar saldo actual de forma segura
    try:
        saldo = obtener_saldo_actual()
        st.info(f"💰 *Saldo actual de caja:* **${saldo:.2f}**")
    except Exception as e:
        st.warning("⚠ No se pudo obtener el saldo actual de caja.")

    # Menú lateral
    menu = st.sidebar.radio(
        "📌 Selección rápida:",
        [
            "Registro de asistencia",
            "Registrar nuevas socias",
            "Reglas internas",
            "Registrar ahorro",
            "Aplicar multas",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Gastos del grupo",
            "Reporte de caja",
            "Cierre de ciclo",
        ]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()

    elif menu == "Reglas internas":
        gestionar_reglas()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Gastos del grupo":
        gastos_grupo()

    elif menu == "Reporte de caja":
        # Import dinámico para evitar ciclos
        from modulos.reporte_caja import reporte_caja
        reporte_caja()

    elif menu == "Cierre de ciclo":
        cierre_ciclo()


# ============================================================
# 📝 REGISTRO DE ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    fecha_raw = st.date_input("📅 Fecha de reunión:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Crear reunión para asistencia
    id_caja = asegurar_reunion(fecha)

    # Lista de socias
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    st.subheader("Lista de asistencia")
    estados = {}

    for s in socias:
        eleccion = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Sí", "No"],
            key=f"asis_{s['Id_Socia']}"
        )
        estados[s["Id_Socia"]] = "Presente" if eleccion == "Sí" else "Ausente"

    if st.button("💾 Guardar asistencia"):

        for id_socia, estado in estados.items():

            cur.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Socia=%s AND Fecha=%s
            """, (id_socia, fecha))
            existe = cur.fetchone()

            if existe:
                cur.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s
                    WHERE Id_Asistencia=%s
                """, (estado, existe["Id_Asistencia"]))

            else:
                cur.execute("""
                    INSERT INTO Asistencia(Id_Socia, Fecha, Estado_asistencia, Id_Reunion)
                    VALUES(%s, %s, %s, %s)
                """, (id_socia, fecha, estado, id_caja))

        con.commit()
        st.success("Asistencia registrada correctamente.")
        st.rerun()

    # Mostrar asistencia del día
    cur.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Fecha=%s
    """, (fecha,))
    registros = cur.fetchall()

    if registros:
        st.subheader("📋 Asistencia registrada")
        st.dataframe(pd.DataFrame(registros), use_container_width=True)


# ============================================================
# 👩‍🦰 REGISTRAR NUEVAS SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registrar nuevas socias")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    nombre = st.text_input("Nombre completo de la socia:")
    dui = st.text_input("Número de DUI (9 dígitos):", max_chars=9)
    telefono = st.text_input("Número de teléfono (8 dígitos):", max_chars=8)

    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        if not dui.isdigit() or len(dui) != 9:
            st.warning("El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        if not telefono.isdigit() or len(telefono) != 8:
            st.warning("El teléfono debe tener exactamente 8 dígitos numéricos.")
            return

        cur.execute("""
            INSERT INTO Socia(Nombre, DUI, Telefono)
            VALUES(%s, %s, %s)
        """, (nombre, dui, telefono))

        con.commit()
        st.success(f"Socia '{nombre}' registrada correctamente.")
        st.rerun()

    # Mostrar lista
    cur.execute("SELECT Id_Socia, Nombre, DUI FROM Socia ORDER BY Id_Socia ASC")
    data = cur.fetchall()

    if data:
        st.subheader("📋 Lista de socias")
        st.dataframe(pd.DataFrame(data), use_container_width=True)


# ============================================================
# ⚠️ MULTAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicar multas")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # Socias
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    dict_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # Tipos de multa
    cur.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cur.fetchall()
    dict_tipos = {t["Tipo de multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    tipo_lower = tipo_sel.lower()

    # Monto sugerido
    if "inasistencia" in tipo_lower:
        monto_def = 1.00
    elif "mora" in tipo_lower:
        monto_def = 3.00
    else:
        monto_def = 0.00

    monto = st.number_input("Monto ($):", min_value=0.00, value=monto_def, step=0.25)

    fecha_raw = st.date_input("Fecha:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cur.execute("""
            INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, %s, %s)
        """, (monto_def, fecha, estado, id_tipo, id_socia))

        con.commit()

        st.success("Multa registrada correctamente.")
        st.rerun()

    # Mostrar multas
    st.subheader("📋 Multas registradas")
    fecha_filtro = st.date_input("Fecha a consultar:", date.today())
    fecha_filtro = fecha_filtro.strftime("%Y-%m-%d")

    cur.execute("""
        SELECT 
            M.Id_Multa, S.Nombre AS Socia,
            T.`Tipo de multa`, M.Monto,
            M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE M.Fecha_aplicacion=%s
        ORDER BY M.Id_Multa ASC
    """, (fecha_filtro,))

    registros = cur.fetchall()

    if registros:
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
