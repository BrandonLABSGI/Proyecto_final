import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.gastos_grupo import gastos_grupo
from modulos.reporte_caja import reporte_caja
from modulos.reglas import gestionar_reglas
from modulos.cierre_ciclo import cierre_ciclo

# CAJA ÚNICA POR REUNIÓN
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


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

    # BOTÓN DE CERRAR SESIÓN
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # MOSTRAR SALDO REAL
    try:
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        row = cur.fetchone()
        saldo = row["saldo_actual"] if row else 0
        st.info(f"💰 *Saldo actual de caja:* **${saldo:.2f}**")
    except:
        st.warning("⚠ No se pudo obtener el saldo actual de caja.")

    # MENÚ
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

    # RUTEO
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
        reporte_caja()
    elif menu == "Cierre de ciclo":
        cierre_ciclo()



# ============================================================
# 🎯 REGISTRO DE ASISTENCIA — CORREGIDO (USANDO Id_Reunion)
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # FECHA
    fecha_raw = st.date_input("📅 Fecha de reunión:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # OBTENER/CREAR EL REGISTRO DE caja_reunion
    Id_Reunion = obtener_o_crear_reunion(fecha)

    # LISTA DE SOCIAS
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas aún.")
        return

    st.subheader("Lista de asistencia")
    estados = {}

    for s in socias:
        eleccion = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Sí", "No"],
            key=f"asis_{s['Id_Socia']}"
        )
        estados[s["Id_Socia"]] = "Presente" if eleccion == "Sí" else "Ausente"

    # BOTÓN GUARDAR
    if st.button("💾 Guardar asistencia"):

        for id_socia, estado in estados.items():

            # VALIDAR SI YA EXISTE
            cur.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Socia = %s AND Fecha = %s
            """, (id_socia, fecha))

            existe = cur.fetchone()

            # ACTUALIZAR
            if existe:
                cur.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s
                    WHERE Id_Asistencia=%s
                """, (estado, existe["Id_Asistencia"]))

            # INSERTAR (AQUÍ ESTABA TU ERROR)
            else:
                cur.execute("""
                    INSERT INTO Asistencia(Id_Socia, Fecha, Estado_asistencia, Id_Reunion)
                    VALUES(%s, %s, %s, %s)
                """, (id_socia, fecha, estado, Id_Reunion))

        con.commit()
        st.success("Asistencia guardada correctamente.")
        st.rerun()


    # MOSTRAR ASISTENCIA GUARDADA
    cur.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Fecha = %s
    """, (fecha,))

    registros = cur.fetchall()

    if registros:
        st.subheader("📋 Asistencia registrada")
        st.dataframe(pd.DataFrame(registros), use_container_width=True)

    # RESUMEN
    cur.execute("SELECT Estado_asistencia FROM Asistencia WHERE Fecha = %s", (fecha,))
    registros_tot = cur.fetchall()

    if registros_tot:
        total_socias = len(registros_tot)
        presentes = sum(1 for r in registros_tot if r["Estado_asistencia"] == "Presente")
        ausentes = total_socias - presentes

        st.subheader("📊 Resumen")
        st.info(
            f"👩‍🦰 Total: **{total_socias}**\n"
            f"🟢 Presentes: **{presentes}**\n"
            f"🔴 Ausentes: **{ausentes}**"
        )

    st.markdown("---")

    # ===============================
    # INGRESOS EXTRAORDINARIOS
    # ===============================

    st.subheader("💵 Ingreso extraordinario")

    fecha_ing = st.date_input("📅 Fecha del ingreso:", date.today())
    fecha_ingreso = fecha_ing.strftime("%Y-%m-%d")

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista = cur.fetchall()

    if not lista:
        st.warning("⚠ Necesitas al menos 1 socia.")
        return

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in lista}

    socia_sel = st.selectbox("Socia que aporta:", list(dict_socias.keys()))
    id_socia_ing = dict_socias[socia_sel]

    concepto = st.selectbox("Concepto:", ["Rifa", "Donación", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        id_caja_ingreso = obtener_o_crear_reunion(fecha_ingreso)

        registrar_movimiento(
            id_caja=id_caja_ingreso,
            tipo="Ingreso",
            categoria=f"Ingreso extraordinario — {concepto}",
            monto=monto
        )

        st.success("Ingreso extraordinario registrado correctamente.")
        st.rerun()
