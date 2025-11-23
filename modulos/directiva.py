import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja
from modulos.gastos_grupo import gastos_grupo
from modulos.cierre_ciclo import cierre_ciclo
from modulos.reglas import gestionar_reglas


# ============================================================
# VERIFICAR ROL
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")
    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ============================================================
    # MENÚ LATERAL PRINCIPAL
    # ============================================================
    menu = st.sidebar.radio(
        "Seleccione una opción:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Registro de ingresos extraordinarios",
            "Gastos del grupo",
            "Reporte de caja",
            "Reglas internas",
            "Cierre de ciclo"
        ]
    )

    # RUTEO A CADA FUNCIÓN
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

    elif menu == "Registro de ingresos extraordinarios":
        pagina_ingresos_extra()

    elif menu == "Gastos del grupo":
        gastos_grupo()

    elif menu == "Reporte de caja":
        reporte_caja()

    elif menu == "Reglas internas":
        gestionar_reglas()

    elif menu == "Cierre de ciclo":
        cierre_ciclo()



# ============================================================
# REGISTRO DE ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    fecha_raw = st.date_input("📅 Fecha de la reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Verificar si ya existe reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row["Id_Reunion"]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.success(f"Reunión creada (ID {id_reunion}).")

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    asistencia_registro = {}

    for s in socias:
        asistencia_registro[s["Id_Socia"]] = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["SI", "NO"],
            key=f"asis_{s['Id_Socia']}"
        )

    if st.button("💾 Guardar asistencia"):
        for id_socia, value in asistencia_registro.items():
            estado = "Presente" if value == "SI" else "Ausente"

            cursor.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Reunion=%s AND Id_Socia=%s
            """, (id_reunion, id_socia))
            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s, Fecha=%s
                    WHERE Id_Asistencia=%s
                """, (estado, fecha, existe["Id_Asistencia"]))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                    VALUES(%s,%s,%s,%s)
                """, (id_reunion, id_socia, estado, fecha))

        con.commit()
        st.success("Asistencia guardada.")
        st.rerun()

    # MOSTRAR REGISTROS
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))
    datos = cursor.fetchall()
    if datos:
        st.dataframe(pd.DataFrame(datos), hide_index=True)

    cursor.close()
    con.close()



# ============================================================
# MULTAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    lista_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # TIPO DE MULTA
    cursor.execute("SELECT Id_Tipo_multa, Tipo_multa FROM Tipo_multa")
    tipos = cursor.fetchall()
    lista_tipos = {t["Tipo_multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto,Fecha_aplicacion,Estado,Id_Tipo_multa,Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo_multa, id_socia))

        con.commit()
        st.success("Multa registrada.")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Multas registradas")

    # FILTROS
    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(lista_socias.keys()))
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])
    filtro_fecha = st.date_input("Filtrar por fecha:", value=None)

    query = """
        SELECT M.Id_Multa, S.Nombre, T.Tipo_multa,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia=M.Id_Socia
        JOIN Tipo_multa T ON T.Id_Tipo_multa=M.Id_Tipo_multa
        WHERE 1=1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre=%s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado=%s"
        params.append(filtro_estado)

    if filtro_fecha:
        query += " AND M.Fecha_aplicacion=%s"
        params.append(filtro_fecha.strftime("%Y-%m-%d"))

    query += " ORDER BY M.Id_Multa DESC"

    cursor.execute(query, params)
    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas)
        st.dataframe(df, hide_index=True)



# ============================================================
# REGISTRO DE SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre de la socia:")

    if st.button("Registrar socia"):
        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        cursor.execute("INSERT INTO Socia(Nombre,Sexo) VALUES(%s,'F')", (nombre,))
        con.commit()
        st.success("Socia registrada.")
        st.rerun()

    cursor.execute("SELECT Id_Socia,Nombre FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        st.dataframe(pd.DataFrame(datos, columns=["ID","Nombre"]), hide_index=True)



# ============================================================
# INGRESOS EXTRAORDINARIOS
# ============================================================
def pagina_ingresos_extra():

    st.header("💰 Ingresos extraordinarios")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    fecha_raw = st.date_input("Fecha de reunión:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Verificar reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row["Id_Reunion"]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid

    # SOCIAS
    cursor.execute("SELECT Id_Socia,Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    lista_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    tipo = st.selectbox("Tipo:", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción:")
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        # Registrar ingreso
        cursor.execute("""
            INSERT INTO IngresosExtra(Id_Reunion,Id_Socia,Tipo,Descripcion,Monto,Fecha)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (id_reunion, id_socia, tipo, descripcion, monto, fecha))

        # ACTUALIZAR CAJA
        cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
        row = cursor.fetchone()
        saldo_actual = float(row["saldo_final"]) if row else 0

        nuevo_saldo = saldo_actual + monto

        cursor.execute("""
            INSERT INTO caja_reunion(fecha, saldo_inicial, ingresos, egresos, saldo_final)
            VALUES(%s,%s,%s,%s,%s)
        """, (fecha, saldo_actual, monto, 0, nuevo_saldo))

        con.commit()
        st.success("Ingreso registrado.")
        st.rerun()

    cursor.close()
    con.close()

