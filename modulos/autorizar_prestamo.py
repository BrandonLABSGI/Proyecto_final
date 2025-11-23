import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento
from modulos.reglas_utils import obtener_reglas


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    # ============================================================
    # 🔗 REGLAS INTERNAS
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ No existen reglas internas registradas.")
        return

    prestamo_maximo = float(reglas["prestamo_maximo"])
    interes_por_10 = float(reglas["interes_por_10"])   # Ej: 6%
    plazo_maximo = int(reglas["plazo_maximo"])         # Semanas

    # ============================================================
    # CONEXIÓN
    # ============================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # SOCIAS
    # ============================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ============================================================
    # FORMULARIO
    # ============================================================
    with st.form("form_prestamo"):

        fecha_prestamo_raw = st.date_input("📅 Fecha del préstamo", date.today())
        fecha_prestamo = fecha_prestamo_raw.strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        # ============================================================
        # MONTO PRESTADO — BLOQUEO TOTAL (NO LETRAS, NO SÍMBOLOS)
        # ============================================================
        monto_str = st.text_input(
            "💵 Monto prestado ($):",
            placeholder=f"Máximo permitido: ${prestamo_maximo}"
        )

        # Limpiar cualquier cosa que no sea número
        if monto_str:
            limpio = "".join(c for c in monto_str if c.isdigit())
            if limpio != monto_str:
                st.warning("⚠ Solo se permiten números. Se eliminaron caracteres inválidos.")
                monto_str = limpio

        monto = float(monto_str) if monto_str.isdigit() else 0.0

        if monto > prestamo_maximo:
            st.error(f"❌ El monto máximo permitido es: ${prestamo_maximo}")
            st.stop()

        # ============================================================
        # INTERÉS — Bloqueado, calculado automáticamente
        # ============================================================
        interes_calculado = (monto / 10) * interes_por_10
        st.number_input("📈 Interés (%)", value=interes_calculado, disabled=True)

        # ============================================================
        # PLAZO Y CUOTAS
        # ============================================================
        plazo = st.number_input(
            "🗓 Plazo (semanas):",
            min_value=1,
            max_value=plazo_maximo,
            value=1
        )

        cuotas = st.number_input(
            "📑 Número de cuotas:",
            min_value=1,
            value=1
        )

        firma = st.text_input("✍️ Firma directiva")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    if not enviar:
        return

    # ============================================================
    # VALIDACIÓN — Préstamo activo
    # ============================================================
    cursor.execute("""
        SELECT COUNT(*) AS activos
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    if cursor.fetchone()["activos"] > 0:
        st.error("❌ La socia ya tiene un préstamo activo.")
        return

    # ============================================================
    # VALIDACIÓN — Ahorro disponible
    # ============================================================
    cursor.execute("""
        SELECT `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia=%s
        ORDER BY Id_Ahorro DESC LIMIT 1
    """, (id_socia,))
    row = cursor.fetchone()
    ahorro_total = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

    if Decimal(monto) > ahorro_total:
        st.error(f"❌ Ahorro insuficiente. Tiene ${ahorro_total}.")
        return

    # ============================================================
    # VALIDACIÓN — Caja
    # ============================================================
    id_caja = obtener_o_crear_reunion(fecha_prestamo)
    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    saldo_caja = Decimal(cursor.fetchone()["saldo_final"])

    if Decimal(monto) > saldo_caja:
        st.error(f"❌ Saldo insuficiente en caja. Disponible: ${saldo_caja}.")
        return

    # ============================================================
    # CÁLCULO FINAL
    # ============================================================
    interes_total = Decimal(monto) * (Decimal(interes_por_10) / Decimal(100))
    total_pagar = Decimal(monto) + interes_total

    # ============================================================
    # REGISTRAR PRÉSTAMO
    # ============================================================
    cursor.execute("""
        INSERT INTO Prestamo(
            `Fecha del préstamo`, `Monto prestado`, `Interes_total`,
            `Tasa de interes`, `Plazo`, `Cuotas`, `Saldo pendiente`,
            Estado_del_prestamo, Id_Grupo, Id_Socia, Id_Caja
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,'activo',1,%s,%s)
    """, (
        fecha_prestamo,
        monto,
        float(interes_total),
        interes_por_10,
        plazo,
        cuotas,
        float(total_pagar),
        id_socia,
        id_caja
    ))

    id_pre = cursor.lastrowid

    # ============================================================
    # DESCONTAR AHORRO
    # ============================================================
    nuevo_ahorro = ahorro_total - Decimal(monto)
    cursor.execute("""
        INSERT INTO Ahorro(
            `Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
            `Comprobante digital`, `Saldo acumulado`, Id_Socia
        )
        VALUES (%s,%s,'Descuento préstamo','---',%s,%s)
    """, (fecha_prestamo, -Decimal(monto), nuevo_ahorro, id_socia))

    # ============================================================
    # ACTUALIZAR CAJA
    # ============================================================
    registrar_movimiento(
        id_caja=id_caja,
        tipo="Egreso",
        categoria=f"Préstamo otorgado – {socia_sel}",
        monto=float(monto)
    )

    # ============================================================
    # GENERAR CUOTAS (cada 15 días)
    # ============================================================
    valor_cuota = total_pagar / Decimal(cuotas)
    fecha_base = datetime.strptime(fecha_prestamo, "%Y-%m-%d")

    listado_cuotas = []

    for n in range(1, cuotas + 1):
        fecha_cuota = fecha_base + timedelta(days=15 * n)
        fecha_str = fecha_cuota.strftime("%Y-%m-%d")

        cursor.execute("""
            INSERT INTO Cuotas_prestamo 
            (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
            VALUES (%s,%s,%s,%s,'pendiente')
        """, (id_pre, n, fecha_str, round(float(valor_cuota), 2)))

        listado_cuotas.append((n, fecha_str, round(float(valor_cuota), 2)))

    con.commit()

    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    st.success("✔ Préstamo autorizado correctamente.")
    st.subheader("📄 Resumen del préstamo")

    st.write(f"**📅 Fecha del préstamo:** {fecha_prestamo}")
    st.write(f"**👩 Socia:** {socia_sel}")
    st.write(f"**💵 Monto prestado:** ${monto}")
    st.write(f"**📈 Intereses generados:** ${round(float(interes_total), 2)}")
    st.write(f"**💰 Total a pagar:** ${round(float(total_pagar), 2)}")
    st.write("---")
    st.write("### 🗓 Cuotas programadas:")

    for num, fecha, valor in listado_cuotas:
        st.write(f"➡ **Cuota {num}:** {fecha} — ${valor}")
