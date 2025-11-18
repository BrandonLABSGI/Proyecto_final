import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion


# ======================================================
#            PANEL PRINCIPAL DE DIRECTIVA
# ======================================================

def interfaz_directiva():

    st.title("👩‍⚖️ Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    menu = st.sidebar.radio(
        "📌 Opciones del panel:",
        [
            "Registrar reunión y asistencia",
            "Registrar préstamos o pagos",
            "Aplicar multas",
            "Cerrar sesión"
        ]
    )

    if menu == "Registrar reunión y asistencia":
        pagina_asistencia()

    elif menu == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Cerrar sesión":
        st.session_state["sesion_iniciada"] = False
        st.success("Sesión cerrada.")
        st.rerun()




# ======================================================
#                   📌 ASISTENCIA
# ======================================================

def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar con la base de datos.")
        return

    cursor = con.cursor()

    # 1️⃣ SELECCIONAR FECHA
    fecha = st.date_input("📅 Fecha de la reunión")

    # 2️⃣ VERIFICAR O CREAR LA REUNIÓN
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        cursor.execute(
            "INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo) "
            "VALUES (%s,'','','','1')",
            (fecha,)
        )
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada con ID: {id_reunion}")

    # 3️⃣ OBTENER SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {s[1]: (s[0], s[2]) for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())

    id_socia = lista_socias[socia_sel][0]
    genero = lista_socias[socia_sel][2]

    # Mostrar género autocompletado
    st.text_input("Género:", genero, disabled=True)

    # Estado asistencia
    estado = st.selectbox("📍 Estado de asistencia:", ["Presente", "Ausente"])

    # 4️⃣ GUARDAR ASISTENCIA
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))

            con.commit()
            st.success("✔ Asistencia registrada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error al guardar: {e}")

    st.divider()

    # 5️⃣ MOSTRAR ASISTENCIAS YA REGISTRADAS
    st.subheader("📋 Asistencias registradas")

    cursor.execute("""
        SELECT A.Id_Asistencia, S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
        ORDER BY A.Id_Asistencia DESC
    """, (id_reunion,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay asistencias registradas para esta reunión.")



# ======================================================
#                   📌 PRÉSTAMOS (placeholder)
# ======================================================

def pagina_prestamos():

    st.header("💰 Registro de préstamos y pagos")
    st.info("Esta sección se implementará después.")

    descripcion = st.text_input("Descripción del registro")
    monto = st.number_input("Monto ($)", min_value=0.00)

    if st.button("Guardar"):
        st.success("✔ Movimiento registrado (simulado).")




# ======================================================
#                   📌 MULTAS
# ======================================================

def pagina_multas():

    st.header("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con la base de datos.")
        return
    cursor = con.cursor()

    # OBTENER SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dic_socias = {s[1]: s[0] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dic_socias.keys())
    id_socia = dic_socias[socia_sel]

    # TIPOS DE MULTA
    cursor.execute("SELECT Id_Tipo_multa, Nombre_tipo FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    dic_tipos = {t[1]: t[0] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dic_tipos.keys())
    id_tipo = dic_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.00)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["Pendiente", "Pagada"])

    # GUARDAR MULTA
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo, id_socia))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error guardando multa: {e}")
