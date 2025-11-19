import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.autorizar_prestamo import autorizar_prestamo  # << OPCIÓN NUEVA


# =========================================================
# PANEL PRINCIPAL (DIRECTOR)
# =========================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso al sistema")
        st.warning("⚠️ Acceso restringido. Solo el Director puede ingresar aquí.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, ingresos, multas y préstamos.")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ---------------- MENU ----------------
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",    # << NUEVA OPCIÓN
            "Generar reporte"
        ]
    )

    # ---------------- RUTEO ----------------
    if menu == "Registro de asistencia":
        pagina_asistencia()
    elif menu == "Aplicar multas":
        pagina_multas()
    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()
    elif menu == "Autorizar préstamo":
        autorizar_prestamo()       # << AQUÍ SE LLAMA LA NUEVA FUNCIÓN
    else:
        pagina_reporte()



# =========================================================
# FUNCIÓN: ASISTENCIA
# =========================================================
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
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, %s, %s, %s, %s)
        """, (fecha, "", "", "", 1))
        con.commit()
        id_reunion = cursor.lastrowid

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    registros = {}

    for id_socia, nombre in socias:
        estado = st.selectbox(
            f"{nombre}",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )
        registros[id_socia] = estado

    if st.button("Guardar asistencia"):
        for id_socia, estado in registros.items():
            final = "Presente" if estado == "SI" else "Ausente"

            cursor.execute("""
                INSERT INTO Asistencia(Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                VALUES(%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE Estado_asistencia=%s
            """, (id_reunion, id_socia, final, fecha, final))

        con.commit()
        st.success("Asistencia guardada correctamente.")



# =========================================================
# FUNCIÓN: MULTAS
# =========================================================
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista = cursor.fetchall()

    dict_socias = {nombre: id_socia for id_socia, nombre in lista}

    socia_sel = st.selectbox("Seleccione socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    dict_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    monto = st.number_input("Monto:", min_value=0.01, step=0.50)
    fecha = st.date_input("Fecha").strftime("%Y-%m-%d")

    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("Registrar multa"):

        cursor.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo, id_socia))
        con.commit()

        st.success("Multa registrada.")



# =========================================================
# FUNCIÓN: NUEVAS SOCIAS
# =========================================================
def pagina_registro_socias():

    st.header("Registro de nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre de la socia")

    if st.button("Registrar"):
        if nombre.strip() == "":
            st.warning("Debe escribir un nombre.")
        else:
            cursor.execute("INSERT INTO Socia(Nombre, Sexo) VALUES(%s,'F')", (nombre,))
            con.commit()
            st.success("Socia registrada.")
            st.rerun()



# =========================================================
# FUNCIÓN: REPORTE
# =========================================================
def pagina_reporte():

    st.header("📄 Reporte general del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("Fecha del reporte", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # ---- ASISTENCIA ----
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        JOIN Reunion R ON R.Id_Reunion = A.Id_Reunion
        WHERE R.Fecha_reunion = %s
    """, (fecha,))
    datos = cursor.fetchall()

    if datos:
        st.subheader("Asistencia")
        st.dataframe(pd.DataFrame(datos, columns=["Socia", "Estado"]))

    # ---- Ingresos ----
    cursor.execute("""
        SELECT S.Nombre, I.Tipo, I.Descripcion, I.Monto
        FROM IngresosExtra I
        JOIN Socia S ON S.Id_Socia = I.Id_Socia
        JOIN Reunion R ON R.Id_Reunion = I.Id_Reunion
        WHERE R.Fecha_reunion = %s
    """, (fecha,))
    ing = cursor.fetchall()

    if ing:
        st.subheader("Ingresos extraordinarios")
        df = pd.DataFrame(ing, columns=["Socia", "Tipo", "Descripción", "Monto"])
        st.dataframe(df)
        st.success(f"Total: ${df['Monto'].sum():.2f}")
