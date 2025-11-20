import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


def ahorro():

    st.header("💰 Registro de Ahorros")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ MOSTRAR ÚLTIMOS APORTES
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT 
            Id_Ahorro,
            `Fecha del aporte`,
            `Monto del aporte`,
            `Tipo de aporte`,
            `Comprobante digital`,
            `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia = %s
        ORDER BY Id_Ahorro DESC
    """, (id_socia,))

    aportes = cursor.fetchall()

    st.subheader("📄 Historial de aportes")
    if aportes:
        for ap in aportes:
            st.write(f"""
                **ID:** {ap[0]}  
                **Fecha:** {ap[1]}  
                **Monto:** ${ap[2]}  
                **Tipo:** {ap[3]}  
                **Comprobante:** {ap[4]}  
                **Saldo acumulado:** ${ap[5]}  
            """)
    else:
        st.info("Esta socia aún no tiene aportes registrados.")

    # ---------------------------------------------------------
    # 3️⃣ FORMULARIO DE NUEVO APORTE
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("🧾 Registrar nuevo aporte")

    fecha_aporte = st.date_input("📅 Fecha del aporte", value=date.today())
    monto = st.number_input("💵 Monto del aporte ($)", min_value=1, step=1)
    tipo = st.selectbox("📌 Tipo de aporte", ["Ordinario", "Extraordinario"])
    comprobante = st.text_input("📎 Comprobante digital (nombre de archivo o código)")

    if st.button("💾 Registrar aporte"):

        try:
            # Obtener saldo anterior
            cursor.execute("""
                SELECT `Saldo acumulado`
                FROM Ahorro
                WHERE Id_Socia = %s
                ORDER BY Id_Ahorro DESC
                LIMIT 1
            """, (id_socia,))
            row = cursor.fetchone()
            saldo_anterior = row[0] if row else 0

            nuevo_saldo = saldo_anterior + monto

            # Insertar aporte en Ahorro
            cursor.execute("""
                INSERT INTO Ahorro
                (`Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
                 `Comprobante digital`, `Saldo acumulado`, Id_Socia, Id_Reunión, Id_Grupo, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s, 1, 1, 1)
            """, (
                fecha_aporte.strftime("%Y-%m-%d"),
                monto,
                tipo,
                comprobante,
                nuevo_saldo,
                id_socia
            ))

            # Registrar en Caja
            cursor.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            saldo_caja = row[0] if row else 0

            nuevo_saldo_caja = saldo_caja + monto

            cursor.execute("""
                INSERT INTO Caja
                (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, 1, 2, CURRENT_DATE())
            """, (f"Ahorro – Socia {id_socia}", monto, nuevo_saldo_caja))

            con.commit()
            st.success("Aporte registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar aporte: {e}")
