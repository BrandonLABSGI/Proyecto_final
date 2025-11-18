import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion
from datetime import date


# -----------------------------------------
# PANEL PRINCIPAL
# -----------------------------------------
def interfaz_directiva():
    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia y multas.")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú
    opcion = st.sidebar.selectbox("📌 Seleccione una opción:", 
                                  ["Registro de asistencia", "Aplicar multas"])

    if opcion == "Registro de asistencia":
        pagina_asistencia()
    elif opcion == "Aplicar multas":
        pagina_multas()


# -----------------------------------------
# 📘 PÁGINA DE ASISTENCIA
# -----------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # FECHA DE LA REUNIÓN
    fecha = st.date_input("📅 Fecha de la reunión", value=date.today())

    # Crear u obtener reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
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
        st.info(f"📌 Reunión creada con ID: {id_reunion}")

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    filas = cursor.fetchall()

    if not filas:
        st.warning("No hay socias registradas.")
        return

    socias = {fila[1]: fila for fila in filas}  # {"Lucia Ramirez": (1,"Lucia","F")}

    nombre_socia = st.selectbox("👩 Seleccione la socia:", list(socias.keys()))

    if nombre_socia not in socias:
        return

    id_socia, _, genero = socias[nombre_socia]

    st.text_input("Género:", genero, disabled=True)

    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # GUARDAR
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))
            con.commit()
            st.success("✅ Asistencia registrada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

    # MOSTRAR EXISTENTES
    cursor.execute("""
        SELECT A.Id_Asistencia, S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))
    registros = cursor.fetchall()

    st.subheader("📋 Asistencias registradas")
    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay asistencias registradas aún.")


# -----------------------------------------
# ⚠️ PÁGINA DE MULTAS
# -----------------------------------------
def pagina_multas():

    st.header("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    filas = cursor.fetchall()

    if not filas:
        st.warning("No hay socias registradas.")
        return

    socias = {fila[1]: fila[0] for fila in filas}  # {"Lucia": 1}

    nombre = st.selectbox("👩 Seleccione la socia:", list(socias.keys()))
    id_socia = socias[nombre]

    # TIPOS DE MULTA (tabla con espacio)
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()

    if not tipos:
        st.warning("No hay tipos de multa registrados.")
        return

    lista_tipos = {t[1]: t[0] for t in tipos}  # {"Mora": 1}

    tipo_multa = st.selectbox("📌 Tipo de multa:", list(lista_tipos.keys()))
    id_tipo = lista_tipos[tipo_multa]

    monto = st.number_input("💲 Monto:", min_value=1.00)
    fecha = st.date_input("📅 Fecha de aplicación", value=date.today())

    # GUARDAR MULTA
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, 'A pagar', %s, %s)
            """, (monto, fecha, id_tipo, id_socia))
            con.commit()
            st.success("✅ Multa registrada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

    # MOSTRAR MULTAS
    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, TM.`Tipo de multa`, M.Monto, M.Fecha_aplicacion, M.Estado
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` TM ON TM.Id_Tipo_multa = M.Id_Tipo_multa
    """)
    lista = cursor.fetchall()

    st.subheader("📋 Multas registradas")

    if lista:
        df = pd.DataFrame(lista, columns=["ID", "Socia", "Tipo", "Monto", "Fecha", "Estado"])
        st.dataframe(df)
    else:
        st.info("No hay multas registradas aún.")
