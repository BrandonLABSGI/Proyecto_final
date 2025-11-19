import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion



# ---------------------------------------------------------
# 🟦 AUTORIZAR PRÉSTAMO
# ---------------------------------------------------------
def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 🔹 SELECCIÓN DE SOCIA (MEJORADO: muestra nombre)
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    opciones = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_seleccion = st.selectbox("👩Seleccione la socia:", list(opciones.keys()))
    id_socia = opciones[socia_seleccion]

    cursor.execute("SELECT Nombre FROM Socia WHERE Id_Socia = %s", (id_socia,))
    nombre_socia = cursor.fetchone()[0]

    st.success(f"📌 Socia seleccionada: **{nombre_socia}** (ID: {id_socia})")

    st.write("---")

    # ---------------------------------------------------------
    # 🔹 CAMPOS DEL PRÉSTAMO
    # ---------------------------------------------------------
    monto = st.number_input("🟢 Monto prestado ($):", min_value=1, step=1)

    tasa_interes = st.number_input("📉 Tasa de interés (%):", min_value=1, step=1)

    plazo_meses = st.number_input("🗓 Plazo (meses)", min_value=1, step=1)

    cuotas = st.number_input("📦 Número de cuotas", min_value=1, step=1)

    firma = st.text_input("✍️ Firma del directivo que autoriza")

    fecha_prestamo = date.today().strftime("%Y-%m-%d")

    st.write("---")

    # ---------------------------------------------------------
    # BOTÓN PARA AUTORIZAR PRÉSTAMO
    # ---------------------------------------------------------
    if st.button("✅ Autorizar préstamo"):

        try:
            cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
            caja = cursor.fetchone()

            if not caja:
                st.error("⚠ No existe una caja registrada.")
                return

            saldo_actual = caja[0]

            if monto > saldo_actual:
                st.error("❌ El monto solicitado es mayor al saldo disponible en caja.")
                return

            cursor.execute(
                """INSERT INTO Prestamo
                (`Fecha del préstamo`, `Monto prestado`, `Tasa de interes`, Plazo, Cuotas,
                `Saldo pendiente`, `Estado del préstamo`, Id_Grupo, Id_Socia, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s,
                (SELECT Id_Caja FROM Caja ORDER BY Id_Caja DESC LIMIT 1))""",
                (fecha_prestamo, monto, tasa_interes, plazo_meses, cuotas,
                 monto, "activo", id_socia)
            )

            con.commit()

            # ---------------------------------------------------------
            # CÁLCULOS DEL PRÉSTAMO
            # ---------------------------------------------------------
            interes_total = monto * (tasa_interes / 100)
            total_a_pagar = monto + interes_total
            pago_por_cuota = total_a_pagar / cuotas

            # ---------------------------------------------------------
            # RESUMEN BONITO
            # ---------------------------------------------------------
            st.success("✅ Préstamo autorizado correctamente.")

            st.header("🧾 Resumen del préstamo autorizado")

            st.subheader("📘 Detalle del préstamo")
            st.write(f"🔹 **Beneficiaria:** {nombre_socia}")
            st.write(f"🔹 **ID:** {id_socia}")
            st.write(f"🔹 **Monto prestado:** ${monto:.2f}")
            st.write(f"🔹 **Tasa de interés:** {tasa_interes}%")
            st.write(f"🔹 **Plazo:** {plazo_meses} meses")
            st.write(f"🔹 **Cuotas:** {cuotas}")
            st.write(f"🔹 **Fecha del préstamo:** {fecha_prestamo}")

            st.subheader("📊 Cálculos del préstamo")
            st.write(f"💰 **Interés total:** ${interes_total:.2f}")
            st.write(f"💵 **Total a pagar:** ${total_a_pagar:.2f}")
            st.write(f"📦 **Pago por cuota:** ${pago_por_cuota:.2f}")

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")

    
