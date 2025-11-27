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
# 💵 REGISTRAR PAGO DEL PRÉSTAMO
# ==========================================================
def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ Primero configure las reglas internas.")
        return

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias)
    id_socia = dict_socias[socia_sel]

    cur.execute("""
        SELECT * FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    prestamo = cur.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])

    cur.execute("""
        SELECT *
        FROM Cuotas_prestamo
        WHERE Id_Prestamo=%s AND Estado='pendiente'
        ORDER BY Numero_cuota
    """, (id_prestamo,))
    cuotas = cur.fetchall()

    if not cuotas:
        st.success("🎉 Todas las cuotas están pagadas.")
        return

    opciones = {
        f"Cuota #{c['Numero_cuota']} — {c['Fecha_programada']} — ${c['Monto_cuota']}":
            c["Id_Cuota"]
        for c in cuotas
    }

    cuota_sel = st.selectbox("Cuota a pagar:", opciones.keys())
    id_cuota = opciones[cuota_sel]

    fecha_pago_dt = st.date_input("Fecha del pago:", date.today())
    fecha_pago = fecha_pago_dt.strftime("%Y-%m-%d")

    if st.button("Registrar pago"):

        cur.execute("SELECT * FROM Cuotas_prestamo WHERE Id_Cuota=%s", (id_cuota,))
        cuota = cur.fetchone()
        monto_cuota = Decimal(cuota["Monto_cuota"])

        id_caja = asegurar_reunion(fecha_pago)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago cuota préstamo {id_prestamo}",
            monto=float(monto_cuota)
        )

        cur.execute("""
            UPDATE Cuotas_prestamo
            SET Estado='pagada',
                Fecha_pago=%s,
                Id_Caja=%s
            WHERE Id_Cuota=%s
        """, (fecha_pago, id_caja, id_cuota))

        nuevo_saldo = saldo_pendiente - monto_cuota
        cur.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente`=%s,
                Estado_del_prestamo=CASE WHEN %s=0 THEN 'pagado' ELSE 'activo' END
            WHERE Id_Préstamo=%s
        """, (nuevo_saldo, nuevo_saldo, id_prestamo))

        con.commit()

        st.success("✔ Pago registrado correctamente.")
        st.rerun()
