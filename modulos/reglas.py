import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from modulos.reglas_utils import obtener_reglas, guardar_reglas
from modulos.conexion import obtener_conexion


# ============================================================
# PANEL PRINCIPAL DE REGLAS INTERNAS
# ============================================================
def gestionar_reglas():

    st.title("📘 Reglas internas del grupo")

    seccion = st.radio(
        "Seleccione una sección:",
        ["Editor de reglas internas", "Comité directivo", "Exportar PDF"]
    )

    if seccion == "Editor de reglas internas":
        editar_reglamento()

    elif seccion == "Comité directivo":
        modulo_comite()

    elif seccion == "Exportar PDF":
        exportar_pdf()


# ============================================================
# EDITOR DEL REGLAMENTO PRINCIPAL
# ============================================================
def editar_reglamento():

    st.subheader("📝 Editor general del reglamento")

    reglas = obtener_reglas()

    if not reglas:
        st.warning("⚠ No existen reglas registradas aún.")
        st.info("Complete el siguiente formulario para crear las reglas iniciales.")
    else:
        st.success("✔ Reglas cargadas correctamente.")

    # ------------------------------------------------------------
    # FORMULARIO — Valores por defecto
    # ------------------------------------------------------------

    nombre_grupo = st.text_input(
        "Nombre del grupo",
        value=reglas["nombre_grupo"] if reglas else ""
    )

    nombre_comunidad = st.text_input(
        "Nombre de la comunidad",
        value=reglas["nombre_comunidad"] if reglas else ""
    )

    fecha_formacion = st.date_input(
        "Fecha de formación del grupo",
        value=reglas["fecha_formacion"] if reglas and reglas["fecha_formacion"] else date.today()
    )

    multa_inasistencia = st.number_input(
        "Multa por inasistencia ($)",
        min_value=0.00,
        step=0.25,
        value=float(reglas["multa_inasistencia"]) if reglas else 0.25
    )

    multa_mora = st.number_input(
        "Multa por mora de préstamo ($)",
        min_value=0.00,
        step=0.25,
        value=float(reglas["multa_mora"]) if reglas else 0.25
    )

    ahorro_minimo = st.number_input(
        "Ahorro mínimo semanal ($)",
        min_value=0.00,
        step=0.25,
        value=float(reglas["ahorro_minimo"]) if reglas else 0.25
    )

    interes_por_10 = st.number_input(
        "Interés por cada $10 prestados (% mensual)",
        min_value=0,
        step=1,
        value=int(reglas["interes_por_10"]) if reglas else 10
    )

    prestamo_maximo = st.number_input(
        "Monto máximo de préstamo ($)",
        min_value=0.00,
        step=1.0,
        value=float(reglas["prestamo_maximo"]) if reglas else 100
    )

    plazo_maximo = st.number_input(
        "Plazo máximo de préstamo (semanas)",
        min_value=1,
        step=1,
        value=int(reglas["plazo_maximo"]) if reglas else 4
    )

    ciclo_inicio = st.date_input(
        "Fecha de inicio del ciclo",
        value=reglas["ciclo_inicio"] if reglas and reglas["ciclo_inicio"] else date.today()
    )

    ciclo_fin = st.date_input(
        "Fecha de fin del ciclo",
        value=reglas["ciclo_fin"] if reglas and reglas["ciclo_fin"] else date.today()
    )

    meta_social = st.text_area(
        "Meta social / comunitaria",
        value=reglas["meta_social"] if reglas else ""
    )

    otras_reglas = st.text_area(
        "Otras reglas generales",
        value=reglas["otras_reglas"] if reglas else ""
    )

    permisos_inasistencia = st.text_area(
        "Condiciones válidas para permisos de inasistencia",
        value=reglas["permisos_inasistencia"] if reglas else ""
    )

    # ------------------------------------------------------------
    # BOTÓN PARA GUARDAR
    # ------------------------------------------------------------

    if st.button("💾 Guardar reglas"):

        guardar_reglas(
            nombre_grupo=nombre_grupo,
            nombre_comunidad=nombre_comunidad,
            fecha_formacion=fecha_formacion,
            multa_inasistencia=multa_inasistencia,
            ahorro_minimo=ahorro_minimo,
            interes_por_10=interes_por_10,
            prestamo_maximo=prestamo_maximo,
            plazo_maximo=plazo_maximo,
            ciclo_inicio=ciclo_inicio,
            ciclo_fin=ciclo_fin,
            meta_social=meta_social,
            otras_reglas=otras_reglas,
            permisos_inasistencia=permisos_inasistencia,
            multa_mora=multa_mora,
            Id_Grupo=1
        )

        st.success("✔ Reglas internas actualizadas correctamente.")
        st.rerun()


# ============================================================
# COMITÉ DIRECTIVO
# ============================================================
def modulo_comite():

    st.subheader("🧑‍💼 Comité directivo del grupo")

    reglas = obtener_reglas()
    datos_previos = reglas["otras_reglas"] if reglas else ""

    st.info("Complete la información del comité directivo.")

    presidente = st.text_input("Presidente", "")
    secretaria = st.text_input("Secretaria", "")
    tesorera = st.text_input("Tesorera", "")
    vocales = st.text_area("Vocales (opcional)")

    if st.button("💾 Guardar comité"):

        texto_comite = (
            f"Presidente: {presidente}\n"
            f"Secretaria: {secretaria}\n"
            f"Tesorera: {tesorera}\n"
            f"Vocales: {vocales}\n\n"
            f"--- Reglas previas ---\n{datos_previos}"
        )

        guardar_reglas(
            nombre_grupo=reglas["nombre_grupo"],
            nombre_comunidad=reglas["nombre_comunidad"],
            fecha_formacion=reglas["fecha_formacion"],
            multa_inasistencia=reglas["multa_inasistencia"],
            ahorro_minimo=reglas["ahorro_minimo"],
            interes_por_10=reglas["interes_por_10"],
            prestamo_maximo=reglas["prestamo_maximo"],
            plazo_maximo=reglas["plazo_maximo"],
            ciclo_inicio=reglas["ciclo_inicio"],
            ciclo_fin=reglas["ciclo_fin"],
            meta_social=reglas["meta_social"],
            otras_reglas=texto_comite,
            permisos_inasistencia=reglas["permisos_inasistencia"],
            multa_mora=reglas["multa_mora"],
            Id_Grupo=1
        )

        st.success("✔ Comité directivo guardado correctamente.")
        st.rerun()


# ============================================================
# EXPORTAR PDF
# ============================================================
def exportar_pdf():

    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No hay reglas para exportar.")
        return

    st.subheader("📄 Exportar reglas en PDF")

    if st.button("📥 Descargar PDF"):

        styles = getSampleStyleSheet()
        pdf_path = "reglas_cvx.pdf"

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []

        story.append(Paragraph("<b>Reglamento del Grupo</b>", styles["Title"]))
        story.append(Spacer(1, 20))

        for k, v in reglas.items():
            story.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
            story.append(Spacer(1, 12))

        doc.build(story)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name="reglas_cvx.pdf",
                mime="application/pdf"
            )
