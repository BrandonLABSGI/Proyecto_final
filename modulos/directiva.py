import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL
# ---------------------------------------------------------
def interfaz_directiva():

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia y multas.")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú lateral
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()
    else:
        pagina_multas()


# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA — VERSIÓN MEJORADA
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("No se pudo conectar a la BD.")
        return
    cursor = con.cursor()

    # Seleccionar fecha
    fecha = st.date_input("📅 Fecha de reunión", value=date.today())

    # ---------------------------------------------------------
    # 🔎 REVISAR SI YA EXISTE REUNIÓN
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
        row = cursor.fetchone()

        if row:
            id_reunion = row[0]   # Reunión ya existe → se usa
        else:
            # Crear reunión nueva (sin Id_Grupo)
            cursor.execute("""
                INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
                VALUES (%s, '', '', '', NULL)
            """, (fecha,))
            con.commit()
            id_reunion = cursor.lastrowid

    except Exception as e:
        st.error(f"⚠ ERROR REAL: {e}")
        return

    # ---------------------------------------------------------
    # OBTENER LISTA DE SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    asistencia_seleccionada = {}
    total_presentes = 0

    # ---------------------------------------------------------
    # TABLA TIPO LISTADO: SOCIA + SELECTBOX SI/NO
    # ---------------------------------------------------------
    for idx, (id_socia, nombre) in enumerate(socias, start=1):

        col1, col2, col3 = st.columns([1, 4, 3])

        with col1:
            st.write(idx)

        with col2:
            st.write(nombre)

        with col3:
            opcion = st.selectbox(
                f"Asistencia_{id_socia}",
                ["NO", "SI"],
                key=f"asiste_{id_socia}"
            )

        asistencia_seleccionada[id_socia] = opcion

        if opcion == "SI":
            total_presentes += 1

    st.write(" ")
    st.success(f"👥 Total presentes: **{total_presentes}**")

    # ---------------------------------------------------------
    # BOTÓN PARA GUARDAR TODA LA ASISTENCIA
    # ---------------------------------------------------------
    if st.button("💾 Guardar asistencia"):

        try:
            for id_socia, estado in asistencia_seleccionada.items():
                estado_texto = "Presente" if estado == "SI" else "Ausente"

                # Verificar si ya existe registro individual
                cursor.execute("""
                    SELECT Id_Asistencia 
                    FROM Asistencia
                    WHERE Id_Reunion = %s AND Id_Socia = %s
                """, (id_reunion, id_socia))

                existe = cursor.fetchone()

                if existe:
                    # Actualizar asistencia existente
                    cursor.execute("""
                        UPDATE Asistencia
                        SET Estado_asistencia = %s, Fecha = %s
                        WHERE Id_Asistencia = %s
                    """, (estado_texto, fecha, existe[0]))
                else:
                    # Insertar nueva asistencia
                    cursor.execute("""
                        INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                        VALUES (%s, %s, %s, %s)
                    """, (id_reunion, id_socia, estado_texto, fecha))

            con.commit()
            st.success("✔ Asistencia guardada correctamente.")

        except Exception as e:
            st.error(f"⚠ ERROR AL GUARDAR: {e}")

    # ---------------------------------------------------------
    # MOSTRAR ASISTENCIAS GUARDADAS
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
        ORDER BY S.Id_Socia ASC
    """, (id_reunion,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Socia", "Estado", "Fecha"])
        st.subheader("📋 Registro actual")
        st.dataframe(df)
    else:
        st.info("Aún no hay asistencia registrada para esta fecha.")


# ---------------------------------------------------------
# 🟥 APLICACIÓN DE MULTAS (SIN CAMBIOS)
# ---------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    cursor.execute("SELECT `Id_Tipo_multa`, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("💵 Monto de la multa:", min_value=0.01, step=0.50, format="%.2f")

    fecha = st.date_input("📅 Fecha de aplicación")

    estado = st.selectbox("Estado del pago:", ["A pagar", "Pagado"])

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo_multa, id_socia))

            con.commit()
            st.success("Multa registrada correctamente.")

        except Exception as e:
            st.error(f"⚠ Error al guardar multa: {e}")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    tabla = cursor.fetchall()

    if tabla:
        df = pd.DataFrame(tabla, columns=["ID", "Socia", "Tipo multa", "Monto", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay multas registradas aún.")

