import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion

def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    # Conexión BD
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # 1️⃣ Selección de FECHA
    fecha = st.date_input("📅 Fecha de la reunión")

    # 2️⃣ Obtener la reunión existente o crear una nueva
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        # Crear nueva reunión automáticamente
        cursor.execute(
            "INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo) 
             VALUES (%s,'','','','1')",
            (fecha,)
        )
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada automáticamente con ID: {id_reunion}")

    # 3️⃣ Cargar SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: (s[0], s[2]) for s in socias}

    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())

    id_socia = lista_socias[seleccion_socia][0]
    genero_socia = lista_socias[seleccion_socia][2]

    # 4️⃣ Autocompletar género
    st.text_input("Género:", genero_socia, disabled=True)

    # 5️⃣ Estado asistencia
    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # 6️⃣ Guardar asistencia
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

    # 7️⃣ Mostrar registros guardados
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
