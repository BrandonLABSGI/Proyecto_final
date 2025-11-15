import streamlit as st
from modulos.config.conexion import obtener_conexion

# -------------------------------------------------------------
# 🛒 Módulo de Registro de Ventas
# -------------------------------------------------------------
def mostrar_venta():
    st.header("🧾 Registro de Ventas")

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
        usuario = st.session_state.get("usuario", "Desconocido")  # toma el usuario logueado

        st.write(f"💰 Total calculado: **${total:.2f}**")
        enviar = st.form_submit_button("✅ Registrar venta")

        if enviar:
            try:
                cursor.execute(
                    "INSERT INTO Venta (Producto, Cantidad, PrecioUnitario, Total, Usuario) VALUES (%s, %s, %s, %s, %s)",
                    (producto, cantidad, precio_unitario, total, usuario)
                )
                con.commit()
                st.success(f"✅ Venta registrada correctamente por {usuario}")
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")
            finally:
                cursor.close()
                con.close()
