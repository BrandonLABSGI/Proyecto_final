import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#     REGISTRO DE AHORROS — SISTEMA CVX
# ============================================================
def ahorro():

    st.header("💰 Registro de Ahorros")

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
    # 2️⃣ HISTORIAL DE APORTES
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
                **ID:** {ap['Id_Ahorro']}  
                **Fecha:** {ap['Fecha del aporte']}  
                **Monto:** ${ap['Monto del aporte']}  
                **Tipo:** {ap['Tipo de aporte']}  
                **Comprobante:** {ap['Comprobante digital']}  
                **Saldo acumulado:** ${ap['Saldo acumulado']}  
            """)
    else:
        st.info("Esta socia aún no tiene aportes registrados.")

    # ---------------------------------------------------------
    # 3️⃣ NUEVO APORTE
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("🧾 Registrar nuevo aporte")

    fecha_aporte_raw = st.date_input("📅 Fecha del aporte", value=date.today())
    fecha_aporte = fecha_aporte_raw.strftime("%Y-%m-%d")

    monto = st.number_input("💵 Monto del aporte ($)", min_value=1.00, step=1.00)
    tipo = st.selectbox("📌 Tipo de aporte", ["Ordinario", "Extraordinario"])
    comprobante = st.text_input("📎 Comprobante digital (opcional)")

    if st.button("💾 Registrar aporte"):

        try:
            # ---------------------------------------------------------
            # 4️⃣ OBTENER SALDO ANTERIOR (CORRECTO)
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT `Saldo acumulado`
                FROM Ahorro
                WHERE Id_Socia = %s
                ORDER BY Id_Ahorro DESC
                LIMIT 1
            """, (id_socia,))
            
            row = cursor.fetchone()
            saldo_anterior = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

            nuevo_saldo = saldo_anterior + Decimal(monto)

            # ---------------------------------------------------------
            # 5️⃣ INSERTAR EN TABLA AHORRO
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Ahorro
                (`Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
                 `Comprobante digital`, `Saldo acumulado`, Id_Socia, Id_Reunión, Id_Grupo, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s, NULL, 1, NULL)
            """, (
                fecha_aporte,
                monto,
                tipo,
                comprobante if comprobante else "---",
                nuevo_saldo,
                id_socia
            ))

            # ---------------------------------------------------------
            # 6️⃣ REGISTRAR INGRESO EN CAJA ÚNICA
            # ---------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_aporte)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Ahorro — {socia_sel}",
                monto=monto
            )

            con.commit()
            st.success("✔ Aporte registrado y agregado a caja correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar aporte: {e}")
