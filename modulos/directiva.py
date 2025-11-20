import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.autorizar_prestamo import autorizar_prestamo

# 👇 MODULOS NUEVOS
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

    # 🔹 SALDO DE CAJA
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

    # MENU LATERAL
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
# 🟩 REGISTRO DE ASISTENCIA + INGRESOS EXTRAORDINARIOS
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    # -----------------------------------------------------
    # CREAR REUNIÓN SI NO EXISTE
    # -----------------------------------------------------
    if row:
        id_reunion = row[0]
    else:
        try:
            cursor.execute("SHOW COLUMNS FROM Reunion")
            columnas = [col[0] for col in cursor.fetchall()]

            datos = {
                "Fecha_reunion": fecha,
                "observaciones": "",
                "Acuerdos": "",
                "Tema_central": "",
                "Id_Grupo": 1
            }

            for col in columnas:
                if col == "Id_Reunion":
                    continue
                if col not in datos:
                    datos[col] = ""

            query = f"""
                INSERT INTO Reunion ({','.join(datos.keys())})
                VALUES ({','.join(['%s'] * len(datos))})
            """
            cursor.execute(query, list(datos.values()))
            con.commit()

            id_reunion = cursor.lastrowid
            st.info(f"Reunión creada (ID {id_reunion}).")

        except Exception as e:
            st.error(f"⚠ ERROR al crear la reunión: {e}")
            return

    # -----------------------------------------------------
    # LISTA DE SOCIAS (CON ID)
    # -----------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    asistencia_registro = {}

    col1, col2, col3 = st.columns([1, 3, 3])
    col1.write("**ID**")
    col2.write("**Socia**")
    col3.write("**Asistencia (SI / NO)**")

    for id_socia, nombre in socias:

        c1, c2, c3 = st.columns([1, 3, 3])
        c1.write(id_socia)
        c2.write(nombre)

        asistencia = c3.selectbox(
            "",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )

        asistencia_registro[id_socia] = asistencia

    # GUARDAR ASISTENCIA
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

        except Exception as e:
            st.error(f"Error al guardar asistencia: {e}")

    # MOSTRAR ASISTENCIA
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

    st.markdown("---")

    # -----------------------------------------------------
    # INGRESOS EXTRAORDINARIOS (CORREGIDO)
    # -----------------------------------------------------
    st.header("💰 Ingresos extraordinarios de la reunión")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista_socias = cursor.fetchall()

    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in lista_socias}

    socia_sel = st.selectbox("👩 Socia que aporta:", dict_socias.keys())
    id_socia_aporta = dict_socias[socia_sel]

    tipo = st.selectbox("Tipo de ingreso:", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción del ingreso (opcional)")
    monto = st.number_input("Monto recibido ($):", min_value=0.00, step=0.50)

    if st.button("➕ Registrar ingreso extraordinario"):

        try:
            cursor.execute("""
                INSERT INTO IngresosExtra (Id_Reunion, Id_Socia, Tipo, Descripcion, Monto, Fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_reunion, id_socia_aporta, tipo, descripcion, monto, fecha))

            cursor.execute("""
                SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1
            """)
            row = cursor.fetchone()
            saldo_actual = row[0] if row else 0

            nuevo_saldo = saldo_actual + float(monto)

            cursor.execute("""
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE())
            """,
            (
                f"Ingreso extraordinario – {socia_sel}",
                monto,
                nuevo_saldo,
                1,
                2
            ))

            con.commit()
            st.success("Ingreso registrado y agregado a CAJA.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar ingreso: {e}")

    # MOSTRAR INGRESOS DEL DÍA
    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre, I.Tipo, I.Descripcion, I.Monto, I.Fecha
        FROM IngresosExtra I
        JOIN Socia S ON S.Id_Socia = I.Id_Socia
        WHERE I.Id_Reunion = %s
    """, (id_reunion,))
    ingresos = cursor.fetchall()

    if ingresos:
        df_ing = pd.DataFrame(
            ingresos,
            columns=["ID", "Socia", "Tipo", "Descripción", "Monto", "Fecha"]
        )
        st.dataframe(df_ing)


# ---------------------------------------------------------
# 🟥 MULTAS
# ---------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

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

    monto = st.number_input("💵 Monto:", min_value=0.01, step=0.50)
    fecha_raw = st.date_input("📅 Fecha")
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("📍 Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):

        cursor.execute("""
            INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, %s, %s)
        """, (monto, fecha, estado, id_tipo_multa, id_socia))

        con.commit()
        st.success("Multa registrada.")
        st.rerun()


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
