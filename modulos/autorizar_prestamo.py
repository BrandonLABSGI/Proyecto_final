import streamlit as st
from modulos.conexion import obtener_conexion
from datetime import date
import pandas as pd

def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ======================================================
    # OBTENER SOCIAS (ORDEN POR ID)
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{id_} - {nombre}": id_ for (id_, nombre) in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        nombre_socia = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[nombre_socia]

        monto = st.number_input("💵 Monto solicitado", min_value=1, step=1)
        tasa_interes = st.number_input("📈 Tasa de interés (%)", min_value=1, step=1)
        plazo = st.number_input("🗓 Plazo (meses)", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas", min_value=1)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # --------------------------------------------------
        # 1. VERIFICAR SALDO DE CAJA
        # --------------------------------------------------
        cursor.execute("SELECT Id_Caja, Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        caja = cursor.fetchone()

        if not caja:
            st.error("❌ No existe caja activa.")
            return

        id_caja, saldo_actual = caja

        if monto > saldo_actual:
            st.error(f"❌ Fondos insuficientes. Saldo disponible: ${saldo_actual}")
            return

        saldo_pendiente = monto

        try:
            # --------------------------------------------------
            # 2. REGISTRAR PRÉSTAMO
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`,
                    `Monto prestado`,
                    `Tasa de interes`,
                    `Plazo`,
                    `Cuotas`,
                    `Saldo pendiente`,
                    `Estado del préstamo`,
                    Id_Grupo,
                    Id_Socia,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                1,          # Id_Grupo
                id_socia,   # Id_Socia
                id_caja     # Id_Caja
            ))

            # --------------------------------------------------
            # 3. REGISTRAR EGRESO EN CAJA
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,
            (
                f"Préstamo otorgado a: {nombre_socia}",
                -monto,
                saldo_actual - monto,
                1,
                3
            ))

            con.commit()

            # ======================================================
            # 4. MOSTRAR RESUMEN DEL PRÉSTAMO
            # ======================================================

            interes_total = monto * (tasa_interes/100)
            total_a_pagar = monto + interes_total
            pago_por_cuota = total_a_pagar / cuotas

            st.success("✅ Préstamo autorizado correctamente.")
            st.info(f"Nuevo saldo en caja: **${saldo_actual - monto}**")

            # ---------- TABLA RESUMEN ----------
            resumen = pd.DataFrame({
                "Campo": [
                    "ID Socia", "Nombre",
                    "Monto prestado", "Tasa de interés",
                    "Plazo (meses)", "Cuotas",
                    "Interés total", "Total a pagar",
                    "Pago por cuota", "Fecha del préstamo"
                ],
                "Valor": [
                    id_socia,
                    nombre_socia.split(" - ", 1)[1],
                    f"${monto}",
                    f"{tasa_interes}%",
                    f"{plazo}",
                    f"{cuotas}",
                    f"${interes_total:.2f}",
                    f"${total_a_pagar:.2f}",
                    f"${pago_por_cuota:.2f}",
                    fecha_prestamo
                ]
            })

            st.table(resumen)

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")
