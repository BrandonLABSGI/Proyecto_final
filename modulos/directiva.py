import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL SEGÚN EL ROL
# ---------------------------------------------------------
def interfaz_directiva():

    # Verificación del rol
    rol = st.session_state.get("rol", None)

    if rol is None:
        st.error("No hay sesión activa.")
        return

    # Mensaje según el rol
    st.title(f"👤 Panel del {rol.capitalize()} del Grupo")
    st.write("Administre funciones del sistema según su rol.")

    # BOTÓN DE CERRAR SESIÓN
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # DIRECTOR → acceso completo
    if rol == "director":
        menu = st.sidebar.radio(
            "Seleccione una sección:",
            ["Registro de asistencia", "Aplicar multas"]
        )

        if menu == "Registro de asistencia":
            pagina_asistencia()
        else:
            pagina_multas()

    # ADMIN / PROMOTORA → acceso limitado
    else:
        st.warning("⚠ Acceso limitado. No tienes permiso para ver estas funciones.")
        st.info("Puedes usar otras funciones del sistema, pero esta sección es solo para el Director.")


# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA (COMPLETO)
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    # FECHA
    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # VERIFICAR/CREAR REUNIÓN
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        try:
            cursor.execute("""
                INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
                VALUES (%s,'','','',1)
            """, (fecha,))
            con.commit()
            id_reunion = cursor.lastrowid
            st.info(f"Reunión creada automáticamente (ID {id_reunion}).")
        except Exception as e:
            st.error("❌ ERROR: No se pudo crear la reunión. Verifica que Id_Grupo exista.")
            return

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    asistencia_registro = {}

    # TABLA
    col1, col2, col3 = st.columns([1, 3, 3])
    col1.write("**#**")
    col2.write("**Socia**")
    col3.write("**Asistencia (SI / NO)**")

    for idx, (id_socia, nombre, sexo) in enumerate(socias, start=1):
        c1, c2, c3 = st.columns([1, 3, 3])

        c1.write(idx)
        c2.write(nombre)

        asistencia = c3.selectbox(
            "",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )

        asistencia_registro[id_socia] = (asistencia, sexo)

    # GUARDAR ASISTENCIA
    if st.button("💾 Guardar asistencia general"):
        try:
            for id_socia, (asistencia, genero) in asistencia_registro.items():

                estado = "Presente" if asistencia == "SI" else "Ausente"

                # ¿Ya existe?
                cursor.execute("""
                    SELECT Id_Asistencia FROM Asistencia
                    WHERE Id_Reunion = %s AND Id_Socia = %s
                """, (id_reunion, id_socia))

                ya_existe = cursor.fetchone()

                if ya_existe:
                    cursor.execute("""
                        UPDATE Asistencia
                        SET Estado_asistencia=%s, Fecha=%s, Genero=%s
                        WHERE Id_Reunion=%s AND Id_Socia=%s
                    """, (estado, fecha, genero, id_reunion, id_socia))

                else:
                    cursor.execute("""
                        INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_reunion, id_socia, estado, genero, fecha))

            con.commit()
            st.success("Asistencia guardada correctamente.")

        except Exception as e:
            st.error(f"❌ Error al guardar asistencia: {e}")

    # RESULTADOS
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE Id_Reunion = %s
    """, (id_reunion,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Socia", "Asistencia"])
        st.subheader("📋 Registro actual")
        st.dataframe(df)

        total_presentes = df[df["Asistencia"] == "Presente"].shape[0]
        st.success(f"👥 Total presentes: {total_presentes}")
    else:
        st.info("Aún no hay asistencia registrada.")


# ---------------------------------------------------------
# 🟥 MULTAS COMPLETAS (FILTRAR + ACTUALIZAR + VER TODO)
# ---------------------------------------------------------
def pagina_multas():

    st.header("⚠ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # TIPOS DE MULTA
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("💵 Monto:", min_value=0.01, step=0.50)
    fecha_raw = st.date_input("📅 Fecha de aplicación")
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("📍 Estado:", ["A pagar", "Pagada"])

    # GUARDAR MULTA
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo_multa, id_socia))
            con.commit()
            st.success("Multa registrada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al guardar multa: {e}")

    st.markdown("---")
    st.subheader("🔎 Filtrar multas registradas")

    # FILTROS
    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(lista_socias.keys()))
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])
    filtro_fecha_raw = st.date_input("Filtrar por fecha:", value=None)
    filtro_fecha = filtro_fecha_raw.strftime("%Y-%m-%d") if filtro_fecha_raw else None

    query = """
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1=1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre = %s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado = %s"
        params.append(filtro_estado)

    if filtro_fecha:
        query += " AND M.Fecha_aplicacion = %s"
        params.append(filtro_fecha)

    query += " ORDER BY M.Id_Multa DESC"
    cursor.execute(query, params)

    multas = cursor.fetchall()

    st.subheader("📋 Multas registradas")

    if multas:
        cols = st.columns([1, 3, 3, 2, 2, 2, 2])
        cols[0].write("**ID**")
        cols[1].write("**Socia**")
        cols[2].write("**Tipo**")
        cols[3].write("**Monto**")
        cols[4].write("**Estado**")
        cols[5].write("**Fecha**")
        cols[6].write("**Acción**")

        for row in multas:
            id_multa, socia, tipo, monto, estado_actual, fecha = row

            c1, c2, c3, c4, c5, c6, c7 = st.columns([1,3,3,2,2,2,2])

            c1.write(id_multa)
            c2.write(socia)
            c3.write(tipo)
            c4.write(f"${monto}")

            nuevo_estado = c5.selectbox(
                "",
                ["A pagar", "Pagada"],
                index=0 if estado_actual == "A pagar" else 1,
                key=f"est_{id_multa}"
            )

            c6.write(str(fecha))

            if c7.button("Actualizar", key=f"btn_{id_multa}"):
                cursor.execute("UPDATE Multa SET Estado=%s WHERE Id_Multa=%s",
                               (nuevo_estado, id_multa))
                con.commit()
                st.success(f"Estado actualizado para multa #{id_multa}")
                st.rerun()

    else:
        st.info("No hay multas registradas con esos filtros.")
