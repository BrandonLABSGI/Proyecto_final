import streamlit as st
from modulos.conexion import obtener_conexion


# ===============================================================
# OBTENER ID DE PROMOTORA BASADO EN EL USUARIO LOGUEADO
# ===============================================================
def obtener_id_promotora(usuario):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Promotora 
        FROM Promotora 
        WHERE Nombre = %s
    """, (usuario,))

    fila = cursor.fetchone()
    return fila["Id_Promotora"] if fila else None



# ===============================================================
# PANEL PRINCIPAL DE PROMOTORA
# ===============================================================
def interfaz_promotora():

    # ----------------------------
    # Validación del rol
    # ----------------------------
    if st.session_state.get("rol") != "Promotora":
        st.error("⛔ No tiene permisos para acceder al panel de promotora.")
        return

    if "usuario" not in st.session_state:
        st.error("⚠ No se detecta usuario logueado.")
        return

    st.title("👩‍💼 Panel de Promotora")
    st.info("Funciones disponibles para la promotora.")

    tabs = ["Gestión de grupos"]
    seleccion = st.sidebar.selectbox("Seleccione una opción", tabs)

    if seleccion == "Gestión de grupos":
        gestion_grupos()



# ===============================================================
# GESTIÓN DE GRUPOS
# ===============================================================
def gestion_grupos():
    st.header("⚙️ Gestión de Grupos")

    sub_opciones = st.tabs(["➕ Crear grupo",
                            "✏️ Editar / Eliminar",
                            "📋 Ver grupos"])

    with sub_opciones[0]:
        crear_grupo()

    with sub_opciones[1]:
        editar_eliminar_grupo()

    with sub_opciones[2]:
        ver_grupos()



# ===============================================================
# CREAR GRUPO
# ===============================================================
def crear_grupo():

    st.subheader("➕ Crear nuevo grupo")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    nombre = st.text_input("Nombre del grupo")
    fecha = st.date_input("Fecha de inicio")
    periodicidad = st.selectbox("Periodicidad", ["Semanal", "Quincenal", "Mensual"])

    if st.button("Guardar grupo"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre para el grupo.")
            return

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO Grupo (Nombre_Grupo, Fecha_Inicio, Periodicidad, Id_Promotora)
            VALUES (%s, %s, %s, %s)
        """, (nombre, fecha, periodicidad, id_promotora))
        con.commit()

        st.success("Grupo creado correctamente.")
        st.rerun()



# ===============================================================
# EDITAR O ELIMINAR GRUPO
# ===============================================================
def editar_eliminar_grupo():

    st.subheader("✏️ Editar o eliminar grupo")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos registrados.")
        return

    opciones = {f"{g['Nombre_Grupo']} (ID {g['Id_Grupo']})": g for g in grupos}
    seleccion = st.selectbox("Seleccione un grupo", opciones.keys())
    g = opciones[seleccion]

    # Campos editables
    nuevo_nombre = st.text_input("Nombre del grupo", g["Nombre_Grupo"])
    nueva_fecha = st.date_input("Fecha de inicio", g["Fecha_Inicio"])
    nueva_periodicidad = st.selectbox("Periodicidad",
                                      ["Semanal", "Quincenal", "Mensual"],
                                      index=["Semanal","Quincenal","Mensual"].index(g["Periodicidad"]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Actualizar grupo"):
            cursor.execute("""
                UPDATE Grupo 
                SET Nombre_Grupo = %s, Fecha_Inicio = %s, Periodicidad = %s
                WHERE Id_Grupo = %s
            """, (nuevo_nombre, nueva_fecha, nueva_periodicidad, g["Id_Grupo"]))
            con.commit()
            st.success("Grupo actualizado correctamente.")
            st.rerun()

    with col2:
        if st.button("🗑️ Eliminar grupo"):

            # VALIDAR SI TIENE PRÉSTAMOS ACTIVOS
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM Prestamo
                WHERE Id_Grupo = %s AND Estado_del_prestamo = 'activo'
            """, (g["Id_Grupo"],))
            tiene_prestamos = cursor.fetchone()["total"]

            if tiene_prestamos > 0:
                st.error("❌ No se puede eliminar este grupo porque tiene préstamos activos.")
                return

            cursor.execute("DELETE FROM Grupo WHERE Id_Grupo = %s", (g["Id_Grupo"],))
            con.commit()
            st.warning("Grupo eliminado correctamente.")
            st.rerun()



# ===============================================================
# VER GRUPOS (CON INFORMACIÓN AMPLIADA)
# ===============================================================
def ver_grupos():

    st.subheader("📋 Ver grupos")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos registrados.")
        return

    opciones = {f"{g['Nombre_Grupo']} (ID {g['Id_Grupo']})": g for g in grupos}
    seleccion = st.selectbox("Seleccione un grupo", opciones.keys())
    g = opciones[seleccion]

    # ===========================
    # EXPANDER: INFO DEL GRUPO
    # ===========================
    with st.expander("📘 Información general del grupo", expanded=True):

        st.write(f"### 👥 {g['Nombre_Grupo']}")
        st.write(f"🆔 ID Grupo: {g['Id_Grupo']}")
        st.write(f"📅 Fecha de inicio: {g['Fecha_Inicio']}")
        st.write(f"🔁 Periodicidad: {g['Periodicidad']}")

        # SOCIAS DEL GRUPO
        cursor.execute("""
            SELECT Id_Socia, Nombre 
            FROM Socia
            WHERE Id_Grupo = %s
        """, (g["Id_Grupo"],))
        socias = cursor.fetchall()

        if socias:
            st.write("👩‍🦰 **Socias del grupo:**")
            for s in socias:
                st.write(f"- {s['Id_Socia']} — {s['Nombre']}")
        else:
            st.info("Este grupo no tiene socias registradas aún.")


    # ===========================
    # EXPANDER: VALIDACIÓN FINANCIERA
    # ===========================
    with st.expander("📑 Validación financiera", expanded=False):

        cursor.execute("""
            SELECT Id_Préstamo, Monto_prestado, Interes_total, Estado_del_prestamo
            FROM Prestamo
            WHERE Id_Grupo = %s
        """, (g["Id_Grupo"],))

        prestamos = cursor.fetchall()

        if not prestamos:
            st.info("No se encontraron préstamos para este grupo.")
        else:
            st.write("### 🧾 Préstamos del grupo:")

            for p in prestamos:
                st.write(f"🆔 ID Préstamo: {p['Id_Préstamo']}")
                st.write(f"💵 Monto prestado: ${p['Monto_prestado']}")
                st.write(f"📌 Interés total: ${p['Interes_total']}")
                st.write(f"📌 Estado: {p['Estado_del_prestamo']}")
                st.markdown("---")


    # ===========================
    # EXPANDER: REPORTES CONSOLIDADOS
    # ===========================
    with st.expander("📊 Reportes consolidados", expanded=False):
        st.info("📌 Próximamente se incluirán reportes por grupo (ingresos, egresos, préstamos, asistencia).")
