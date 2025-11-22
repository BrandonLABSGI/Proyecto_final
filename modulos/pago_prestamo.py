import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ PRÉSTAMO ACTIVO
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND LOWER(Estado_del_prestamo)='activo'
    """, (id_socia,))
    prestamo = cursor.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = float(prestamo["Saldo pendiente"])

    st.subheader("📄 Información del préstamo")
    st.write(f"**ID:** {id_prestamo}")
    st.write(f"**Monto prestado:** ${prestamo['Monto prestado']}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")

    # ---------------------------------------------------------
    # 3️⃣ REGISTRO DE PAGO
    # ---------------------------------------------------------
    st.markdown("---")
    fecha_pago = st.date_input("📅 Fecha del pago", value=date.today()).strftime("%Y-%m-%d")
    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.50, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            # 1️⃣ Obtener saldo actual en caja
            cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
            row = cursor.fetchone()
            saldo_actual = row["Saldo_actual"] if row else 0

            nuevo_saldo_caja = saldo_actual + monto_abonado

            # 2️⃣ Registrar ingreso en CAJA
            cursor.execute("""
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s,%s,%s,1,2,%s)
            """, (
                f"Pago de préstamo – Socia {id_socia}",
                monto_abonado,
                nuevo_saldo_caja,
                fecha_pago
            ))

            id_caja = cursor.lastrowid

            # 3️⃣ Calcular nuevo saldo del préstamo
            nuevo_saldo_prestamo = saldo_pendiente - monto_abonado
            if nuevo_saldo_prestamo < 0:
                nuevo_saldo_prestamo = 0

            # 4️⃣ Guardar en Pago_del_prestamo (CORRECTO)
            cursor.execute("""
                INSERT INTO Pago_del_prestamo
                (`Fecha de pago`, `Monto abonado`, `Interés pagado`, `Capital pagado`,
                 `Saldo restante`, `Id_Préstamo`, `Id_Caja`)
                VALUES (%s,%s,0,0,%s,%s,%s)
            """, (
                fecha_pago,
                monto_abonado,
                nuevo_saldo_prestamo,
                id_prestamo,
                id_caja
            ))

            # 5️⃣ Actualizar saldo del préstamo
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s,
                    Estado_del_prestamo = CASE
                        WHEN %s = 0 THEN 'pagado'
                        ELSE 'activo'
                    END
                WHERE Id_Préstamo=%s
            """, (nuevo_saldo_prestamo, nuevo_saldo_prestamo, id_prestamo))

            con.commit()
            st.success("✔ Pago registrado correctamente.")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
