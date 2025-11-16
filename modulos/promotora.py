import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

# ============================================================
# 👩‍💼 PANEL DE PROMOTORA
# ============================================================

def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")
    st.write("Supervisa tus grupos, registra nuevos y valida información financiera.")

    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📋 Consultar grupos",
            "🆕 Registrar nuevo grupo",
            "💵 Validar información financiera",
            "📊 Reportes consolidados"
        ]
    )

    if opcion == "📋 Consultar grupos":
        consultar_grupos()
    elif opcion == "🆕 Registrar nuevo grupo":
        registrar_grupo()
    elif opcion == "💵 Validar información financiera":
        validar_finanzas()
    elif opcion == "📊 Reportes consolidados":
        reportes()

# ============================================================
# 📋 CONSULTAR GRUPOS
# ============================================================

def consultar_grupos():
    st.subheader("📋 Grupos Asignados")
    con = obtener_conexion()
    cur = con.cursor()
    usuario = st.session_state["usuario"]

    try:
        cur.execute("""
            SELECT g.Nombre_grupo
            FROM Grupo g
            INNER JOIN Empleado e ON g.Id_Promotora = e.Id_Empleado
            WHERE e.Usuario = %s
        """, (usuario,))
        grupos = cur.fetchall()

        if not grupos:
            st.info("No tienes grupos asignados actualmente.")
            return

        for g in grupos:
            with st.expander(f"📌 {g[0]}"):
                st.write("**Información general del grupo:**")
                st.write("- Fecha de inicio: *(desde la base de datos)*")
                st.write("- Tasa de interés: *(desde la base de datos)*")
                st.write("- Periodicidad: *(desde la base de datos)*")
    except Exception as e:
        st.error(f"❌ Error al consultar los grupos: {e}")
    finally:
        cur.close()
        con.close()

# ============================================================
# 🆕 REGISTRAR NUEVO GRUPO
# ============================================================

def registrar_grupo():
    st.subheader("🆕 Registrar un nuevo grupo")
    con = obtener_conexion()
    cur = con.cursor()

    nombre = st.text_input("Nombre del grupo")
    fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
    tasa = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
    periodicidad = st.text_input("Periodicidad de reuniones (por ejemplo: semanal, quincenal)")
    tipo_multa = st.text_input("Tipo de multa (por ejemplo: Retraso, Inasistencia)")
    reglas = st.text_area("Reglas de préstamo o funcionamiento del grupo")
    id_promotora = obtener_id_promotora()
    id_distrito = st.number_input("ID del distrito", min_value=1, step=1)

    if st.button("💾 Guardar grupo"):
        if not nombre.strip():
            st.warning("⚠️ El nombre del grupo es obligatorio.")
            return
        try:
            cur.execute("""
                INSERT INTO Grupo (Nombre_grupo, fecha_inicio, Tasa_de_interes,
                Periodicidad_de_reuniones, Tipo_de_multa, Reglas_de_prestamo, Id_Promotora, Id_Distrito)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (nombre, fecha_inicio, tasa, periodicidad, tipo_multa, reglas, id_promotora, id_distrito))
            con.commit()
            st.success(f"✅ Grupo '{nombre}' registrado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al registrar grupo: {e}")
        finally:
            cur.close()
            con.close()

# ============================================================
# 💵 VALIDAR INFORMACIÓN FINANCIERA
# ============================================================

def validar_finanzas():
    st.subheader("💵 Validar información financiera")
    st.info("Aquí podrás revisar préstamos, pagos y movimientos de los grupos.")
    st.warning("⚠️ Módulo en desarrollo. Pronto podrás aprobar pagos y revisar saldos.")

# ============================================================
# 📊 REPORTES CONSOLIDADOS
# ============================================================

def reportes():
    st.subheader("📊 Reportes consolidados")
    st.info("Visualiza reportes de grupos, préstamos y reuniones.")
    st.warning("⚠️ Esta sección se habilitará para exportar a PDF o Excel.")

# ============================================================
# 🔍 FUNCIÓN AUXILIAR: OBTENER ID DE LA PROMOTORA ACTUAL
# ============================================================

def obtener_id_promotora():
    con = obtener_conexion()
    cur = con.cursor()
    usuario = st.session_state["usuario"]

    try:
        cur.execute("SELECT Id_Empleado FROM Empleado WHERE Usuario = %s", (usuario,))
        resultado = cur.fetchone()
        if resultado:
            return resultado[0]
        else:
            st.error("⚠️ No se encontró el ID de la promotora en la base de datos.")
            return None
    except Exception as e:
        st.error(f"❌ Error al obtener ID de promotora: {e}")
        return None
    finally:
        cur.close()
        con.close()
