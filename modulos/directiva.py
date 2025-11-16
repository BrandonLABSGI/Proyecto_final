import streamlit as st
import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="btfcfbzptdyxq4f8afmu"
    )

def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opcion = st.sidebar.radio("Selecciona una opción:", [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ])

    if opcion == "Aplicar multas":
        st.subheader("⚠️ Aplicación de multas")
        nombre = st.text_input("Nombre del miembro sancionado")
        motivo = st.text_area("Motivo de la multa")
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)

        if st.button("Registrar multa"):
            if nombre and motivo and monto > 0:
                try:
                    con = obtener_conexion()
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO Multa (Estado, Id_Tipo_multa, Id_Usuario, Id_Asistencia, Id_Prestamo) VALUES (%s,%s,%s,%s,%s)",
                        ("Pendiente", 1, 1, 1, 1)
                    )
                    con.commit()
                    con.close()
                    st.success("✅ Multa registrada correctamente")
                except Exception as e:
                    st.error(f"Error al registrar multa: {e}")
            else:
                st.warning("⚠️ Completa todos los campos antes de registrar la multa.")
