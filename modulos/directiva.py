import streamlit as st

# Importaciones corregidas y válidas
from modulos.conexion import obtener_conexion
from modulos.asistencia import interfaz_asistencia
from modulos.administrador import interfaz_administrador


# ============================================================
# PANEL PRINCIPAL DE LA DIRECTIVA
# ============================================================

def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Aquí puede registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)

    # ===================================
    # REUNIONES / ASISTENCIA
    # ===================================
    if seleccion == "Registrar reunión y asistencia":
        interfaz_asistencia()

    # ===================================
    # PRÉSTAMOS (AÚN SIMPLE)
    # ===================================
    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    # ===================================
    # MULTAS
    # ===================================
    elif seleccion == "Aplicar multas":
        pagina_multas()

    # ===================================
    # REPORTES
    # ===================================
    elif seleccion == "Generar actas y reportes":
        pagina_reportes()



# ============================================================
#       MÓDULO DE MULTAS
# ============================================================

def pagina_multas():

    st.header("⚠️ Aplicación de Multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # =============================
    # CARGAR SOCIAS
    # =============================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    socias_dict = {nombre: sid for sid, nombre in socias}

    nombre_socia = st.selectbox("Seleccione la socia:", list(socias_dict.keys()))
    id_socia = socias_dict[nombre_socia]

    # =============================
    # CARGAR TIPOS DE MULTA
    # =============================
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    if not tipos:
        st.warning("⚠ No hay tipos de multa configurados.")
        return

    tipos_dict = {tipo: tid for tid, tipo in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(tipos_dict.keys()))
    id_tipo = tipos_dict[tipo_sel]

    # =============================
    # DATOS DE LA MULTA
    # =============================

    monto = st.number_input("Monto ($)", min_value=0.00, step=0.50, format="%.2f")
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["A pagar", "Pagado"])

    # =============================
    # GUARDAR MULTA
    # =============================
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo, id_socia))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"Error al registrar la multa: {e}")

    cursor.close()
    con.close()



# ============================================================
#       MÓDULO DE PRÉSTAMOS
# ============================================================

def pagina_prestamos():
    st.header("💰 Registro de préstamos o pagos")

    tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
    descripcion = st.text_area("Descripción")

    if st.button("Guardar"):
        st.success("Movimiento registrado (módulo no conectado aún).")



# ============================================================
#       MÓDULO DE REPORTES
# ============================================================

def pagina_reportes():
    st.header("📊 Actas y reportes")
    st.info("Aquí se generarán reportes del grupo próximamente.")
