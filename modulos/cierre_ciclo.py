import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# Caja por reunión
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#                 🟦 MÓDULO DE CIERRE DE CICLO
# ============================================================
def cierre_ciclo():

    st.header("🔚 Cierre de Ciclo – Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ OBTENER CICLO ACTIVO
    # ============================================================
    cursor.execute("""
        SELECT *
        FROM cierre_ciclo
        WHERE Estado = 'Abierto'
        ORDER BY Id_Cierre DESC
        LIMIT 1
    """)
    ciclo = cursor.fetchone()

    if not ciclo:
        st.error("❌ No existe ningún ciclo activo. Debes crear uno antes de cerrar.")
        return

    id_cierre = ciclo["Id_Cierre"]
    fecha_inicio = ciclo["Fecha_inicio"]

    st.info(f"📌 Ciclo activo iniciado el: **{fecha_inicio}**")

    # ============================================================
    # 2️⃣ OBTENER DATOS DE AHORROS POR SOCIA
    # ============================================================
    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre,
               COALESCE(A.`Saldo acumulado`,0) AS saldo_final
        FROM Socia S
        LEFT JOIN (
            SELECT Id_Socia, `Saldo acumulado`
            FROM Ahorro
            ORDER BY Id_Ahorro DESC
        ) A ON S.Id_Socia = A.Id_Socia
        ORDER BY S.Id_Socia ASC;
    """)
    socias = cursor.fetchall()

    df_socias = pd.DataFrame(socias)

    total_ahorros = df_socias["saldo_final"].sum()

    # ============================================================
    # 3️⃣ OBTENER FONDO DEL GRUPO (CAJA)
    # ============================================================
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        ORDER BY fecha DESC
        LIMIT 1
    """)
    row_fondo = cursor.fetchone()

    total_fondo = row_fondo["saldo_final"] if row_fondo else 0

    # ============================================================
    # 4️⃣ MOSTRAR RESUMEN PREVIO
    # ============================================================
    st.subheader("📊 Resumen del ciclo antes del cierre")

    c1, c2 = st.columns(2)
    c1.metric("💰 Total ahorros individuales", f"${total_ahorros:,.2f}")
    c2.metric("🏦 Fondo total del grupo (caja)", f"${total_fondo:,.2f}")

    # ============================================================
    # 5️⃣ CALCULAR UTILIDADES DEL GRUPO
    # ============================================================
    if total_ahorros == 0:
        st.error("❌ No hay ahorros registrados. No puede hacerse el cierre.")
        return

    utilidades = total_fondo - total_ahorros
    if utilidades < 0:
        st.warning("⚠ El fondo del grupo es menor que los ahorros. No se puede cerrar.")
        return

    st.metric("📈 Utilidades del grupo", f"${utilidades:,.2f}")

    # ============================================================
    # 6️⃣ DISTRIBUCIÓN PROPORCIONAL
    # ============================================================
    df_socias["porcentaje"] = df_socias["saldo_final"] / total_ahorros
    df_socias["utilidad_asignada"] = df_socias["porcentaje"] * utilidades
    df_socias["utilidad_redondeada"] = df_socias["utilidad_asignada"].round(2)
    df_socias["saldo_siguiente_ciclo"] = df_socias["saldo_final"] + df_socias["utilidad_redondeada"]

    st.subheader("📄 Distribución proporcional")

    st.dataframe(df_socias[[
        "Id_Socia", "Nombre", "saldo_final",
        "porcentaje", "utilidad_redondeada", "saldo_siguiente_ciclo"
    ]])

    faltante = utilidades - df_socias["utilidad_redondeada"].sum()

    st.info(f"🧮 Ajuste por redondeo (sobrante): **${faltante:.2f}**")

    # ============================================================
    # 7️⃣ CONFIRMAR CIERRE
    # ============================================================
    if st.button("🔒 Confirmar cierre de ciclo"):

        try:
            # 1️⃣ Registrar valores finales del ciclo
            cursor.execute("""
                UPDATE cierre_ciclo
                SET 
                    Fecha_cierre = %s,
                    Total_ahorros = %s,
                    Total_fondo_grupo = %s,
                    Utilidades = %s,
                    Sobrante = %s,
                    Estado = 'Cerrado'
                WHERE Id_Cierre = %s
            """, (
                date.today().strftime("%Y-%m-%d"),
                total_ahorros,
                total_fondo,
                utilidades,
                faltante,
                id_cierre
            ))

            # 2️⃣ Crear nuevo ciclo automáticamente
            cursor.execute("""
                INSERT INTO cierre_ciclo
                (Fecha_inicio, Fecha_cierre, Total_ahorros, Total_fondo_grupo,
                 Utilidades, Sobrante, Estado, Id_Grupo)
                VALUES (%s, NULL, 0, 0, 0, 0, 'Abierto', %s)
            """, (
                date.today().strftime("%Y-%m-%d"),
                ciclo["Id_Grupo"]
            ))

            con.commit()
            st.success("✔ El ciclo ha sido cerrado correctamente y un nuevo ciclo fue creado.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al cerrar ciclo: {e}")

