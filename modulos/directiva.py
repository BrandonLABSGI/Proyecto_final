import streamlit as st
from modulos.login import login
from modulos.venta import mostrar_venta
from modulos.administrador import interfaz_admin
from modulos.promotora import interfaz_promotora
from modulos.asistencia import interfaz_asistencia
from modulos.config.conexion import obtener_conexion


# ================================
#   FUNCIÓN PRINCIPAL DIRECTIVA
# ================================
def interfaz_directiva():

    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registrar reuniones, préstamos, asistencia, multas y generar reportes.")

    # Barra lateral
    st.sidebar.header("Menú principal")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Registrar asistencia",
        "Generar actas y reportes"
    ]

    opcion = st.sidebar.radio("Seleccione una opción:", opciones)

    # ============================
    # OPCIÓN: REUNIONES/ASISTENCIA
    # ============================
    if opcion == "Registrar reunión y asistencia":
        st.write("Módulo en construcción.")

    # ============================
    # OPCIÓN: PRÉSTAMOS
    # ============================
    elif opcion == "Registrar préstamos o pagos":
        st.write("Módulo en construcción.")

    # ============================
    # OPCIÓN: MULTAS
    # ============================
    elif opcion == "Aplicar multas":
        pagina_multas()

    # ============================
    # OPCIÓN: FORMULARIO DE ASISTENCIA
    # ============================
    elif opcion == "Registrar asistencia":
        interfaz_asistencia()

    # ============================
    # OPCIÓN: REPORTES
    # ============================
    elif opcion == "Generar actas y reportes":
        st.write("Módulo en construcción.")



# ================================
#   PÁGINA DE MULTAS (YA FUNCIONAL)
# ================================
def pagina_multas():

    con = obtener_conexion()
    cursor = con.cursor()

    st.header("⚠️ Aplicación de multas")

    # Socias -------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_ for id_, nombre in socias}

    nombre_socia = st.selectbox("Seleccione la socia:", list(lista_socias.keys()))
    id_socia = lista_socias[nombre_socia]

    # Tipos de multa -----------------------
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()
    lista_multas = {tipo: id_ for id_, tipo in tipos}

    tipo_multa = st.selectbox("Tipo de multa:", list(lista_multas.keys()))
    id_tipo = lista_multas[tipo_multa]

    # Datos
    monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=1.0)
    fecha = st.date_input("Fecha de aplicación")

    estado = st.selectbox("Estado:", ["A pagar", "Pagado"])

    if st.button("💾 Registrar multa"):

        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo, id_socia))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error registrando la multa: {e}")

    con.close()
