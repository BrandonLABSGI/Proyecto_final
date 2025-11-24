import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ============================================================
# OBTENER ID EMPLEADO (PROMOTORA)
# ============================================================
def obtener_id_promotora():
    """Retorna el Id_Empleado de la promotora logueada."""
    usuario = st.session_state.get("usuario", "")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Empleado 
        FROM Empleado 
        WHERE Usuario = %s AND Rol = 'Promotora'
    """, (usuario,))

    row = cursor.fetchone()

    cursor.close()
    con.close()

    return row["Id_Empleado"] if row else None



# ============================================================
# PANEL PRINCIPAL PROMOTORA — MENÚ HORIZONTAL NUEVO
# ============================================================
def interfaz_promotora():

    st.title("👩‍🦰 Panel de Promotora — Solidaridad CVX")

    # VALIDAR USUARIO
    id_promotora = obtener_id_promotora()
    if not id_promotora:
        st.error("⚠ No se pudo validar la promotora. Verifica el usuario.")
        return

    # --------- MENÚ HORIZONTAL ---------
    tabs = st.tabs([
        "➕ Crear grupo",
        "📋 Ver grupos",
        "✏️ Editar grupo",
        "🗑️ Eliminar grupo"
    ])

    # ========== OPCIÓN 1: CREAR GRUPO ==========
    with tabs[0]:
        st.subheader("➕ Crear Grupo Nuevo")
        crear_grupo(id_promotora)

    # ========== OPCIÓN 2: VER GRUPOS ==========
    with tabs[1]:
        st.subheader("📋 Grupos Asignados")
        ver_grupos(id_promotora)

    # ========== OPCIÓN 3: EDITAR GRUPO ==========
    with tabs[2]:
        st.subheader("✏️ Editar Grupo")
        editar_grupo(id_promotora)

    # ========== OPCIÓN 4: ELIMINAR GRUPO ==========
    with tabs[3]:
        st.subheader("🗑️ Eliminar Grupo")
        eliminar_grupo(id_promotora)



# ============================================================
# CREAR GRUPO — CONTENIDO COMPLETO
# ============================================================
def crear_grupo(id_promotora):

    nombre = st.text_input("Nombre del grupo")
    tasa = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
    periodicidad = st.number_input("Periodicidad de reuniones (días)", min_value=1, step=1)
    tipo_multa = st.text_input("Tipo de multa")
    reglas = st.text_area("Reglas del préstamo")
    fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
    distrito = st.number_input("ID del distrito", min_value=1, step=1)

    if st.button("Crear grupo", type="primary"):
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO Grupo(
                Nombre_grupo, Tasa_de_interes, Periodicidad_de_reuniones,
                Tipo_de_multa, Reglas_de_prestamo, fecha_inicio,
                Id_Promotora, Id_Distrito
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            nombre, tasa, periodicidad, tipo_multa,
            reglas, fecha_inicio, id_promotora, distrito
        ))

        con.commit()
        cursor.close()
        con.close()

        st.success("✅ Grupo creado correctamente.")
        st.rerun()



# ============================================================
# VER GRUPOS
# ============================================================
def ver_grupos(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * 
        FROM Grupo
        WHERE Id_Promotora = %s
        ORDER BY Id_Grupo DESC
    """, (id_promotora,))

    grupos = cursor.fetchall()

    cursor.close()
    con.close()

    if not grupos:
        st.info("No tienes grupos creados todavía.")
        return

    df = pd.DataFrame(grupos)
    st.dataframe(df, hide_index=True)



# ============================================================
# EDITAR GRUPO
# ============================================================
def editar_grupo(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))

    lista = cursor.fetchall()

    if not lista:
        st.warning("No tienes grupos para editar.")
        return

    opciones = {g["Nombre_grupo"]: g["Id_Grupo"] for g in lista}
    sel = st.selectbox("Selecciona un grupo:", opciones.keys())
    id_grupo = opciones[sel]

    cursor.execute("SELECT * FROM Grupo WHERE Id_Grupo=%s", (id_grupo,))
    grupo = cursor.fetchone()

    nombre = st.text_input("Nombre", grupo["Nombre_grupo"])
    tasa = st.number_input("Tasa", value=float(grupo["Tasa_de_interes"]))
    periodicidad = st.number_input("Periodicidad", value=grupo["Periodicidad_de_reuniones"])
    tipo_multa = st.text_input("Tipo de multa", grupo["Tipo_de_multa"])
    reglas = st.text_area("Reglas", grupo["Reglas_de_prestamo"])
    distrito = st.number_input("Distrito", value=grupo["Id_Distrito"])

    if st.button("Actualizar grupo", type="primary"):
        cursor.execute("""
            UPDATE Grupo
            SET Nombre_grupo=%s, Tasa_de_interes=%s, Periodicidad_de_reuniones=%s,
                Tipo_de_multa=%s, Reglas_de_prestamo=%s, Id_Distrito=%s
            WHERE Id_Grupo=%s
        """, (nombre, tasa, periodicidad, tipo_multa, reglas, distrito, id_grupo))

        con.commit()
        st.success("Grupo actualizado correctamente.")
        st.rerun()

    cursor.close()
    con.close()



# ============================================================
# ELIMINAR GRUPO
# ============================================================
def eliminar_grupo(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora=%s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos para eliminar.")
        return

    opciones = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}
    sel = st.selectbox("Seleccione el grupo a eliminar:", opciones.keys())
    id_eliminar = opciones[sel]

    if st.button("Eliminar definitivamente", type="primary"):
        cursor.execute("DELETE FROM Grupo WHERE Id_Grupo=%s", (id_eliminar,))
        con.commit()

        st.error("❌ Grupo eliminado permanentemente.")
        st.rerun()

    cursor.close()
    con.close()
