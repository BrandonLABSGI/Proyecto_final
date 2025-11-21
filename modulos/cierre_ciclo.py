import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

def cierre_ciclo():

    st.title("🔴 Cierre del Ciclo General – Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------------------------------------------
    # 1️⃣ CICLO ACTIVO
    # --------------------------------------------------------------
    cursor.execute("SELECT id_ciclo, nombre_ciclo, fecha_inicio FROM ciclo WHERE estado='abierto'")
    ciclo = cursor.fetchone()

    if not ciclo:
        st.error("❌ No existe un ciclo activo.")
        return

    id_ciclo, nombre_ciclo, fecha_inicio = ciclo

    st.info(f"📌 Ciclo activo: **{nombre_ciclo}** (Inició: {fecha_inicio})")

    # --------------------------------------------------------------
    # 2️⃣ SUMAR INGRESOS DEL CICLO
    # --------------------------------------------------------------

    # MULTAS PAGADAS
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0)
        FROM multa
        WHERE Estado='pagada'
    """)
    total_multas = cursor.fetchone()[0]

    # INGRESOS EXTRA
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0)
        FROM IngresosExtra
    """)
    total_ing_extra = cursor.fetchone()[0]

    # PAGOS DE PRÉSTAMO (capital + interés)
    cursor.execute("""
        SELECT IFNULL(SUM(Monto_abonado + Interes_pagado),0)
        FROM Pago_del_prestamo
    """)
    total_pagos = cursor.fetchone()[0]

    total_ingresos = total_multas + total_ing_extra + total_pagos

    # --------------------------------------------------------------
    # 3️⃣ SUMAR EGRESOS DEL CICLO
    # --------------------------------------------------------------

    cursor.execute("""
        SELECT IFNULL(SUM(Monto_prestado),0)
        FROM Prestamo
    """)
    total_prestamos = cursor.fetchone()[0]

    total_egresos = total_prestamos

    # --------------------------------------------------------------
    # 4️⃣ CÁLCULOS FINALES DEL CICLO
    # --------------------------------------------------------------

    saldo_inicial = 0.00
    monto_repartido = (saldo_inicial + total_ingresos) - total_egresos
    saldo_final = 0.00   # regla oficial

    st.subheader("📊 Resumen del ciclo")

    st.write(f"💰 **Total de ingresos del ciclo:** ${total_ingresos:,.2f}")
    st.write(f"🏦 **Total de egresos del ciclo:** ${total_egresos:,.2f}")
    st.write("---")
    st.success(f"🧮 **Monto a repartir:** ${monto_repartido:,.2f}")
    st.info("El saldo final del ciclo será **$0.00** porque todo el dinero se reparte.")

    # --------------------------------------------------------------
    # 5️⃣ BOTÓN DE CIERRE
    # --------------------------------------------------------------

    if st.button("🔒 Cerrar ciclo ahora"):

        cursor.execute("""
            UPDATE ciclo
            SET fecha_fin=%s,
                saldo_final=%s,
                estado='cerrado'
            WHERE id_ciclo=%s
        """, (date.today(), saldo_final, id_ciclo))

        con.commit()

        st.success("✔ Ciclo cerrado exitosamente. El saldo final es 0.00.")
        st.rerun()
