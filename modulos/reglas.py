import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ---------------------------------------------------------
#  PANEL PRINCIPAL DE GESTIÓN DE REGLAS
# ---------------------------------------------------------
def gestionar_reglas():

    st.title("📘 Reglas internas del grupo")

    menu = st.radio(
        "Seleccione una sección:",
        [
            "Editor de reglas internas",
            "Comité directivo",
            "Permisos válidos de inasistencia",
            "Exportar reglas en PDF"
        ]
    )

    if menu == "Editor de reglas internas":
        editar_reglas()

    elif menu == "Comité directivo":
        gestionar_comite()

    elif menu == "Permisos válidos de inasistencia":
        gestionar_permisos()

    elif menu == "Exportar reglas en PDF":
        exportar_pdf()



# =========================================================
#  1) EDITOR DE REGLAS INTERNAS
# =========================================================
def editar_reglas():

    st.subheader("📝 Editor de reglas internas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Cargar única regla (id_regla = 1)
    cursor.execute("SELECT * FROM reglas_grupo WHERE id_regla = 1")
    datos = cursor.fetchone()

    if not datos:
        st.error("No existe registro base en reglas_grupo (id_regla=1).")
        return

    nombre_grupo = st.text_input("Nombre del Grupo", datos["nombre_grupo"])
    nombre_comunidad = st.text_input("Comunidad", datos["nombre_comunidad"])
    multa_inasistencia = st.number_input("Multa por inasistencia", value=float(datos["multa_inasistencia"]))
    ahorro_minimo = st.number_input("Ahorro mínimo", value=float(datos["ahorro_minimo"]))
    interes_por_10 = st.number_input("Interés por cada $10 prestados (%)", value=float(datos["interes_por_10"]))
    prestamo_maximo = st.number_input("Préstamo máximo", value=float(datos["prestamo_maximo"]))
    plazo_maximo = st.number_input("Plazo máximo (meses)", value=int(datos["plazo_maximo"]))
    otras = st.text_area("Otras reglas", datos["otras_reglas"])

    if st.button("💾 Guardar cambios"):

        cursor.execute("""
            UPDATE reglas_grupo SET 
                nombre_grupo=%s,
                nombre_comunidad=%s,
                multa_inasistencia=%s,
                ahorro_minimo=%s,
                interes_por_10=%s,
                prestamo_maximo=%s,
                plazo_maximo=%s,
                otras_reglas=%s
            WHERE id_regla=1
        """, (
            nombre_grupo, nombre_comunidad, multa_inasistencia,
            ahorro_minimo, interes_por_10, prestamo_maximo,
            plazo_maximo, otras
        ))

        con.commit()
        st.success("Reglas internas actualizadas correctamente.")



# =========================================================
#  2) COMITÉ DIRECTIVO
# =========================================================
def gestionar_comite():

    st.subheader("👩‍💼 Comité Directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    st.markdown("### ➕ Registrar nuevo miembro")

    cargo = st.text_input("Cargo (Ejemplo: Presidenta)")
    nombre = st.text_input("Nombre de la socia")

    if st.button("Registrar miembro"):

        cursor.execute("""
            INSERT INTO comite_directiva(id_regla, cargo, nombre_socia)
            VALUES(1, %s, %s)
        """, (cargo, nombre))

        con.commit()
        st.success("Miembro agregado al comité.")
        st.rerun()

    # Mostrar comité
    cursor.execute("SELECT * FROM comite_directiva WHERE id_regla = 1")
    tabla = cursor.fetchall()

    if tabla:
        st.markdown("### 🧾 Comité actual")
        df = pd.DataFrame(tabla)
        st.dataframe(df)



# =========================================================
#  3) PERMISOS DE INASISTENCIA
# =========================================================
def gestionar_permisos():

    st.subheader("🆗 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    st.markdown("### ➕ Agregar nuevo permiso")

    descripcion = st.text_input("Descripción del permiso")

    if st.button("Registrar permiso"):

        cursor.execute("""
            INSERT INTO regla_permisos_inasistencia(id_regla, descripcion)
            VALUES(1, %s)
        """, (descripcion,))

        con.commit()
        st.success("Permiso registrado.")
        st.rerun()

    # Mostrar permisos
    cursor.execute("SELECT * FROM regla_permisos_inasistencia WHERE id_regla = 1")
    permisos = cursor.fetchall()

    if permisos:
        st.markdown("### 📋 Permisos registrados")
        df = pd.DataFrame(permisos)
        st.dataframe(df)



# =========================================================
#  4) EXPORTAR A PDF
# =========================================================
def exportar_pdf():

    st.subheader("📄 Exportar todas las reglas en PDF")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo WHERE id_regla = 1")
    reglas = cursor.fetchone()

    cursor.execute("SELECT cargo, nombre_socia FROM comite_directiva WHERE id_regla = 1")
    comite = cursor.fetchall()

    cursor.execute("SELECT descripcion FROM regla_permisos_inasistencia WHERE id_regla = 1")
    permisos = cursor.fetchall()

    filename = "/mnt/data/reglas_grupo.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)

    contenido = []

    contenido.append(Paragraph("<b>Reglas del Grupo</b><br/><br/>", styles["Title"]))

    for clave, valor in reglas.items():
        contenido.append(Paragraph(f"<b>{clave}:</b> {valor}<br/>", styles["Normal"]))

    contenido.append(Paragraph("<br/><b>Comité Directivo</b><br/>", styles["Heading2"]))
    for fila in comite:
        contenido.append(Paragraph(f"{fila['cargo']}: {fila['nombre_socia']}<br/>", styles["Normal"]))

    contenido.append(Paragraph("<br/><b>Permisos válidos</b><br/>", styles["Heading2"]))
    for p in permisos:
        contenido.append(Paragraph(f"- {p['descripcion']}<br/>", styles["Normal"]))

    doc.build(contenido)

    st.success("PDF generado correctamente.")
    st.download_button("📥 Descargar PDF", open(filename, "rb"), file_name="reglas_grupo.pdf")

