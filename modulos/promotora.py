import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date
import pandas as pd

# --------------------------
# PANEL PRINCIPAL DE PROMOTORA
# --------------------------
def panel_promotora(id_promotora):
    st.title("👩‍💼 Panel de Promotora")
    st.markdown("Supervisa tus grupos, registra nuevos y valida información financiera.")

    opcion = st.sidebar.radio("Selecciona una opción:", 
                              ["📁 Consultar grupos", 
                               "📝 Registrar nuevo grupo",
                               "💵 Validar información financiera", 
                               "📊 Reportes consolidados"])

    if opcion == "📁 Consultar grupos":
        mostrar_grupos(id_promotora)
    elif opcion == "📝 Registrar nuevo grupo":
        registrar_grupo(id_promotora)
    elif opcion == "💵 Validar información financiera":
        validar_finanzas(id_promotora)
    elif opcion == "📊 Reportes consolidados":
        generar_reportes(id_promotora)


# --------------------------
# SECCIÓN 1: CONSULTAR GRUPOS
# --------------------------
def mostrar_grupos(id_promotora):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM Grupo WHERE Id_Promotora = %s", (id_promotora,))
    grupos = cur.fetchall()
    cur.close()
    con.close()

    st.subheader("📋 Grupos Asignados")
    if grupos:
        for g in grupos:
            with st.expander(f"📌 {g['Nombre_grupo']}"):
                st.write(f"**Tasa de interés:** {g['Tasa_de_interes']}%")
                st.write(f"**Periodicidad:** {g['Periodicidad_de_reuniones']}")
                st.write(f"**Tipo de multa:** {g['Tipo_de_multa']}")
                st.write(f"**Reglas del préstamo:** {g['Reglas_de_prestamo']}")
                st.write(f"**Fecha de inicio:** {g['fecha_inicio']}")
                st.write(f"**Distrito:** {g['Id_Distrito']}")
    else:
        st.info("No tienes grupos registrados todavía.")


# --------------------------
# SECCIÓN 2: REGISTRAR NUEVO GRUPO
# --------------------------
def registrar_grupo(id_promotora):
    st.subheader("📝 Registrar nuevo grupo")

    with st.form("form_grupo"):
        nombre = st.text_input("Nombre del grupo")
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
        tasa_interes = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
        periodicidad = st.selectbox("Periodicidad de reuniones", ["Semanal", "Quincenal", "Mensual"])
        tipo_multa = st.text_input("Tipo de multa (ejemplo: 'Retraso de pago')")
        reglas = st.text_area("Reglas del préstamo")
        id_distrito = st.number_input("ID del distrito", min_value=1, step=1)

        enviar = st.form_submit_button("✅ Registrar grupo")

        if enviar:
            if nombre.strip() == "" or reglas.strip() == "":
                st.warning("⚠️ Todos los campos son obligatorios.")
            else:
                try:
                    con = obtener_conexion()
                    cur = con.cursor()
                    cur.execute("""
                        INSERT INTO Grupo (Nombre_grupo, fecha_inicio, Tasa_de_interes, 
                                           Periodicidad_de_reuniones, Tipo_de_multa, 
                                           Reglas_de_prestamo, Id_Promotora, Id_Distrito)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nombre, fecha_inicio, tasa_interes, periodicidad, tipo_multa, reglas, id_promotora, id_distrito))
                    con.commit()
                    cur.close()
                    con.close()
                    st.success(f"✅ Grupo '{nombre}' registrado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al registrar el grupo: {e}")


# --------------------------
# SECCIÓN 3: VALIDAR FINANZAS
# --------------------------
def validar_finanzas(id_promotora):
    st.subheader("💵 Validar información financiera")
    st.info("Aquí podrás revisar préstamos, pagos y movimientos de los grupos.")

    st.warning("⚠️ Módulo en desarrollo. Pronto podrás aprobar pagos y revisar saldos.")


# --------------------------
# SECCIÓN 4: REPORTES CONSOLIDADOS
# --------------------------
def generar_reportes(id_promotora):
    st.subheader("📊 Reporte Consolidado")
    st.write("Descarga los datos de todos los grupos registrados por ti.")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT Nombre_grupo, fecha_inicio, Tasa_de_interes, Periodicidad_de_reuniones, 
               Tipo_de_multa, Reglas_de_prestamo, Id_Distrito
        FROM Grupo WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cur.fetchall()
    cur.close()
    con.close()

    if grupos:
        df = pd.DataFrame(grupos)
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Descargar reporte en Excel",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"reporte_grupos_promotora_{id_promotora}.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay grupos registrados para mostrar.")
