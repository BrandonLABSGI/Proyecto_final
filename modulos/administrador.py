import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
import re

# ============================================================
#              PANEL PRINCIPAL DEL ADMINISTRADOR
# ============================================================
def interfaz_admin():
    # Seguridad: solo usuarios con rol "Administrador"
    rol = st.session_state.get("rol", "")
    if rol != "Administrador":
        st.error("⛔ No tiene permisos para acceder al panel de administrador.")
        return

    st.title("🛡️ Panel del Administrador")

    # --------------------------------------------------------
    # Métricas generales (tarjetas superiores)
    # --------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    try:
        con = obtener_conexion()
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM Distrito")
        total_distritos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Grupo")
        total_grupos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Empleado WHERE Rol = 'Promotora'")
        total_promotoras = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Empleado")
        total_empleados = cur.fetchone()[0]

        col1.metric("🏙 Distritos", total_distritos)
        col2.metric("👥 Grupos", total_grupos)
        col3.metric("👩‍💼 Promotores", total_promotoras)
        col4.metric("🧑‍💻 Empleados", total_empleados)

    except Exception as e:
        st.warning(f"No se pudieron cargar las métricas: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except:
            pass

    st.markdown("---")

    # --------------------------------------------------------
    # Menú lateral de administración
    # --------------------------------------------------------
    seccion = st.sidebar.radio(
        "📂 Módulos de administración",
        [
            "Gestión de roles",
            "Gestión de distritos",
            "Gestión de grupos",
            "Gestión de promotoras",
            "Gestión de empleados",
            "Resumen general",
        ]
    )

    if seccion == "Gestión de roles":
        gestion_roles()
    elif seccion == "Gestión de distritos":
        gestion_distritos()
    elif seccion == "Gestión de grupos":
        gestion_grupos()
    elif seccion == "Gestión de promotoras":
        gestion_promotoras()
    elif seccion == "Gestión de empleados":
        gestion_empleados()
    elif seccion == "Resumen general":
        resumen_general()
# ============================================================
#                      GESTIÓN DE ROLES
# ============================================================
def gestion_roles():
    st.header("🎭 Gestión de roles")

    con = obtener_conexion()
    cursor = con.cursor()

    col1, col2 = st.columns([2, 1])

    with col1:
        nuevo_rol = st.text_input("Nombre del nuevo rol")

    with col2:
        if st.button("➕ Crear rol"):
            if nuevo_rol.strip() == "":
                st.warning("Debe escribir un nombre de rol.")
            else:
                try:
                    cursor.execute(
                        "INSERT INTO Roles(Tipo_de_rol) VALUES(%s)",
                        (nuevo_rol,),
                    )
                    con.commit()
                    st.success("Rol creado correctamente.")
                except Exception as e:
                    st.error(f"Error al crear rol: {e}")

    st.markdown("### 📋 Roles existentes")
    try:
        cursor.execute("SELECT Id_Roles, Tipo_de_rol FROM Roles ORDER BY Id_Roles ASC")
        roles = cursor.fetchall()
        if roles:
            df = pd.DataFrame(roles, columns=["ID", "Tipo de rol"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay roles registrados.")
    except Exception as e:
        st.error(f"Error al consultar roles: {e}")

    cursor.close()
    con.close()


# ============================================================
#                   GESTIÓN DE DISTRITOS
# ============================================================
def gestion_distritos():
    st.header("🏙 Gestión de distritos")

    con = obtener_conexion()
    cursor = con.cursor()

    st.subheader("➕ Crear nuevo distrito")
    nombre = st.text_input("Nombre del distrito")

    if st.button("Crear distrito"):
        if nombre.strip() == "":
            st.warning("El nombre del distrito es obligatorio.")
        else:
            try:
                cursor.execute(
                    """
                    INSERT INTO Distrito(Nombre_distrito, Representantes, Cantidad_grupos, Estado_distrito)
                    VALUES(%s, 0, 0, 'Activo')
                    """,
                    (nombre,),
                )
                con.commit()
                st.success("Distrito creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear distrito: {e}")

    st.markdown("### 📋 Distritos registrados")

    try:
        cursor.execute(
            """
            SELECT Id_Distrito, Nombre_distrito
            FROM Distrito
            ORDER BY Id_Distrito ASC
            """
        )
        distritos = cursor.fetchall()
        if distritos:
            df = pd.DataFrame(distritos, columns=["ID", "Nombre"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay distritos registrados.")
    except Exception as e:
        st.error(f"Error al consultar distritos: {e}")

    cursor.close()
    con.close()
# ============================================================
#                   GESTIÓN DE PROMOTORAS
# ============================================================
def gestion_promotoras():
    st.header("👩‍💼 Gestión de promotoras")

    con = obtener_conexion()
    cursor = con.cursor()

    # Obtener id del rol Promotora
    cursor.execute("SELECT Id_Roles FROM Roles WHERE Tipo_de_rol='Promotora' LIMIT 1")
    row = cursor.fetchone()
    if not row:
        st.error("Debe crear el rol 'Promotora' en Gestión de Roles.")
        return

    id_rol_promotora = row[0]

    # Cargar distritos
    cursor.execute("SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito")
    distritos = cursor.fetchall()
    dict_dist = {f"{d[0]} - {d[1]}": d[0] for d in distritos}

    st.subheader("➕ Registrar nueva promotora")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        contra = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
    with col2:
        dui = st.text_input("DUI (9 dígitos)")
        tel = st.text_input("Teléfono (8 dígitos)")
        distrito_sel = st.selectbox("Distrito", list(dict_dist.keys()))
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    if st.button("Registrar promotora"):
        errores = []

        if not re.fullmatch(r"\d{9}", dui): errores.append("DUI inválido.")
        if not re.fullmatch(r"\d{8}", tel): errores.append("Teléfono inválido.")
        if usuario.strip() == "" or contra.strip() == "": errores.append("Usuario y contraseña obligatorios.")
        if nombres.strip() == "" or apellidos.strip() == "": errores.append("Datos personales obligatorios.")

        if errores:
            for e in errores: st.error(e)
        else:
            cursor.execute(
                """
                INSERT INTO Empleado(Usuario, Contra, Id_Rol, Rol, Nombres, Apellidos, DUI, Telefono, Distrito, Estado)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    usuario, contra,
                    id_rol_promotora, "Promotora",
                    nombres, apellidos,
                    dui, tel,
                    dict_dist[distrito_sel],
                    estado,
                )
            )
            con.commit()
            st.success("Promotora registrada.")

    st.markdown("---")
    st.subheader("📋 Promotoras registradas")

    cursor.execute(
        """
        SELECT e.Id_Empleado, e.Usuario, e.Nombres, e.Apellidos, d.Nombre_distrito, e.Estado
        FROM Empleado e
        LEFT JOIN Distrito d ON e.Distrito = d.Id_Distrito
        WHERE e.Id_Rol = %s
        """,
        (id_rol_promotora,)
    )
    prom = cursor.fetchall()

    if prom:
        st.dataframe(
            pd.DataFrame(
                prom,
                columns=["ID", "Usuario", "Nombres", "Apellidos", "Distrito", "Estado"]
            ),
            use_container_width=True
        )
    else:
        st.info("No hay promotoras registradas.")

    cursor.close()
    con.close()
# ============================================================
# 📘 GESTIÓN DE GRUPOS — ADMINISTRADOR
# ============================================================
def gestion_grupos():

    st.header("📘 Gestión de grupos")

    # Menú horizontal
    opcion = st.radio(
        "Seleccione una opción:",
        ["Crear grupo", "Grupos registrados", "Reasignar grupo"],
        horizontal=True
    )

    # ============================================================
    # 1) CREAR GRUPO
    # ============================================================
    if opcion == "Crear grupo":
        st.subheader("➕ Crear nuevo grupo")

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        # Distritos
        cursor.execute("SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Nombre_distrito ASC")
        distritos = cursor.fetchall()
        dict_distritos = {f"{d['Id_Distrito']} - {d['Nombre_distrito']}": d['Id_Distrito'] for d in distritos}

        # Promotoras
        cursor.execute("""
            SELECT Id_Empleado, Nombres, Apellidos FROM Empleado WHERE Rol='Promotora'
        """)
        promotoras = cursor.fetchall()
        dict_promotoras = {
            f"{p['Id_Empleado']} — {p['Nombres']} {p['Apellidos']}": p['Id_Empleado']
            for p in promotoras
        }

        # Campos
        nombre = st.text_input("Nombre del grupo")
        tasa = st.number_input("Tasa de interés (%)", min_value=0.0, max_value=100.0)
        monto_max = st.number_input("Monto máximo del préstamo", min_value=0.0)
        periodicidad = st.number_input("Periodicidad (días)", min_value=1)
        reglas = st.text_area("Reglas del préstamo")
        distrito_sel = st.selectbox("Distrito", list(dict_distritos.keys()))
        promotora_sel = st.selectbox("Promotora", list(dict_promotoras.keys()))

        if st.button("Crear grupo"):
            cursor.execute("""
                INSERT INTO Grupo (
                    Nombre_grupo, Tasa_de_interes, Monto_maximo_prestamo,
                    Periodicidad_reuniones, Reglas_del_prestamo,
                    Id_Distrito, Id_Promotora
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                nombre, tasa, monto_max, periodicidad,
                reglas, dict_distritos[distrito_sel], dict_promotoras[promotora_sel]
            ))
            con.commit()
            st.success("Grupo creado correctamente.")

        cursor.close()
        con.close()

    # ============================================================
    # 2) LISTAR GRUPOS REGISTRADOS
    # ============================================================
    elif opcion == "Grupos registrados":
        st.subheader("📋 Listado de grupos")

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT G.Id_Grupo, G.Nombre_grupo,
                   D.Nombre_distrito,
                   E.Nombres AS Promotora, E.Apellidos AS PromotoraA
            FROM Grupo G
            LEFT JOIN Distrito D ON D.Id_Distrito = G.Id_Distrito
            LEFT JOIN Empleado E ON E.Id_Empleado = G.Id_Promotora
            ORDER BY G.Id_Grupo ASC
        """)
        data = cursor.fetchall()

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay grupos registrados.")

        cursor.close()
        con.close()

    # ============================================================
    # 3) REASIGNAR GRUPO (INTEGRADO)
    # ============================================================
    elif opcion == "Reasignar grupo":

        st.subheader("🔄 Reasignar grupo a otra promotora")

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        # 1) Cargar todos los grupos
        cursor.execute("""
            SELECT G.Id_Grupo, G.Nombre_grupo, 
                   G.Id_Promotora,
                   E.Nombres AS NombrePromotora, E.Apellidos AS ApellidoPromotora
            FROM Grupo G
            LEFT JOIN Empleado E ON G.Id_Promotora = E.Id_Empleado
            ORDER BY G.Id_Grupo ASC
        """)
        grupos = cursor.fetchall()

        if not grupos:
            st.info("No hay grupos registrados.")
            return

        lista_grupos = {
            f"{g['Id_Grupo']} — {g['Nombre_grupo']} (Promotora: {g['NombrePromotora']} {g['ApellidoPromotora']})": g
            for g in grupos
        }

        sel_grupo = st.selectbox("Seleccione un grupo:", list(lista_grupos.keys()))
        grupo = lista_grupos[sel_grupo]

        st.write(f"### Grupo seleccionado: **{grupo['Nombre_grupo']}**")
        st.write(f"Promotora actual: **{grupo['NombrePromotora']} {grupo['ApellidoPromotora']}**")

        st.markdown("---")

        # 2) Cargar promotoras disponibles
        cursor.execute("""
            SELECT Id_Empleado, Nombres, Apellidos, Distrito 
            FROM Empleado 
            WHERE Rol = 'Promotora'
            ORDER BY Nombres ASC
        """)
        promotoras = cursor.fetchall()

        if not promotoras:
            st.error("No hay promotoras registradas.")
            return

        lista_promotoras = {
            f"{p['Id_Empleado']} — {p['Nombres']} {p['Apellidos']} (Distrito: {p['Distrito']})": p['Id_Empleado']
            for p in promotoras
        }

        nueva = st.selectbox("Seleccione la nueva promotora:", list(lista_promotoras.keys()))
        id_nueva = lista_promotoras[nueva]

        st.warning("⚠️ Antes de reasignar confirme que esta promotora supervisará este grupo correctamente.")

        if st.button("Confirmar reasignación"):
            cursor.execute("""
                UPDATE Grupo
                SET Id_Promotora = %s
                WHERE Id_Grupo = %s
            """, (id_nueva, grupo["Id_Grupo"]))

            con.commit()
            st.success(f"Grupo '{grupo['Nombre_grupo']}' reasignado exitosamente.")

        cursor.close()
        con.close()
# ============================================================
# 📊 RESUMEN GENERAL DEL SISTEMA
# ============================================================
def resumen_general():

    st.header("📊 Resumen general del sistema")

    try:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        # Totales del sistema
        cursor.execute("SELECT COUNT(*) AS total FROM Distrito")
        total_distritos = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Grupo")
        total_grupos = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Empleado")
        total_empleados = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Empleado WHERE Rol='Promotora'")
        total_promotoras = cursor.fetchone()["total"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏙 Distritos", total_distritos)
        col2.metric("👥 Grupos", total_grupos)
        col3.metric("🧑‍💻 Empleados", total_empleados)
        col4.metric("👩‍💼 Promotoras", total_promotoras)

        st.markdown("---")

        # Distribución de grupos por distrito
        st.subheader("📌 Distribución de grupos por distrito")
        cursor.execute("""
            SELECT D.Nombre_distrito, COUNT(G.Id_Grupo) AS Total
            FROM Distrito D
            LEFT JOIN Grupo G ON G.Id_Distrito = D.Id_Distrito
            GROUP BY D.Id_Distrito
            ORDER BY Total DESC
        """)
        dist = cursor.fetchall()

        df_dist = pd.DataFrame(dist)
        st.dataframe(df_dist, use_container_width=True)

        st.markdown("---")

        # Promotoras y cantidad de grupos asignados
        st.subheader("👩‍💼 Promotoras y grupos asignados")
        cursor.execute("""
            SELECT E.Id_Empleado, E.Nombres, E.Apellidos,
                   D.Nombre_distrito,
                   COUNT(G.Id_Grupo) AS Grupos
            FROM Empleado E
            LEFT JOIN Distrito D ON D.Id_Distrito = E.Distrito
            LEFT JOIN Grupo G ON G.Id_Promotora = E.Id_Empleado
            WHERE E.Rol = 'Promotora'
            GROUP BY E.Id_Empleado
            ORDER BY Grupos DESC
        """)
        prom = cursor.fetchall()

        df_prom = pd.DataFrame(prom)
        st.dataframe(df_prom, use_container_width=True)

        st.markdown("---")

        # Estado general por grupo
        st.subheader("📋 Estado general de grupos")
        cursor.execute("""
            SELECT 
                G.Id_Grupo, G.Nombre_grupo,
                D.Nombre_distrito AS Distrito,
                E.Nombres AS Promotora,
                E.Apellidos AS PromotoraA
            FROM Grupo G
            LEFT JOIN Distrito D ON D.Id_Distrito = G.Id_Distrito
            LEFT JOIN Empleado E ON E.Id_Empleado = G.Id_Promotora
            ORDER BY G.Id_Grupo ASC
        """)
        grupos = cursor.fetchall()

        df_grupos = pd.DataFrame(grupos)
        st.dataframe(df_grupos, use_container_width=True)

    except Exception as e:
        st.error("❌ Error al cargar el resumen general.")
        st.caption(str(e))

    finally:
        try:
            cursor.close()
            con.close()
        except:
            pass


# ============================================================
# FIN DEL MÓDULO DE ADMINISTRADOR
# ============================================================
