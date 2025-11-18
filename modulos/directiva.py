import streamlit as st
from modulos.login import login
from modulos.conexion import obtener_conexion


# ============================================================
#                 INTERFAZ PRINCIPAL DE DIRECTIVA
# ============================================================
def interfaz_directiva():

    st.header("👥 Panel de Directiva del Grupo")
    st.write("Aquí puede registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    opcion = st.sidebar.radio("Seleccione una opción:", opciones)

    if opcion == "Registrar reunión y asistencia":
        pagina_asistencia()

    elif opcion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif opcion == "Aplicar multas":
        pagina_multas()

    elif opcion == "Generar actas y reportes":
        st.info("📄 Módulo de reportes en desarrollo.")



# ============================================================
#                     PÁGINA: ASISTENCIA
# ============================================================
def pagina_asistencia():
    st.subheader("📝 Registro de asistencia del grupo")

    st.info("Este módulo registrará la asistencia más adelante. Ahora es solo una vista previa.")

    fecha = st.date_input("Fecha de la reunión")
    modalidad = st.selectbox("Modalidad (M/H):", ["M", "H"])

    st.subheader("Lista de asistencia")
    st.warning("Pronto aparecerá aquí la lista de socias para marcar presente/ausente.")



# ============================================================
#                 PÁGINA: PRÉSTAMOS Y PAGOS
# ============================================================
def pagina_prestamos():
    st.subheader("💰 Registro de préstamos o pagos")

    st.info("Este módulo se desarrollará después. Aquí se conectará con la BD para registrar préstamos.")



# ============================================================
#                      PÁGINA: MULTAS
# ============================================================
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error: No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # ---------------------------------------------------------------------
    # 1. CARGAR SOCIAS
    # ---------------------------------------------------------------------
    try:
        cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
        socias = cursor.fetchall()
    except Exception as e:
        st.error(f"Error cargando socias: {e}")
        return

    if not socias:
        st.warning("No existen socias registradas.")
        return

    map_socias = {s[1]: s[0] for s in socias}
    socia_seleccionada = st.selectbox("Seleccione la socia:", list(map_socias.keys()))
    id_socia = map_socias[socia_seleccionada]

    # ---------------------------------------------------------------------
    # 2. CARGAR TIPOS DE MULTA (TABLA CON ESPACIOS)
    # ---------------------------------------------------------------------
    try:
        cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
        tipos = cursor.fetchall()
    except Exception as e:
        st.error(f"Error cargando tipos de multa: {e}")
        return

    if not tipos:
        st.warning("No existen tipos de multa registrados.")
        return

    map_tipos = {t[1]: t[0] for t in tipos}
    tipo_sel = st.selectbox("Tipo de multa:", list(map_tipos.keys()))
    id_tipo_multa = map_tipos[tipo_sel]

    # ---------------------------------------------------------------------
    # 3. DATOS DE LA MULTA
    # ---------------------------------------------------------------------
    monto = st.number_input("Monto de la multa ($)", min_value=0.00, step=0.50, format="%.2f")
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["A pagar", "Pagado"])

    # ---------------------------------------------------------------------
    # 4. BOTÓN PARA GUARDAR MULTA
    # ---------------------------------------------------------------------
    if st.button("💾 Registrar multa"):

        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo_multa, id_socia))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error registrando la multa: {e}")

    con.close()
