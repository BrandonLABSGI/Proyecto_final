import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.reglas_utils import obtener_reglas
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion


def cierre_ciclo():

    st.title("🔴 Cierre del Ciclo General – Solidaridad CVX")

    # ======================================================
    # 1️⃣ LEER REGLAS INTERNAS (FECHAS DEL CICLO)
    # ======================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No existen reglas internas registradas. Debes definirlas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    ciclo_fin = reglas.get("ciclo_fin")

    if not ciclo_inicio:
        st.error("⚠ Debes definir la fecha de inicio del ciclo en Reglas Internas.")
        return

    st.info(f"📌 Ciclo actual: **{ciclo_inicio} → {ciclo_fin or 'Activo'}**")

    if ciclo_fin:
        st.warning("⚠ Este ciclo ya fue cerrado anteriormente.")
        return

    # ======================================================
    # 2️⃣ CONEXIÓN
    # ======================================================
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ======================================================
    # 3️⃣ TOTAL INGRESOS Y EGRESOS DESDE caja_movimientos
    # ======================================================
    cur.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto ELSE 0 END),0) AS ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto ELSE 0 END),0) AS egresos
        FROM caja_movimientos
        WHERE fecha >= %s
    """, (ciclo_inicio,))

    mov = cur.fetchone()
    total_ingresos = Decimal(str(mov["ingresos"]))
    total_egresos = Decimal(str(mov["egresos"]))

    balance = total_ingresos - total_egresos

    # ======================================================
    # 4️⃣ SALDO REAL EN CAJA (último saldo_final en caja_reunion)
    # ======================================================
    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        ORDER BY fecha DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    saldo_actual = Decimal(str(row["saldo_final"])) if row else Decimal("0.00")

    st.subheader("📊 Resumen financiero del ciclo")
    st.write(f"📥 **Ingresos totales:** ${total_ingresos:.2f}")
    st.write(f"📤 **Egresos totales:** ${total_egresos:.2f}")
    st.write(f"💼 **Balance neto:** ${balance:.2f}")
    st.write(f"💰 **Saldo actual real en caja:** ${saldo_actual:.2f}")

    monto_repartir = saldo_actual

    st.success(f"🧮 **Monto a repartir entre todas las socias:** ${monto_repartir:.2f}")

    st.warning("⚠ Después del cierre, el saldo en caja será reiniciado a $0.00")

    # ======================================================
    # 5️⃣ BOTÓN PARA CERRAR CICLO
    # ======================================================
    if st.button("🔒 Cerrar ciclo ahora"):

        hoy = date.today().strftime("%Y-%m-%d")

        # Actualizar fecha de cierre en reglas_internas
        cur.execute("""
            UPDATE reglas_internas
            SET ciclo_fin = %s
            ORDER BY id_regla DESC
            LIMIT 1
        """, (hoy,))

        # Registrar movimiento especial de cierre
        id_caja = obtener_o_crear_reunion(hoy)

        if saldo_actual > 0:
            registrar_movimiento(
                id_caja=id_caja,
                tipo="Egreso",
                categoria="Cierre de ciclo – distribución del fondo",
                monto=float(saldo_actual)
            )

        con.commit()

        st.success("✔ Ciclo cerrado correctamente. El saldo se ha reiniciado a $0.00.")
        st.balloons()
        st.rerun()

