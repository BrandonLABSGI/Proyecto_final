import streamlit as st
from datetime import date
from modulos.Configuración.conexion import obtener_conexion

def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opcion = st.sidebar.radio("Selecciona una opción:", [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ])

    # -------------------------------------------------------------------------
    # ⚠️ OPCIÓN: APLICAR MULTAS
    # -------------------------------------------------------------------------
    if opcion == "Aplicar multas":
        st.subheader("⚠️ Aplicación de multas")

        id_usuario = st.number_input("ID del miembro sancionado (Id_Usuario)", min_value=1, step=1)
        id_tipo = st.number_input("ID del tipo de multa (Id_Tipo_multa)", min_value=1, step=1)
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
        estado = st.selectbox("Estado de la multa", ["Pendiente", "Pagada", "Condonada"])
        fecha = date.today()

        if st.button("Registrar multa"):
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                # Inserta en la tabla Multa según tu estructura
                cursor.execute("""
                    INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Usuario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (monto, fecha, estado, id_tipo, id_usuario))

                con.commit()
                st.success(f"✅ Multa registrada correctamente para el usuario ID {id_usuario}.")
            except Exception as e:
                st.error(f"❌ Error al registrar la multa: {e}")
            finally:
                con.close()
