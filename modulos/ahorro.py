import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion
from modulos.reglas_utils import obtener_reglas


# ==========================================================
# 🔐 FUNCION CENTRAL → EVITA CREAR REUNIÓN PREMATURA
# ==========================================================
def asegurar_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT id_caja FROM caja_reunion WHERE fecha=%s", (fecha,))
    row = cursor.fetchone()
    if row:
        return row["id_caja"]
    return obtener_o_crear_reunion(fecha)


# ==========================================================
# 💰 REGISTRAR AHORRO
# ==========================================================
def ahorro():

    st.header("💰 Registrar ahorro")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    if not socias:
        st.warning("No hay socias registradas.")
        return

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia = st.selectbox("Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia]

    monto_raw = st.number_input("Monto del ahorro ($):", min_value=0.01, step=0.01)
    monto = Decimal(str(monto_raw))

    fecha_dt = st.date_input("Fecha del aporte:", date.today())
    fecha = fecha_dt.strftime("%Y-%m-%d")

    if st.button("Registrar ahorro"):

        id_caja = asegurar_reunion(fecha)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Ahorro — {socia}",
            monto=float(monto)
        )

        cur.execute("""
            INSERT INTO Ahorro(Id_Socia, Fecha, Monto, Id_Caja)
            VALUES(%s, %s, %s, %s)
        """, (id_socia, fecha, monto, id_caja))

        con.commit()

        st.success("Ahorro registrado correctamente.")
        st.rerun()
