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

    # Menú lateral SEPARADO
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()
    else:
        pagina_multas()


# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la BD.")
        return
    cursor = con.cursor()

    # Selección de fecha
    fecha = st.date_input("📅 Fecha de reunión", value=date.today())

    # Verificar si la reunión ya existe
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"Reunión creada (ID {id_reunion}).")

    # Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    registros = cursor.fetchall()

    # Crear diccionario SEGURO
    socias = {
        fila[1]: {"id": fila[0], "sexo": fila[2]}
        for fila in registros
    }

    nombre = st.selectbox("👩 Socia:", list(socias.keys()))
    id_socia = socias[nombre]["id"]
    sexo = socias[nombre]["sexo"]

    st.text_input("Género:", sexo, disabled=True)

    estado = st.selectbox("📍 Estado:", ["Presente", "Ausente"])

    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s,%s,%s,%s,%s)
            """, (id_reunion, id_socia, estado, sexo, fecha))
            con.commit()
            st.success("Asistencia registrada.")
        except Exception as e:
            st.error(f"Error: {e}")

    # Mostrar asistencia
    cursor.execute("""
        SELECT S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))
    tabla = cursor.fetchall()

    st.subheader("📋 Registro actual")
    if tabla:
        df = pd.DataFrame(tabla, columns=["Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("Aún no hay asistencia registrada.")


# ---------------------------------------------------------
# 🟥 APLICACIÓN DE MULTAS
# ---------------------------------------------------------
def pagina_multas():
    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    # Obtener socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # Obtener tipos de multa
    cursor.execute("SELECT `Id_Tipo_multa`, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()

    lista_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    # --- MONTO EN DECIMALES ($) ---
    monto = st.number_input(
        "💵 Monto de la multa ($):",
        min_value=0.01,
        step=0.01,
        format="%.2f"
    )

    fecha = st.date_input("📅 Fecha de aplicación", value=date.today())

    estado = "A pagar"

    # --- REGISTRAR MULTA ---
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo_multa, id_socia))

            con.commit()
            st.success("✅ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"⚠ Error al guardar multa: {e}")

    # Mostrar multas registradas
    st.divider()
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)

    registros = cursor.fetchall()
    if registros:
        df = pd.DataFrame(registros, 
            columns=["ID", "Socia", "Tipo multa", "Monto", "Estado", "Fecha"]
        )
        st.dataframe(df)
    else:
        st.info("No hay multas registradas aún.")
