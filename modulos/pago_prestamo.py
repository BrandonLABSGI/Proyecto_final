import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ------------------------------------------
    # 1️⃣ SOCIAS
    # ------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ------------------------------------------
    # 2️⃣ PRESTAMOS ACTIVOS
    # ------------------------------------------
    cursor.execute("""
        SELECT 
            `Id_Préstamo`,
            `Fecha del préstamo`,
            `Monto prestado`,
            `Saldo pendiente`,
            `Cuotas`,
            `Tasa de interes`,
            `Plazo`
        FROM Prestamo
        WHERE Id_Socia = %s AND LOWER(Estado_del_prestamo) = 'activo'
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    opciones = {
        f"ID {p[0]} | Prestado: ${p[2]} | Saldo: ${p[3]}": p[0] for p in prestamos
    }
    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", list(opciones.keys()))
    id_prestamo = opciones[prestamo_sel]

    # ------------------------------------------
    # 3️⃣ OBTENER DATOS
    # ------------------------------------------
    cursor.execute("""
        SELECT 
            `Fecha del préstamo`, 
            `Monto prestado`, 
            `Saldo pendiente`, 
            `Tasa de interes`,
            `Plazo`,
            `Cuotas`
        FROM Prestamo
        WHERE Id_Préstamo = %s
    """, (id_prestamo,))

    fecha_prestamo, monto_prestado, saldo_pendiente, tasa, plazo, cuotas = cursor.fetchone()

    # ------------------------------------------
    # 4️⃣ FORMULARIO DE PAGO
    # ------------------------------------------
    st.subheader("📄 Registrar pago")

    fecha_pago_raw = st.date_input("📅 Fecha del pago:", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")
    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.01, step=0.50)

    if st.button("💾 Registrar pago"):
        try:

            # ------------------------------------------
            # 5️⃣ PRIMERO INSERTAMOS EN CAJA
            # ------------------------------------------
            cursor.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            saldo_actual = row[0] if row else 0
            nuevo_saldo_caja = saldo_actual + float(monto_abonado)

            cursor.execute("""
                INSERT INTO Caja
                (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha, Id_Multa)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE(), NULL)
            """, (
                f"Pago de préstamo – Socia {id_socia}",
                float(monto_abonado),
                nuevo_saldo_caja,
                1,
                2  # 2 = INGRESO
            ))

            # 🔥 Recuperamos el Id_Caja recién creado
            id_caja_registro = cursor.lastrowid

            # ------------------------------------------
            # 6️⃣ INSERTAR EN PAGO DEL PRÉSTAMO
            # ------------------------------------------
            saldo_restante = saldo_pendiente - float(monto_abonado)
            if saldo_restante < 0:
                saldo_restante = 0

            cursor.execute("""
                INSERT INTO `Pago del prestamo`
                (`Fecha de pago`, `Monto abonado`, `Interés pagado`,
                 `Capital pagado`, `Saldo restante`, `Id_Préstamo`, `Id_Caja`)
                VALUES (%s, %s, 0, 0, %s, %s, %s)
            """, (
                fecha_pago,
                float(monto_abonado),
                saldo_restante,
                id_prestamo,
                id_caja_registro
            ))

            # ------------------------------------------
            # 7️⃣ ACTUALIZAR PRÉSTAMO
            # ------------------------------------------
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente` = %s,
                    Estado_del_prestamo = CASE WHEN %s = 0 THEN 'cancelado' ELSE 'activo' END
                WHERE Id_Préstamo = %s
            """, (saldo_restante, saldo_restante, id_prestamo))

            # ------------------------------------------
            # 8️⃣ CONFIRMAR
            # ------------------------------------------
            con.commit()
            st.success("Pago registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
