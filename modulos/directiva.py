import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# ===== MÓDULOS EXTERNOS =====
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja

# ===== CAJA ÚNICA =====
from modulos.caja import (
    obtener_o_crear_reunion,
    registrar_movimiento,
    obtener_saldo_actual,
    obtener_reporte_reunion
)

# ===== OTROS =====
from modulos.gastos_grupo import gastos_grupo
from modulos.cierre_ciclo import cierre_ciclo
from modulos.reglas import gestionar_reglas
from modulos.reglas_utils import obtener_reglas



# ============================================================
# PANEL PRINCIPAL — DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ===== Fecha global (solo para reportes) =====
    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    fecha_sel = st.date_input(
        "📅 Fecha del reporte",
        value=pd.to_datetime(st.session_state["fecha_global"])
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = fecha_sel

    # ===== Saldo global =====
    try:
        saldo_global = obtener_saldo_actual()
        st.success(f"💰 Saldo REAL en caja: ${saldo_global:.2f}")
    except Exception as e:
        st.error(f"⚠ No se pudo obtener el saldo actual: {e}")

    # ===== Reporte del día =====
    try:
        reporte = obtener_reporte_reunion(fecha_sel)

        ingresos = reporte["ingresos"]
        egresos = reporte["egresos"]
        balance = reporte["balance"]
        saldo_final = reporte["saldo_final"]

        st.subheader(f"📊 Reporte del día {fecha_sel}")
        st.info(
            f"""
            📥 **Ingresos del día:** ${ingresos:.2f}  
            📤 **Egresos del día:** ${egresos:.2f}  
            📘 **Balance del día:** ${balance:.2f}  
            🔚 **Saldo final registrado ese día:** ${saldo_final:.2f}
            """
        )

    except Exception as e:
        st.error(f"⚠ Error al generar reporte diario: {e}")

    # ============================================
    # MENÚ LATERAL
    # ============================================
    menu = st.sidebar.radio(
        "Menú rápido:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Registrar otros gastos",
            "Cierre de ciclo",
            "Reporte de caja",
            "Reglas internas"
        ]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Registrar otros gastos":
        gastos_grupo()

    elif menu == "Cierre de ciclo":
        cierre_ciclo()

    elif menu == "Reporte de caja":
        reporte_caja()

    elif menu == "Reglas internas":
        gestionar_reglas()

    # ============================================
    # RESUMEN DEL CICLO
    # ============================================
    reglas = obtener_reglas()

    if reglas:
        fecha_inicio_ciclo = reglas.get("fecha_inicio_ciclo", None)

        if fecha_inicio_ciclo:

            st.markdown("---")
            st.subheader("📊 Resumen del ciclo (desde reglas internas)")

            con = obtener_conexion()
            cur = con.cursor(dictionary=True)

            cur.execute("""
                SELECT 
                    IFNULL(SUM(ingresos),0) AS total_ingresos,
                    IFNULL(SUM(egresos),0) AS total_egresos
                FROM caja_reunion
                WHERE fecha >= %s
            """, (fecha_inicio_ciclo,))

            tot = cur.fetchone()

            total_ingresos_ciclo = float(tot["total_ingresos"])
            total_egresos_ciclo = float(tot["total_egresos"])
            balance = total_ingresos_ciclo - total_egresos_ciclo

            st.write(f"📥 **Ingresos acumulados:** ${total_ingresos_ciclo:.2f}")
            st.write(f"📤 **Egresos acumulados:** ${total_egresos_ciclo:.2f}")
            st.write(f"💼 **Balance acumulado:** ${balance:.2f}")

            cur.close()
            con.close()
        else:
            st.info("⚠ No está definida la fecha de inicio del ciclo en Reglas Internas.")
    else:
        st.info("⚠ Debes registrar reglas internas primero.")



# ============================================================
# MULTAS — TOTALMENTE CONECTADAS A REGLAS INTERNAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    from modulos.reglas_utils import obtener_reglas
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ Debes registrar reglas internas primero.")
        return

    multa_inasistencia = float(reglas.get("multa_inasistencia", 0))
    multa_mora = float(reglas.get("multa_mora", 0))

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    opciones_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    st.subheader("➕ Registrar nueva multa")

    tipo_sel = st.selectbox("Tipo de multa:", ["Inasistencia", "Mora préstamo", "Otra"])

    if tipo_sel == "Inasistencia":
        monto_default = multa_inasistencia
        editable = False
    elif tipo_sel == "Mora préstamo":
        monto_default = multa_mora
        editable = False
    else:
        monto_default = 0.25
        editable = True

    socia_sel = st.selectbox("👩 Socia:", opciones_socias.keys())
    id_socia = opciones_socias[socia_sel]

    fecha = st.date_input("📅 Fecha", date.today()).strftime("%Y-%m-%d")

    monto = st.number_input(
        "Monto ($)",
        min_value=0.25,
        step=0.25,
        value=monto_default,
        disabled=not editable
    )

    estado_sel = st.selectbox("Estado:", ["A pagar", "Pagada"])

    cursor.execute("""
        SELECT Estado_asistencia
        FROM Asistencia
        WHERE Id_Socia=%s AND Fecha=%s
        LIMIT 1
    """, (id_socia, fecha))

    row_asistencia = cursor.fetchone()

    if row_asistencia and row_asistencia["Estado_asistencia"] == "Permiso":
        st.warning("🔒 La socia tenía PERMISO. No se puede aplicar multa.")
        return

    if st.button("💾 Registrar multa"):

        cursor.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, NULL, %s)
        """, (monto, fecha, estado_sel, id_socia))

        con.commit()
        st.success("✔ Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")

    st.subheader("📌 Multas pendientes")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, M.Monto, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON M.Id_Socia=S.Id_Socia
        WHERE Estado='A pagar'
        ORDER BY Id_Multa DESC
    """)

    pendientes = cursor.fetchall()

    for m in pendientes:
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        c1.write(f"#{m['Id_Multa']}")
        c2.write(m["Nombre"])
        c3.write(f"${m['Monto']}")

        if c4.button("Pagar", key=f"pay_{m['Id_Multa']}"):
            id_caja = obtener_o_crear_reunion(m["Fecha_aplicacion"])

            registrar_movimiento(
                id_caja,
                "Ingreso",
                f"Pago de multa — {m['Nombre']}",
                float(m["Monto"])
            )

            cursor.execute("UPDATE Multa SET Estado='Pagada' WHERE Id_Multa=%s", (m["Id_Multa"],))
            con.commit()
            st.success("✔ Multa pagada.")
            st.rerun()

    cursor.close()
    con.close()



