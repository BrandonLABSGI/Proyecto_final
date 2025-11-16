import streamlit as st
from datetime import date
import sys
import importlib.util
import pathlib
import mysql.connector

# ======================================================
# ✅ Cargar manualmente la conexión desde “Configuración/conexion.py”
# (Esto evita el error por la tilde en el nombre de la carpeta)
# ======================================================
ruta = pathlib.Path(__file__).resolve().parent / "Configuración" / "conexion.py"
spec = importlib.util.spec_from_file_location("conexion_configuracion", ruta)
conexion_mod = importlib.util.module_from_spec(spec)
sys.modules["conexion_configuracion"] = conexion_mod
spec.loader.exec_module(conexion_mod)

# Importar la función de conexión
obtener_conexion = conexion_mod.obtener_conexion

# ======================================================
# 🎯 Interfaz de la Directiva
# ======================================================
def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    # Menú lateral
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📅 Registrar reunión y asistencia",
            "💰 Registrar préstamos o pagos",
            "⚠️ Aplicar multas",
            "🧾 Generar actas y reportes"
        ]
    )

    # ======================================================
    # 🧾 OPCIÓN 1: Registrar reunión y asistencia
    # ======================================================
    if "reunión" in opcion:
        st.subheader("📅 Registro de reuniones y asistencias")
        st.info("Aquí podrás registrar las asistencias de los miembros del grupo.")
        st.text_input("Tema de la reunión")
        st.date_input("Fecha", value=date.today())
        st.text_area("Observaciones")
        st.button("Registrar asistencia")

    # ======================================================
    # 💰 OPCIÓN 2: Registrar préstamos o pagos
    # ======================================================
    elif "préstamos" in opcion:
        st.subheader("💰 Registro de préstamos o pagos")
        st.text_input("Nombre del miembro")
        st.number_input("Monto ($)", min_value=0.0, step=0.5)
        st.selectbox("Tipo de movimiento", ["Préstamo", "Pago"])
        st.text_area("Observaciones")
        st.button("Registrar movimiento")

    # ======================================================
    # ⚠️ OPCIÓN 3: Aplicar multas
    # ======================================================
    elif "multas" in opcion:
        st.subheader("⚠️ Aplicación de multas")

        nombre = st.text_input("Nombre del miembro sancionado")
        motivo = st.text_area("Motivo de la multa")
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)

        if st.button("Registrar multa"):
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Insertar en la tabla Multa
                query = """
                    INSERT INTO Multa (Fecha_aplicacion, Estado, Monto, Id_Usuario)
                    VALUES (%s, %s, %s, %s)
                """
                valores = (date.today(), motivo, monto, 1)  # ID de usuario genérico (ajústalo si es necesario)
                cursor.execute(query, valores)
                con.commit()

                st.success("✅ Multa registrada correctamente en la base de datos.")
                cursor.close()
                con.close()
            except mysql.connector.Error as err:
                st.error(f"❌ Error al registrar multa: {err}")

    # ======================================================
    # 🧾 OPCIÓN 4: Generar actas y reportes
    # ======================================================
    elif "reportes" in opcion:
        st.subheader("🧾 Generar actas y reportes")
        st.info("Aquí podrás generar actas y visualizar reportes de actividades.")
        st.selectbox("Selecciona el tipo de reporte", ["Actas", "Pagos", "Multas", "Asistencia"])
        st.date_input("Desde", value=date(2025, 1, 1))
        st.date_input("Hasta", value=date.today())
        st.button("Generar reporte")
