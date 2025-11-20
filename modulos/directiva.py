import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL (SOLO DIRECTOR)
# ---------------------------------------------------------
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso al sistema")
        st.warning("⚠️ Acceso restringido. Esta sección es exclusiva para el Director.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, multas, préstamos y ahorros.")

    # SALDO DE CAJA
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT Saldo_actual 
            FROM Caja 
            ORDER BY Id_Caja DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()

        if row:
            saldo = row[0]
            st.info(f"💰 Saldo actual de caja: **${saldo}**")
        else:
            st.warning("⚠ Caja aún no tiene saldo registrado.")
    except:
        st.warning("⚠ No se pudo obtener el saldo actual de caja.")

    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio(
        "Seleccione una sección:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro"
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



# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, '', '', '', 1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"Reunión creada (ID {id_reunion}).")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    asistencia_registro = {}

    for id_socia, nombre in socias:
        col1, col2, col3 = st.columns([1, 3, 2])
        col1.write(id_socia)
        col2.write(nombre)

        asistencia = col3.selectbox(
            "",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )

        asistencia_registro[id_socia] = asistencia

    if st.button("💾 Guardar asistencia general"):

        try:
            for id_socia, asistencia in asistencia_registro.items():

                estado = "Presente" if asistencia == "SI" else "Ausente"

                cursor.execute("""
                    SELECT Id_Asistencia 
                    FROM Asistencia 
                    WHERE Id_Reunion = %s AND Id_Socia = %s
                """, (id_reunion, id_socia))

                ya = cursor.fetchone()

                if ya:
                    cursor.execute("""
                        UPDATE Asistencia
                        SET Estado_asistencia = %s, Fecha = %s
                        WHERE Id_Reunion = %s AND Id_Socia = %s
                    """, (estado, fecha, id_reunion, id_socia))
                else:
                    cursor.execute("""
                        INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                        VALUES (%s, %s, %s, %s)
                    """, (id_reunion, id_socia, estado, fecha))

            con.commit()
            st.success("Asistencia guardada correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"Error al guardar asistencia: {e}")

    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Asistencia"])
        st.dataframe(df)

        total_presentes = df[df["Asistencia"] == "Presente"].shape[0]
        st.success(f"👥 Total presentes: **{total_presentes}**")



# ---------------------------------------------------------
# 🟥 MULTAS (COMPLETAS Y CON CAJA)
# ---------------------------------------------------------
def pagina_multas():

    st.header("⚠️ Gestión de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    st.subheader("➕ Registrar multa")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    dict_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", dict_tipos.keys())
    id_tipo_multa = dict_tipos[tipo_sel]

    monto = st.number_input("💵 Monto:", min_value=0.01)
    fecha_raw = st.date_input("📅 Fecha")
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("📍 Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, %s, %s)
        """, (monto, fecha, estado, id_tipo_multa, id_socia))

        multa_id = cursor.lastrowid

        if estado == "Pagada":
            cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
            row = cursor.fetchone()
            saldo_actual = row[0] if row else 0

            nuevo_saldo = saldo_actual + float(monto)

            cursor.execute("""
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha, Id_Multa)
                VALUES (%s, %s, %s, 1, 2, CURRENT_DATE(), %s)
            """, (f"Pago de multa – {socia_sel}", monto, nuevo_saldo, multa_id))

        con.commit()
        st.success("Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")

    st.subheader("🔍 Filtros")

    col1, col2, col3 = st.columns(3)
    filtro_fecha = col1.date_input("Filtrar por fecha:", value=None)
    filtro_estado = col2.selectbox("Estado:", ["Todos", "A pagar", "Pagada"])
    filtro_nombre = col3.text_input("Buscar por nombre:")

    query = """
        SELECT M.Id_Multa, S.Nombre, M.Monto, M.Fecha_aplicacion, M.Estado,
               T.`Tipo de multa`
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1 = 1
    """

    params = []

    if filtro_fecha:
        query += " AND M.Fecha_aplicacion = %s"
        params.append(filtro_fecha.strftime("%Y-%m-%d"))

    if filtro_estado != "Todos":
        query += " AND M.Estado = %s"
        params.append(filtro_estado)

    if filtro_nombre.strip() != "":
        query += " AND S.Nombre LIKE %s"
        params.append(f"%{filtro_nombre}%")

    cursor.execute(query, tuple(params))
    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(
            multas,
            columns=["ID", "Socia", "Monto", "Fecha", "Estado", "Tipo"]
        )
        st.dataframe(df, use_container_width=True)

        st.subheader("Actualizar estado de multa")

        id_multa_sel = st.selectbox(
            "Seleccione una multa:",
            df["ID"].tolist()
        )

        nuevo_estado = st.selectbox(
            "Nuevo estado:",
            ["A pagar", "Pagada"]
        )

        if st.button("Actualizar multa"):

            cursor.execute("""
                UPDATE Multa
                SET Estado = %s
                WHERE Id_Multa = %s
            """, (nuevo_estado, id_multa_sel))

            if nuevo_estado == "Pagada":
                monto = df[df["ID"] == id_multa_sel]["Monto"].values[0]

                cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
                row = cursor.fetchone()
                saldo_actual = row[0] if row else 0

                nuevo_saldo = saldo_actual + float(monto)

                cursor.execute("""
                    INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha, Id_Multa)
                    VALUES (%s, %s, %s, 1, 2, CURRENT_DATE(), %s)
                """, (f"Pago de multa (actualizado) – ID {id_multa_sel}", monto, nuevo_saldo, id_multa_sel))

            con.commit()
            st.success("Multa actualizada correctamente.")
            st.rerun()
    else:
        st.info("No hay multas registradas con los filtros seleccionados.")



# ---------------------------------------------------------
# 🟩 REGISTRO DE SOCIAS
# ---------------------------------------------------------
def pagina_registro_socias():

    st.header("👩‍🦰 Registrar nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre completo")

    if st.button("💾 Registrar socia"):
        if nombre.strip() == "":
            st.warning("Escribe un nombre.")
        else:
            cursor.execute("""
                INSERT INTO Socia (Nombre, Sexo)
                VALUES (%s, 'F')
            """, (nombre,))
            con.commit()
            st.success("Socia registrada.")
            st.rerun()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        st.dataframe(pd.DataFrame(datos, columns=["ID", "Nombre"]))
