import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion


# ------------------------------------------------------------
#  BOTÓN DE CERRAR SESIÓN
# ------------------------------------------------------------
def boton_cerrar_sesion():
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.rerun()


# ------------------------------------------------------------
#  REGISTRO DE ASISTENCIA
# ------------------------------------------------------------
def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # Fecha de la reunión
    fecha = st.date_input("📅 Fecha de la reunión")

    # Revisar si ya existe la reunión en esa fecha
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, '', '', '', 1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada automáticamente con ID: {id_reunion}")

    # Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: (s[0], s[2]) for s in socias}

    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())

    id_socia = lista_socias[seleccion_socia][0]
    genero_socia = lista_socias[seleccion_socia][1]  # <-- CORREGIDO

    # Mostrar género autocompletado
    st.text_input("Género:", genero_socia, disabled=True)

    # Estado asistencia
    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # Guardar asistencia
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero_socia, fecha))

            con.commit()
            st.success("✅ Asistencia registrada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error al guardar asistencia: {e}")

    # Mostrar registros de asistencia
    st.divider()
    st.subheader("📋 Asistencias registradas")

    cursor.execute("""
        SELECT A.Id_Asistencia, S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay asistencias registradas aún.")


# ------------------------------------------------------------
#  APLICACIÓN DE MULTAS
# ------------------------------------------------------------
def pagina_multas():

    st.subheader("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {s[1]: s[0] for s in socias}

    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[seleccion_socia]

    # Cargar tipos de multa
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    lista_tipos = {t[1]: t[0] for t in tipos}

    seleccion_tipo = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[seleccion_tipo]

    fecha = st.date_input("📅 Fecha de aplicación")

    if st.button("💾 Aplicar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (5, %s, 'A pagar', %s, %s)
            """, (fecha, id_tipo_multa, id_socia))

            con.commit()
            st.success("✅ Multa aplicada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error al aplicar multa: {e}")


# ------------------------------------------------------------
#  INTERFAZ PRINCIPAL DE DIRECTIVA
# ------------------------------------------------------------
def interfaz_directiva():

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    boton_cerrar_sesion()

    opcion = st.selectbox(
        "📌 Seleccione una opción:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if opcion == "Registro de asistencia":
        pagina_asistencia()

    elif opcion == "Aplicar multas":
        pagina_multas()
