import streamlit as st

# Importar módulos reales del proyecto
from modulos.login import login
from modulos.venta import mostrar_venta
from modulos.administrador import interfaz_admin
from modulos.promotora import interfaz_promotora
from modulos.asistencia import interfaz_asistencia
from modulos.conexion import obtener_conexion   # ← CORRECCIÓN

# ============================================================
# PANEL PRINCIPAL DE LA DIRECTIVA
# ============================================================

def interfaz_directiva():
    st.title("👨‍💼 Panel de Directiva del Grupo")
    st.write("Registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)

    if seleccion == "Registrar reunión y asistencia":
        interfaz_asistencia()

    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif seleccion == "Aplicar multas":
        pagina_multas()

    elif seleccion == "Generar actas y reportes":
        pagina_reportes()


# ============================================================
# PÁGINA: MULTAS
# ============================================================

def pagina_multas():
    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # =============================
    # Cargar SOCIAS desde la BD
    # =============================
    try:
        cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
        socias = cursor.fetchall()

        if not socias:
            st.warning("⚠ No hay socias registradas.")
            return

        dic_socias = {nombre: sid for sid, nombre in socias}

        socia_sel = st.selectbox("Seleccione la socia:", list(dic_socias.keys()))
        id_socia = dic_socias[socia_sel]

    except Exception as e:
        st.error(f"Error cargando socias: {e}")
        return

    # =============================
    # Cargar TIPOS DE MULTA
    # =============================
    try:
        cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
        tipos = cursor.fetchall()

        if not tipos:
            st.warning("⚠ No hay tipos de multa configurados.")
            return

        dic_tipos = {nombre: tid for tid, nombre in tipos}

        tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
        id_tipo = dic_tipos[tipo_sel]

    except Exception as e:
        st.error(f"Error cargando tipos de multa: {e}")
        return

    # =============================
    # Datos adicionales
    # =============================
    monto = st.number_input("Monto de la multa ($)", min_value=0.00, step=0.50, format="%.2f")
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    # =============================
    # Guardar multa
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
            st.error(f"❌ Error registrando la multa: {e}")

    cursor.close()
    con.close()


# ============================================================
# PÁGINA: PRÉSTAMOS (BÁSICO)
# ============================================================

def pagina_prestamos():
    st.header("💰 Registro de préstamos o pagos")
    tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
    descripcion = st.text_area("Descripción")

    if st.button("Guardar movimiento"):
        st.success("Movimiento registrado correctamente (aún no conectado a BD).")


# ============================================================
# PÁGINA: REPORTES
# ============================================================

def pagina_reportes():
    st.header("📊 Generar actas y reportes")
    st.info("Aquí podrás generar reportes del grupo.")