# ============================================================
# ASISTENCIA
# ============================================================
def pagina_asistencia():

    from modulos.reglas_utils import obtener_reglas

    st.header("📝 Registro de asistencia")

    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No hay reglas internas registradas.")
        return

    multa_inasistencia = float(reglas["multa_inasistencia"])

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    fecha_raw = st.date_input("📅 Fecha de reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row["Id_Reunion"]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s, '', '', '', 1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.success(f"Reunión creada (ID {id_reunion}).")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    registro = {}
    for s in socias:
        estado = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Presente", "Ausente", "Permiso"],
            key=f"asis_{s['Id_Socia']}"
        )
        registro[s["Id_Socia"]] = estado

    if st.button("💾 Guardar asistencia"):

        for id_socia, estado in registro.items():

            if estado == "Presente":
                est = "Presente"
            elif estado == "Permiso":
                est = "Permiso"
            else:
                est = "Ausente"

                cursor.execute("""
                    INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                    VALUES (%s, %s, 'A pagar', 1, %s)
                """, (multa_inasistencia, fecha, id_socia))

            cursor.execute("""
                SELECT Id_Asistencia FROM Asistencia
                WHERE Id_Reunion=%s AND Id_Socia=%s
            """, (id_reunion, id_socia))

            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s, Fecha=%s
                    WHERE Id_Asistencia=%s
                """, (est, fecha, existe["Id_Asistencia"]))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                    VALUES(%s, %s, %s, %s)
                """, (id_reunion, id_socia, est, fecha))

        con.commit()
        st.success("✔ Asistencia registrada correctamente.")
        st.rerun()

    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))

    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, hide_index=True)

    cursor.close()
    con.close()
