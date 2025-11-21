import streamlit as st
import mysql.connector
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from modulos.conexion import obtener_conexion


# ===========================================================
# PANTALLA PRINCIPAL DE REGLAS INTERNAS
# ===========================================================
def gestionar_reglas():
    st.title("📘 Reglas internas del grupo")

    opcion = st.radio(
        "Seleccione una sección:",
        [
            "Editor de reglas internas",
            "Comité directivo",
            "Permisos válidos de inasistencia",
            "Exportar reglas en PDF"
        ]
    )

    if opcion == "Editor de reglas internas":
        mostrar_reglas()

    elif opcion == "Comité directivo":
        mostrar_comite()

    elif opcion == "Permisos válidos de inasistencia":
        mostrar_permisos()

    elif opcion == "Exportar reglas en PDF":
        exportar_pdf()



# ===========================================================
# SECCIÓN 1: REGLAS DEL GRUPO
# Tabla: reglas_grupo
# ===========================================================
def mostrar_reglas():

    st.subheader("📖 Editor de reglas internas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    nueva = st.text_input("Agregar nueva regla:")

    if st.button("➕ Añadir regla"):
        if nueva.strip() != "":
            cursor.execute("""
                INSERT INTO reglas_grupo (descripcion, id_grupo)
                VALUES (%s, 1)
            """, (nueva,))
            con.commit()
            st.success("Regla agregada correctamente.")
            st.rerun()

    cursor.execute("SELECT id_regla, descripcion FROM reglas_grupo ORDER BY id_regla ASC")
    reglas = cursor.fetchall()

    st.markdown("### 📋 Lista de reglas")
    for r in reglas:
        col1, col2, col3 = st.columns([7, 1, 1])
        col1.write(r["descripcion"])

        if col2.button("✏️", key=f"edit_r{r['id_regla']}"):
            editar_regla(r["id_regla"], r["descripcion"])
            st.rerun()

        if col3.button("🗑️", key=f"del_r{r['id_regla']}"):
            cursor.execute("DELETE FROM reglas_grupo WHERE id_regla=%s", (r["id_regla"],))
            con.commit()
            st.success("Regla eliminada.")
            st.rerun()

    cursor.close()
    con.close()



# ===========================================================
# Editar regla interna
# ===========================================================
def editar_regla(id_regla, texto_actual):
    st.markdown("### ✏️ Editar regla")
    nuevo = st.text_area("Nueva descripción:", texto_actual)

    if st.button("💾 Guardar cambios", key=f"save_edit_{id_regla}"):
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            UPDATE reglas_grupo 
            SET descripcion=%s
            WHERE id_regla=%s
        """, (nuevo, id_regla))
        con.commit()
        cursor.close()
        con.close()
        st.success("Regla actualizada.")
        st.rerun()



# ===========================================================
# SECCIÓN 2: COMITÉ DIRECTIVO
# Tabla: comite_directiva
# ===========================================================
def mostrar_comite():
    st.subheader("👥 Comité directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    st.markdown("### Registrar nuevo miembro")

    cargo = st.text_input("Cargo")
    nombre = st.text_input("Nombre de la socia")

    if st.button("➕ Registrar miembro"):
        cursor.execute("""
            INSERT INTO comite_directiva (id_regla, cargo, nombre_socia)
            VALUES (1, %s, %s)
        """, (cargo, nombre))
        con.commit()
        st.success("Miembro registrado.")
        st.rerun()

    cursor.execute("""
        SELECT id_comite, cargo, nombre_socia 
        FROM comite_directiva 
        ORDER BY id_comite ASC
    """)
    miembros = cursor.fetchall()

    st.markdown("### 📋 Miembros del comité")
    for m in miembros:
        col1, col2, col3 = st.columns([5, 3, 1])
        col1.write(f"**{m['cargo']}**")
        col2.write(m["nombre_socia"])

        if col3.button("❌", key=f"del_c{m['id_comite']}"):
            cursor.execute("DELETE FROM comite_directiva WHERE id_comite=%s", (m["id_comite"],))
            con.commit()
            st.success("Miembro eliminado.")
            st.rerun()

    cursor.close()
    con.close()



# ===========================================================
# SECCIÓN 3: PERMISOS VÁLIDOS DE INASISTENCIA
# Tabla: regla_permisos_inasistencia
# ===========================================================
def mostrar_permisos():

    st.subheader("📝 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    permiso = st.text_input("Agregar nuevo permiso")

    if st.button("➕ Registrar permiso"):
        cursor.execute("""
            INSERT INTO regla_permisos_inasistencia (id_regla, descripcion)
            VALUES (1, %s)
        """, (permiso,))
        con.commit()
        st.success("Permiso registrado.")
        st.rerun()

    cursor.execute("""
        SELECT id_permiso, descripcion
        FROM regla_permisos_inasistencia
        ORDER BY id_permiso ASC
    """)
    lista = cursor.fetchall()

    st.markdown("### 📋 Lista de permisos")
    for p in lista:
        col1, col2 = st.columns([8, 1])
        col1.write(p["descripcion"])

        if col2.button("🗑️", key=f"del_p{p['id_permiso']}"):
            cursor.execute("DELETE FROM regla_permisos_inasistencia WHERE id_permiso=%s", (p["id_permiso"],))
            con.commit()
            st.success("Permiso eliminado.")
            st.rerun()

    cursor.close()
    con.close()



# ===========================================================
# SECCIÓN 4: EXPORTAR PDF (FUNCIONA EN STREAMLIT CLOUD)
# ===========================================================
def exportar_pdf():

    st.subheader("📄 Exportar todas las reglas en PDF")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT descripcion FROM reglas_grupo ORDER BY id_regla ASC")
    reglas = cursor.fetchall()

    cursor.close()
    con.close()

    if not reglas:
        st.warning("No hay reglas para exportar.")
        return

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    contenido = []

    contenido.append(Paragraph("<b>REGLAS INTERNAS DEL GRUPO</b>", styles["Title"]))
    contenido.append(Paragraph("<br/><br/>", styles["Normal"]))

    for r in reglas:
        contenido.append(Paragraph(f"• {r[0]}", styles["Normal"]))

    doc.build(contenido)

    buffer.seek(0)

    st.success("PDF generado correctamente.")

    st.download_button(
        label="📥 Descargar PDF",
        data=buffer,
        file_name="Reglas_internas.pdf",
        mime="application/pdf"
    )


