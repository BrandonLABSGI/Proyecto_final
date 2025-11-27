import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion


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
# 💳 AUTORIZAR PRÉSTAMO
# ==========================================================
def autorizar_prestamo():

    st.header("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    monto = st.number_input("Monto del préstamo ($):", min_value=1.00, step=1.00)

    tasa = st.number_input("Tasa de interés (%)", min_value=0.00, value=10.0)

    fecha_dt = st.date_input("Fecha del préstamo:", date.today())
    fecha = fecha_dt.strftime("%Y-%m-%d")

    if st.button("Autorizar préstamo"):

        # Reunión correcta del día
        id_caja = asegurar_reunion(fecha)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Préstamo otorgado — {socia_sel}",
            monto=float(monto)
        )

        cursor.execute("""
            INSERT INTO Prestamo(Monto_prestado, `Saldo pendiente`, `Tasa de interes`,
                                 Estado_del_prestamo, Id_Socia, Fecha_entrega, Id_Caja)
            VALUES(%s,%s,%s,'activo',%s,%s,%s)
        """, (monto, monto, tasa, id_socia, fecha, id_caja))

        con.commit()

        st.success("✔ Préstamo autorizado correctamente.")
        st.rerun()
