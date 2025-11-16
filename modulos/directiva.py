import streamlit as st
from modulos.Configuracion.conexion import obtener_conexion

def interfaz_directiva():
    st.header("👔 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opcion = st.radio("Selecciona una opción:", [
        "📋 Registrar reunión y asistencia",
        "💰 Registrar préstamos o pagos",
        "⚠️ Aplicar multas",
        "🧾 Generar actas y reportes"
    ])

    if opcion == "⚠️ Aplicar multas":
        st.subheader("⚠️ Aplicación de multas")

        nombre = st.text_input("Nombre del miembro sancionado")
        motivo = st.text_area("Motivo de la multa")
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)

        if st.button("Registrar multa"):
            if nombre and motivo and monto > 0:
                try:
                    con = obtener_conexion()
                    cur = con.cursor()
                    cur.execute("INSERT INTO Multa (Estado, Monto, Id_Usuario) VALUES (%s, %s, %s)", ("Pendiente", monto, 1))
                    con.commit()
                    con.close()
                    st.success("✅ Multa registrada correctamente.")
                except Exception as e:
                    st.error(f"Error al registrar multa: {e}")
            else:
                st.warning("Completa todos los campos antes de registrar.")

    elif opcion == "📋 Registrar reunión y asistencia":
        st.info("Módulo de reuniones en desarrollo.")
    elif opcion == "💰 Registrar préstamos o pagos":
        st.info("Módulo de préstamos en desarrollo.")
    elif opcion == "🧾 Generar actas y reportes":
        st.info("Módulo de reportes en desarrollo.")
