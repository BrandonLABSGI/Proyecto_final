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

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        socia_seleccionada = st.selectbox(
            "👩 Socia que recibe el préstamo", 
            list(lista_socias.keys())
        )
        id_socia = lista_socias[socia_seleccionada]

        monto = st.number_input("💵 Monto prestado ($):", min_value=1, step=1)
        tasa_interes = st.number_input("📈 Tasa de interés (%):", min_value=1, step=1)
        plazo = st.number_input("🗓 Plazo (meses):", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas:", min_value=1)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # ======================================================
        # 🔒 REGLA INTERNA: MÁXIMO PRÉSTAMO = $100.00
        # ======================================================
        limite_regla_interna = 100.00
        if monto > limite_regla_interna:
            st.error(f"❌ No puede solicitar un préstamo mayor a ${limite_regla_interna}.")
            return

        # ======================================================
        # 🔒 INTERÉS MÁXIMO
        # ======================================================
        if tasa_interes > 6:
            st.error("❌ El interés no puede ser mayor al 6%.")
            return

        # ======================================================
        # 🔒 PLAZO MÁXIMO
        # ======================================================
        if plazo > 4:
            st.error("❌ El plazo máximo permitido es 4 meses.")
            return

        # ======================================================
        # VALIDAR AHORRO
        # ======================================================
        cursor.execute("""
            SELECT Saldo_acumulado
            FROM Ahorro
            WHERE Id_Socia=%s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))

        registro_ahorro = cursor.fetchone()
        ahorro_total = float(registro_ahorro["Saldo_acumulado"]) if registro_ahorro else 0.0

        if monto > ahorro_total:
            st.error(f"❌ La socia tiene solo ${ahorro_total}. No puede solicitar ${monto}.")
            return

        # ======================================================
        # OBTENER CAJA / SALDO
        # ======================================================
        id_caja = obtener_o_crear_reunion(str(fecha_prestamo))

        cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
        saldo_actual = float(cursor.fetchone()["saldo_final"])

        if monto > saldo_actual:
            st.error(f"❌ Fondos insuficientes. Saldo disponible: ${saldo_actual}")
            return

        # ======================================================
        # CÁLCULOS
        # ======================================================
        interes_total = round((monto * tasa_interes) / 100, 2)
        total_a_pagar = round(monto + interes_total, 2)
        cuota_individual = round(total_a_pagar / cuotas, 2)

        # ======================================================
        # REGISTRAR PRÉSTAMO
        # ======================================================
        cursor.execute("""
            INSERT INTO Prestamo(
                `Fecha del préstamo`, `Monto prestado`, `Tasa de interes`,
                `Plazo`, `Cuotas`, `Saldo pendiente`, Estado_del_prestamo,
                Id_Grupo, Id_Socia, Id_Caja
            )
            VALUES (%s,%s,%s,%s,%s,%s,'activo',1,%s,%s)
        """,
        (
            fecha_prestamo,
            monto,
            tasa_interes,
            plazo,
            cuotas,
            total_a_pagar,
            id_socia,
            id_caja
        ))

        id_prestamo = cursor.lastrowid

        # ======================================================
        # DESCONTAR AHORRO
        # ======================================================
        nuevo_ahorro = ahorro_total - monto

        cursor.execute("""
            INSERT INTO Ahorro(
                Fecha_del_aporte,
                Monto_del_aporte,
                Tipo_de_aporte,
                Comprobante_digital,
                Saldo_acumulado,
                Id_Socia,
                Id_Reunion,
                Id_Grupo,
                Id_Caja
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            fecha_prestamo,
            -monto,
            "Descuento préstamo",
            "---",
            nuevo_ahorro,
            id_socia,
            id_caja,
            1,
            id_caja
        ))

        # ======================================================
        # REGISTRAR MOVIMIENTO REAL (EGRESO)
        # ======================================================
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Préstamo otorgado a {socia_seleccionada}",
            monto=float(monto)
        )

        # ======================================================
        # REGISTRO DE CUOTAS
        # ======================================================
        fecha_base = datetime.strptime(str(fecha_prestamo), "%Y-%m-%d")

        for n in range(1, cuotas + 1):
            fecha_cuota = fecha_base + timedelta(days=15*n)
            cursor.execute("""
                INSERT INTO Cuotas_prestamo
                (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
                VALUES (%s,%s,%s,%s,'pendiente')
            """,
            (
                id_prestamo,
                n,
                fecha_cuota.strftime("%Y-%m-%d"),
                cuota_individual
            ))

        con.commit()

        st.success("✔ Préstamo autorizado correctamente.")

        # ======================================================
        # RESUMEN
        # ======================================================
        st.markdown("---")
        st.subheader("📄 Resumen del préstamo")
        st.write(f"📅 **Fecha:** {fecha_prestamo}")
        st.write(f"👩 **Socia:** {socia_seleccionada}")
        st.write(f"💵 **Monto prestado:** ${monto}")
        st.write(f"📈 **Interés total:** ${interes_total}")
        st.write(f"💰 **Total a pagar:** ${total_a_pagar}")
        st.write(f"🧾 **Cuotas:** {cuotas} cuotas de ${cuota_individual}")

        st.write("### 🗓 Calendario de cuotas:")
        for n in range(1, cuotas + 1):
            fecha_cuota = fecha_base + timedelta(days=15*n)
            st.write(f"➡ **Cuota {n}:** {fecha_cuota.strftime('%Y-%m-%d')} — ${cuota_individual}")
