import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#  PAGO DE PRÉSTAMO — SISTEMA CVX
# ============================================================
def pago_prestamo():

    st.title("💰 Registrar pago de préstamo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ***************************************************************************
    # 1) SOCIA
    # ***************************************************************************
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("No hay socias registradas.")
        return

    opciones = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("👩 Seleccione una socia", list(opciones.keys()))
    id_socia = opciones[socia_sel]

    # ***************************************************************************
    # 2) OBTENER PRÉSTAMO ACTIVO
    # ***************************************************************************
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    prestamo = cursor.fetchone()

    if not prestamo:
        st.info("ℹ La socia no tiene ningún préstamo activo.")
        return

    # Datos del préstamo
    id_prestamo = prestamo["Id_Préstamo"]
    monto = prestamo["Monto prestado"]
    interes_total = prestamo["Interes_total"]
    cuotas = prestamo["Cuotas"]
    saldo_pendiente = float(prestamo["Saldo pendiente"])

    total_a_pagar = monto + interes_total
    cuota_fija = round(total_a_pagar / cuotas, 2)
    interes_por_cuota = round(interes_total / cuotas, 2)

    # ***************************************************************************
    # 3) MOSTRAR DETALLE DEL PRÉSTAMO
    # ***************************************************************************
    st.subheader("📄 Detalle del préstamo")

    detalle = {
        "ID Préstamo": id_prestamo,
        "Monto prestado": f"${monto:.2f}",
        "Interés total": f"${interes_total:.2f}",
        "Total a pagar": f"${total_a_pagar:.2f}",
        "Cuotas quincenales": cuotas,
        "Cuota por pago": f"${cuota_fija:.2f}",
        "Interés por cuota": f"${interes_por_cuota:.2f}",
        "Saldo pendiente actual": f"${saldo_pendiente:.2f}"
    }

    st.table(pd.DataFrame(detalle.items(), columns=["Detalle", "Valor"]))

    # ***************************************************************************
    # 4) FORMULARIO DE PAGO
    # ***************************************************************************
    fecha_pago_raw = st.date_input("📅 Fecha del pago", date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    if st.button("💵 Registrar pago"):

        # 1) CALCULAR CAPITAL PAGADO
        capital_pagado = round(cuota_fija - interes_por_cuota, 2)

        # 2) NUEVO SALDO
        nuevo_saldo = round(saldo_pendiente - cuota_fija, 2)
        if nuevo_saldo < 0:
            nuevo_saldo = 0

        # ***************************************************************************
        # 3) REGISTRAR INGRESO EN CAJA
        # ***************************************************************************
        id_caja = obtener_o_crear_reunion(fecha_pago)

        registrar_movimiento(
            id_caja,
            "Ingreso",
            f"Pago préstamo – {socia_sel}",
            float(cuota_fija)
        )

        # ***************************************************************************
        # 4) REGISTRAR EN TABLA Pago_del_prestamo
        # ***************************************************************************
        cursor.execute("""
            INSERT INTO Pago_del_prestamo(
                `Fecha_de_pago`,
                `Monto_abonado`,
                `Interes_pagado`,
                `Capital_pagado`,
                `Saldo_restante`,
                `Id_Prestamo`,
                `Id_Caja`
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            fecha_pago,
            cuota_fija,
            interes_por_cuota,
            capital_pagado,
            nuevo_saldo,
            id_prestamo,
            id_caja
        ))

        # ***************************************************************************
        # 5) ACTUALIZAR PRÉSTAMO
        # ***************************************************************************
        if nuevo_saldo == 0:
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=0,
                    Estado_del_prestamo='pagado'
                WHERE Id_Préstamo=%s
            """, (id_prestamo,))
        else:
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s
                WHERE Id_Préstamo=%s
            """, (nuevo_saldo, id_prestamo))

        con.commit()

        st.success("✔ Pago registrado correctamente.")
        st.info(f"💵 Nuevo saldo pendiente: **${nuevo_saldo:.2f}**")
        st.rerun()

    # ***************************************************************************
    # 6) HISTORIAL DE PAGOS — CORREGIDO 100%
    # ***************************************************************************
    st.subheader("📜 Historial de pagos")

    # LIMPIA RESULTADOS PENDIENTES (EVITA EL ERROR)
    try:
        cursor.fetchall()
    except:
        pass

    cursor.execute("""
        SELECT *
        FROM Pago_del_prestamo
        WHERE Id_Prestamo=%s
        ORDER BY Id_Pago ASC
    """, (id_prestamo,))

    pagos = cursor.fetchall()

    if pagos:
        df = pd.DataFrame(pagos)
        st.dataframe(df, hide_index=True)
    else:
        st.info("La socia aún no tiene pagos registrados.")

    cursor.close()
    con.close()
