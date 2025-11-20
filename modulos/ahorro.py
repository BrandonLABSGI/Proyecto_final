import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

def ahorro():

    st.header("🏦 Registro de ahorro")

    con = obtener_conexion()
    cursor = con.cursor()

    # Socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    fecha = st.date_input("Fecha del aporte", value=date.today())
    monto = st.number_input("Monto del aporte", min_value=0.00, step=0.50)
    tipo = st.selectbox("Tipo de aporte", ["Ahorro", "Ahorro extra"])
    comprobante = st.text_input("Comprobante digital (opcional)")

    if st.button("Registrar ahorro"):

        # Obtener saldo acumulado actual
        cursor.execute("""
            SELECT Saldo_acumulado
            FROM Ahorro
            WHERE Id_Socia = %s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))
        row = cursor.fetchone()
        saldo_actual = row[0] if row else 0

        nuevo_saldo = saldo_actual + float(monto)

        # Guardar aporte
        cursor.execute("""
            INSERT INTO Ahorro
            (`Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
             `Comprobante digital`, Saldo_acumulado,
             Id_Socia, Id_Reunión, Id_Grupo, Id_Caja)
            VALUES (%s, %s, %s, %s, %s, %s, NULL, 1, NULL)
        """, (fecha, monto, tipo, comprobante, nuevo_saldo, id_socia))

        # Actualizar CAJA
        cursor.execute("""
            SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1
        """)
        row = cursor.fetchone()
        saldo_caja = row[0] if row else 0
        nuevo = saldo_caja + float(monto)

        cursor.execute("""
            INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
            VALUES (%s, %s, %s, 1, 2, CURRENT_DATE())
        """, (f"Ahorro – {socia_sel}", monto, nuevo))

        con.commit()
        st.success("Ahorro registrado correctamente.")
        st.rerun()

    st.markdown("---")

    # HISTORIAL
    cursor.execute("""
        SELECT 
            `Fecha del aporte`,
            `Monto del aporte`,
            `Tipo de aporte`,
            Saldo_acumulado
        FROM Ahorro
        WHERE Id_Socia = %s
        ORDER BY Id_Ahorro DESC
    """, (id_socia,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Fecha", "Monto", "Tipo", "Saldo acumulado"])
        st.subheader("📋 Historial de ahorro")
        st.dataframe(df)
    else:
        st.info("Aún no hay registros de ahorro.")
