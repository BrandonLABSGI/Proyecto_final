import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # OBTENER SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {
        f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias
    }

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # ======================================================
    # OBTENER SALDO DE AHORROS (CORREGIDO)
    # ======================================================
    cursor.execute("""
        SELECT `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia = %s
        ORDER BY Id_Ahorro DESC
        LIMIT 1
    """, (id_socia,))
    row_saldo = cursor.fetchone()

    saldo_ahorro = row_saldo["Saldo acumulado"] if row_saldo else 0

    st.info(f"💰 **Ahorro actual de la socia:** ${saldo_ahorro}")

    # ======================================================
    # DATOS DEL PRÉSTAMO
    # ======================================================
    st.markdown("---")
    st.header("📌 Datos del préstamo")

    monto = st.number_input("💵 Monto solicitado", min_value=1.00, step=1.00)
    tasa = st.number_input("📈 Tasa de interés (%)", min_value=0.0, step=0.1)
    cuotas = st.number_input("🔢 Número de cuotas", min_value=1, step=1)

    fecha_prestamo_raw = st.date_input("📅 Fecha del préstamo", date.today())
    fecha_prestamo = fecha_prestamo_raw.strftime("%Y-%m-%d")

    # ======================================================
    # VALIDACIÓN DE AHORROS
    # ======================================================
    if monto > saldo_ahorro * 2:
        st.error("❌ El monto del préstamo no puede ser mayor al doble del ahorro.")
        return

    # ======================================================
    # BOTÓN PARA AUTORIZAR
    # ======================================================
    if st.button("💾 Autorizar préstamo"):

        try:
            # ------------------------------------------------------
            # Crear registro del préstamo
            # ------------------------------------------------------
            cursor.execute("""
                INSERT INTO Prestamo
                (Id_Socia, Monto prestado, Tasa de interes, Fecha del prestamo,
                 Estado_del_prestamo, Saldo pendiente, Cuotas)
                VALUES (%s, %s, %s, %s, 'activo', %s, %s)
            """, (
                id_socia,
                monto,
                tasa,
                fecha_prestamo,
                monto,    # saldo pendiente inicial = monto solicitado
                cuotas
            ))

            # OBTENER ID DEL PRÉSTAMO CREADO
            id_prestamo = cursor.lastrowid

            # ------------------------------------------------------
            # GENERAR CUOTAS AUTOMÁTICAMENTE
            # ------------------------------------------------------
            monto_cuota = round(monto / cuotas, 2)

            for i in range(1, int(cuotas) + 1):
                fecha_cuota = fecha_prestamo_raw + timedelta(days=30 * i)

                cursor.execute("""
                    INSERT INTO Cuotas_prestamo
                    (Id_Prestamo, Numero_cuota, Fecha_programada,
                     Monto_cuota, Estado)
                    VALUES (%s, %s, %s, %s, 'pendiente')
                """, (
                    id_prestamo,
                    i,
                    fecha_cuota.strftime("%Y-%m-%d"),
                    monto_cuota
                ))

            # ------------------------------------------------------
            # REGISTRO EN CAJA (SALIDA DE DINERO)
            # ------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_prestamo)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Egreso",
                categoria=f"Préstamo otorgado a {socia_sel}",
                monto=float(monto)
            )

            con.commit()

            st.success("✔ Préstamo autorizado correctamente.")
            st.success(f"📄 ID del préstamo creado: {id_prestamo}")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al autorizar el préstamo: {e}")
