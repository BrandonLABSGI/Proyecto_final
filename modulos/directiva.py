import streamlit as st
import datetime
from modulos.configuracion.conexion import obtener_conexion

def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    # Menú de opciones
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        ["Registrar reunión y asistencia", "Registrar préstamos o pagos", "Aplicar multas", "Generar actas y reportes"]
    )

    # --- OPCIÓN 1: Registrar reunión y asistencia ---
    if opcion == "Registrar reunión y asistencia":
        st.header("🗓️ Registro de Reunión y Asistencia")
        st.info("Aquí podrás registrar reuniones y marcar asistencia de los miembros.")
        st.warning("Módulo en desarrollo.")

    # --- OPCIÓN 2: Registrar préstamos o pagos ---
    elif opcion == "Registrar préstamos o pagos":
        st.header("💰 Registro de Préstamos o Pagos")
        st.info("Registra nuevos préstamos o pagos del grupo.")
        st.warning("Módulo en desarrollo.")

    # --- OPCIÓN 3: Aplicar multas ---
    elif opcion == "Aplicar multas":
        st.header("⚠️ Aplicación de Multas")

        nombre = st.text_input("Nombre del miembro sancionado")
        motivo = st.text_area("Motivo de la multa")
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
        fecha = datetime.date.today()

        if st.button("Registrar multa"):
            if nombre.strip() == "" or motivo.strip() == "" or monto <= 0:
                st.error("⚠️ Debes llenar todos los campos antes de registrar la multa.")
            else:
                try:
                    conexion = obtener_conexion()
                    cursor = conexion.cursor()

                    # Inserta la multa en la base de datos
                    consulta = """
                        INSERT INTO Multa (Fecha_aplicacion, Monto, Estado, Id_Tipo_multa)
                        VALUES (%s, %s, %s, %s)
                    """
                    valores = (fecha, monto, motivo, 1)
                    cursor.execute(consulta, valores)
                    conexion.commit()

                    st.success(f"✅ Multa registrada exitosamente para {nombre}.")
                except Exception as e:
                    st.error(f"❌ Error al registrar la multa: {e}")
                finally:
                    conexion.close()

    # --- OPCIÓN 4: Generar actas y reportes ---
    elif opcion == "Generar actas y reportes":
        st.header("🧾 Generar Actas y Reportes")
        st.info("Aquí podrás generar actas y reportes consolidados.")
        st.warning("Módulo en desarrollo.")
