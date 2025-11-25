import streamlit as st
from datetime import date
import pandas as pd

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento


# ============================================================
# ⚠️ MÓDULO INDEPENDIENTE DE MULTAS
# ============================================================
def modulo_multas():

    st.title("⚠️ Administración de Multas")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ----------------------------------------------------------
    # LISTA DE SOCIAS
    # ----------------------------------------------------------
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    dict_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ----------------------------------------------------------
    # TIPOS DE MULTA
    # ----------------------------------------------------------
    cur.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM tipo_de_multa")
    tipos = cur.fetchall()
    dict_tipos = {t["Tipo_de_multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    # ----------------------------------------------------------
    # DETALLES DE MULTA
    # ----------------------------------------------------------
    monto = st.number_input("Monto ($):", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    # ----------------------------------------------------------
    # REGISTRAR MULTA
    # ----------------------------------------------------------
    if st.button("💾 Registrar multa"):

        cur.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo, id_socia))

        con.commit()
        st.success("Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Multas registradas")

    # ----------------------------------------------------------
    # FILTROS
    # ----------------------------------------------------------
    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(dict_socias.keys()))
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])

    query = """
        SELECT M.Id_Multa, S.Nombre AS Socia, T.Tipo_de_multa,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN tipo_de_multa T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1 = 1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre = %s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado = %s"
        params.append(filtro_estado)

    query += " ORDER BY M.Id_Multa DESC"

    cur.execute(query, params)
    multas = cur.fetchall()

    # ----------------------------------------------------------
    # MOSTRAR Y ACTUALIZAR MULTAS
    # ----------------------------------------------------------
    for m in multas:

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 3, 2, 2, 2, 2])

        col1.write(m["Id_Multa"])
        col2.write(m["Socia"])
        col3.write(m["Tipo_de_multa"])
        col4.write(f"${m['Monto']:.2f}")

        nuevo_estado = col5.selectbox(
            " ",
            ["A pagar", "Pagada"],
            index=0 if m["Estado"] == "A pagar" else 1,
            key=f"multa_ind_{m['Id_Multa']}"
        )

        col6.write(str(m["Fecha_aplicacion"]))

        if col7.button("Actualizar", key=f"up_ind_{m['Id_Multa']}"):
            
            estado_anterior = m["Estado"]

            # Si pasa de "A pagar" a "Pagada" → sumar a caja
            if estado_anterior == "A pagar" and nuevo_estado == "Pagada":

                cur.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (m["Fecha_aplicacion"],))
                reunion = cur.fetchone()

                if reunion:
                    id_caja = reunion["id_caja"]

                    registrar_movimiento(
                        id_caja=id_caja,
                        tipo="Ingreso",
                        categoria=f"Pago multa ({m['Socia']})",
                        monto=float(m["Monto"])
                    )

            # Actualizar estado
            cur.execute("""
                UPDATE Multa
                SET Estado = %s
                WHERE Id_Multa = %s
            """, (nuevo_estado, m["Id_Multa"]))

            con.commit()
            st.success("Multa actualizada correctamente.")
            st.rerun()
