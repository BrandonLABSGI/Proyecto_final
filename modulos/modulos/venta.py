import streamlit as st
from modulos.config.conexion import obtener_conexion

# -------------------------------------------------------------
# 🧾 Módulo de Registro de Ventas
# -------------------------------------------------------------
def mostrar_venta():
    st.header("🛒 Registro de Ventas")

    # Conectamos a la base de datos
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # --- FORMULARIO DE REGISTRO ---
    with st.form("form_venta"):
        producto = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario ($)", min_value=0.01, step=0.01)
        total = cantidad * precio_unitario
        st.write(f"💰 **Total:** ${total:,.2f}")

        enviar = st.form_submit_button("✅ Registrar venta")

        if enviar:
            if producto.strip() == "":
                st.warning("⚠️ Debes ingresar el nombre del producto.")
            else:
                try:
                    # ✅ Insertamos el usuario logueado en la venta
                    query = """
                        INSERT INTO Venta (Producto, Cantidad, PrecioUnitario, Total, Usuario)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (producto, cantidad, precio_unitario, total, st.session_state["usuario"]))
                    con.commit()
                    st.success(f"✅ Venta registrada correctamente por **{st.session_state['usuario']}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al registrar la venta: {e}")
                finally:
                    cursor.close()
                    con.close()

    # --- MOSTRAR VENTAS REGISTRADAS ---
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("SELECT Id_Venta, Producto, Cantidad, PrecioUnitario, Total, Usuario FROM Venta ORDER BY Id_Venta DESC")
    registros = cursor.fetchall()

    if registros:
        st.subheader("📋 Ventas registradas")
        st.table(registros)
    else:
        st.info("🕓 Aún no hay ventas registradas.")

    cursor.close()
    con.close()
