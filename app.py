import streamlit as st

from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
# from modulos.administrador import interfaz_admin  # ← LO DESACTIVAMOS PARA EVITAR EL ERROR


# -------------------------------
# ESTADO DE SESIÓN
# -------------------------------

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------

if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    # DIRECTOR
    if rol == "Director":
        interfaz_directiva()

    # PROMOTORA
    elif rol == "Promotora":
        interfaz_promotora()

    # ADMINISTRADOR – dejar mientras no existe el módulo
    elif rol == "Administrador":
        st.title("🛠 Panel del Administrador (en construcción)")
        st.info("Este panel aún no está disponible.")

    else:
        st.error(f"❌ Rol no reconocido: {rol}")
        st.session_state.clear()
        st.rerun()

    # BOTÓN CERRAR SESIÓN
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

else:
    login()
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 GENERACIÓN DE REPORTES
# ---------------------------------------------------------
def pagina_reporte():

    st.header("📄 Reporte general del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1) Seleccionar fecha del reporte
    # ---------------------------------------------------------
    fecha_raw = st.date_input("Seleccione una fecha de reunión para el reporte")
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Buscar reunión
    cursor.execute("""
        SELECT Id_Reunion 
        FROM Reunion
        WHERE Fecha_reunion = %s
    """, (fecha,))
    row = cursor.fetchone()

    if not row:
        st.warning("⚠ No existe una reunión registrada para esa fecha.")
        return

    id_reunion = row[0]

    st.success(f"Reunión encontrada (ID {id_reunion})")

    st.markdown("---")

    # ---------------------------------------------------------
    # 2) Cargar asistencia
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
        ORDER BY S.Id_Socia ASC
    """, (id_reunion,))
    asistencia = cursor.fetchall()

    df_asistencia = pd.DataFrame(asistencia, columns=["Socia", "Asistencia"])

    st.subheader("🧍‍♀️ Asistencia del día")
    st.dataframe(df_asistencia)

    total_presentes = df_asistencia[df_asistencia["Asistencia"] == "Presente"].shape[0]
    st.info(f"👥 Total presentes: {total_presentes}")

    st.markdown("---")

    # ---------------------------------------------------------
    # 3) Cargar ingresos extraordinarios
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT S.Nombre, I.Tipo, I.Descripcion, I.Monto
        FROM IngresosExtra I
        JOIN Socia S ON S.Id_Socia = I.Id_Socia
        WHERE I.Id_Reunion = %s
        ORDER BY I.Id_Ingreso ASC
    """, (id_reunion,))

    ingresos = cursor.fetchall()

    df_ing = pd.DataFrame(ingresos, columns=["Socia", "Tipo", "Descripción", "Monto"])

    st.subheader("💰 Ingresos extraordinarios")
    st.dataframe(df_ing)

    total_ingresos = df_ing["Monto"].sum() if not df_ing.empty else 0
    st.success(f"💵 Total del día: ${total_ingresos:.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # 4) GENERAR PDF
    # ---------------------------------------------------------

    def generar_pdf():
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp.name, pagesize=letter)

        styles = getSampleStyleSheet()
        story = []

        # Título
        story.append(Paragraph(f"Reporte del Grupo - Fecha: {fecha}", styles["Title"]))
        story.append(Paragraph(" ", styles["Normal"]))

        # Tabla de asistencia
        story.append(Paragraph("Asistencia:", styles["Heading2"]))

        tabla_asistencia = [["Socia", "Asistencia"]] + asistencia
        tabla = Table(tabla_asistencia)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.gray),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))
        story.append(tabla)
        story.append(Paragraph(" ", styles["Normal"]))

        # Tabla ingresos
        story.append(Paragraph("Ingresos extraordinarios:", styles["Heading2"]))

        tabla_ing = [["Socia", "Tipo", "Descripción", "Monto"]] + ingresos
        tabla2 = Table(tabla_ing)
        tabla2.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.gray),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))
        story.append(tabla2)

        story.append(Paragraph(f"Total ingresos: ${total_ingresos:.2f}", styles["Heading3"]))

        doc.build(story)

        return temp.name


    st.subheader("📥 Descargar reporte PDF")

    if st.button("📄 Generar PDF"):
        pdf_path = generar_pdf()
        with open(pdf_path, "rb") as pdf:
            st.download_button(
                label="⬇ Descargar reporte en PDF",
                data=pdf,
                file_name=f"Reporte_{fecha}.pdf",
                mime="application/pdf"
            )

