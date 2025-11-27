import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion
from modulos.reglas_utils import obtener_reglas


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    # ============================================================
    # 🔗 Cargar reglas internas
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No hay reglas internas registradas. Configúralas primero.")
        return

    multa_mora = Decimal(str(reglas.get("multa_mora", 0)))

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # SOCIAS
    # ============================================================
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    dict_socias = {
        f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] 
        for s in socias
    }

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ============================================================
    # PRÉSTAMO ACTIVO
    # ============================================================
    cur.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
        LIMIT 1
    """, (id_socia,))
    prestamo = cur.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])

    # ============================================================
    # CALCULAR INTERÉS TOTAL REAL (NO EXISTE EN LA TABLA)
    # ============================================================
    monto_prestado = Decimal(prestamo["Monto prestado"])
    tasa = Decimal(prestamo["Tasa de interes"])
    interes_total = round(monto_prestado * tasa / Decimal(100), 2)

    # ============================================================
    # CONTAR CUOTAS PENDIENTES
    # ============================================================
    cur.execute("""
        SELECT COUNT(*) AS pendientes
        FROM Cuotas_prestamo
        WHERE Id_Prestamo=%s AND Estado='pendiente'
    """, (id_prestamo,))
    cuotas_pendientes = cur.fetchone()["pendientes"]

    # ============================================================
    # MOSTRAR INFORMACIÓN DEL PRÉSTAMO
    # ============================================================
    st.subheader("📄 Información del préstamo")
    st.write(f"**ID Préstamo:** {id_prestamo}")
    st.write(f"**Monto prestado:** ${monto_prestado}")
    st.write(f"📈 **Interés total:** ${interes_total}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")
    st.write(f"**Cuotas pendientes:** {cuotas_pendientes}")

    st.divider()

    # ============================================================
    # CUOTAS PENDIENTES
    # ============================================================
    cur.execute("""
        SELECT *
        FROM Cuotas_prestamo
        WHERE Id_Prestamo=%s AND Estado='pendiente'
        ORDER BY Numero_cuota ASC
    """, (id_prestamo,))
    cuotas = cur.fetchall()

    if not cuotas:
        st.success("🎉 Todas las cuotas están pagadas.")
        return

    st.subheader("📅 Cuotas pendientes")

    opciones = {
        f"Cuota #{c['Numero_cuota']} — Fecha {c['Fecha_programada']} — ${c['Monto_cuota']}":
            c["Id_Cuota"]
        for c in cuotas
    }

    cuota_sel = st.selectbox("Seleccione la cuota a pagar:", opciones.keys())
    id_cuota = opciones[cuota_sel]

    # ❗ AHORA SÍ DEVUELVE UN OBJETO date REAL
    fecha_pago_dt = st.date_input("📅 Fecha del pago:", date.today())

    # ============================================================
    # BOTÓN PRINCIPAL
    # ============================================================
    if st.button("💾 Registrar pago"):

        # Obtener datos de la cuota seleccionada
        cur.execute("SELECT * FROM Cuotas_prestamo WHERE Id_Cuota=%s", (id_cuota,))
        cuota = cur.fetchone()

        monto_cuota = Decimal(cuota["Monto_cuota"])
        fecha_programada = cuota["Fecha_programada"]

        # Normalizar fecha programada → convertir a date si llega como string
        if isinstance(fecha_programada, date):
            fecha_programada_dt = fecha_programada
        else:
            fecha_programada_dt = date.fromisoformat(str(fecha_programada))

        # ============================================================
        # 🚫 RESTRICCIÓN: SOLO PERMITIR LA FECHA EXACTA
        # ============================================================
        if fecha_pago_dt != fecha_programada_dt:
            st.error(f"❌ Esta cuota solo puede pagarse en la fecha EXACTA: {fecha_programada_dt}")
            return

        # ============================================================
        # PAGO DE CUOTA → CAJA
        # ============================================================
        id_caja = obtener_o_crear_reunion(str(fecha_pago_dt))

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago cuota préstamo {id_prestamo}",
            monto=float(monto_cuota)
        )

        # ============================================================
        # MARCAR CUOTA COMO PAGADA
        # ============================================================
        cur.execute("""
            UPDATE Cuotas_prestamo
            SET Estado='pagada', Fecha_pago=%s, Id_Caja=%s
            WHERE Id_Cuota=%s
        """, (str(fecha_pago_dt), id_caja, id_cuota))

        # ============================================================
        # ACTUALIZAR SALDO DEL PRÉSTAMO
        # ============================================================
        nuevo_saldo = saldo_pendiente - monto_cuota

        if nuevo_saldo < 0:
            nuevo_saldo = Decimal("0.00")

        cur.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente`=%s,
                Estado_del_prestamo =
                    CASE WHEN %s=0 THEN 'pagado' ELSE 'activo' END
            WHERE Id_Préstamo=%s
        """, (nuevo_saldo, nuevo_saldo, id_prestamo))

        # ============================================================
        # 🔥 CIERRE AUTOMÁTICO DEL PRÉSTAMO
        # ============================================================
        cur.execute("""
            SELECT COUNT(*) AS pendientes
            FROM Cuotas_prestamo
            WHERE Id_Prestamo=%s AND Estado='pendiente'
        """, (id_prestamo,))
        pendientes = cur.fetchone()["pendientes"]

        if pendientes == 0:
            cur.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente` = 0,
                    Estado_del_prestamo = 'pagado'
                WHERE Id_Préstamo = %s
            """, (id_prestamo,))

        con.commit()

        st.success("✔ Pago registrado correctamente.")
        st.rerun()
