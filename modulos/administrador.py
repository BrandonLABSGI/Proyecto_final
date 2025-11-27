import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
import re

# ============================================================
#              PANEL PRINCIPAL DEL ADMINISTRADOR
# ============================================================
def interfaz_admin():
    rol = st.session_state.get("rol", "")
    if rol != "Administrador":
        st.error("⛔ No tiene permisos para acceder al panel de administrador.")
        return

    st.title("🛡️ Panel del Administrador")

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

    # === BOTONES DEL MENÚ (SIN PROMOTORAS) ===
    seccion = st.sidebar.radio(
        "📂 Módulos de administración",
        [
            "Gestión de roles",
            "Gestión de distritos",
            "Gestión de grupos",
            "Gestión de empleados",
            "Resumen general",
        ]
    )

    # === RUTEO (también sin promotoras) ===
    if seccion == "Gestión de roles":
        gestion_roles()
    elif seccion == "Gestión de distritos":
        gestion_distritos()
    elif seccion == "Gestión de grupos":
        gestion_grupos()
    elif seccion == "Gestión de empleados":
        gestion_empleados()
    elif seccion == "Resumen general":
        resumen_general()

# ============================================================
#                      GESTIÓN DE ROLES
# ============================================================
# (todo igual)

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
                    INSERT INTO Distrito(
                        Nombre_distrito,
                        Representantes,
                        Cantidad_grupos,
                        Estado_distrito
                    )
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
            FROM Distrito ORDER BY Id_Distrito ASC
            """
        )
        distritos = cursor.fetchall()
        if distritos:
            df = pd.DataFrame(
                distritos,
                columns=["ID", "Nombre"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay distritos registrados.")
    except Exception as e:
        st.error(f"Error al consultar distritos: {e}")

    cursor.close()
    con.close()


# ============================================================
#           GESTIÓN DE PROMOTORAS (CORREGIDO)
# ============================================================
def gestion_promotoras():
    st.header("👩‍💼 Gestión de promotores")

    con = obtener_conexion()
    cursor = con.cursor()

    # ID del Rol Promotora
    try:
        cursor.execute("SELECT Id_Roles FROM Roles WHERE Tipo_de_rol = 'Promotora'")
        row = cursor.fetchone()
        if not row:
            st.error("No existe el rol 'Promotora'.")
            return
        id_rol_promotora = row[0]
    except:
        st.error("Error cargando rol Promotora.")
        return

    # Cargar distritos
    try:
        cursor.execute("SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito ASC")
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos}
    except:
        dict_distritos = {}

    st.subheader("➕ Registrar nueva promotora")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        contra = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")

    with col2:
        dui = st.text_input("DUI (9 dígitos)", max_chars=9)
        telefono = st.text_input("Teléfono (8 dígitos)", max_chars=8)
        if dui and not dui.isdigit():
            st.error("El DUI solo puede contener números.")
        if telefono and not telefono.isdigit():
            st.error("El teléfono solo puede contener números.")

        distrito_sel = st.selectbox(
            "Distrito base",
            list(dict_distritos.keys()) if dict_distritos else ["(Sin distritos)"],
        )
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    if st.button("Registrar promotora"):
        errores = []

        if usuario.strip() == "" or contra.strip() == "":
            errores.append("Usuario y contraseña obligatorios.")
        if nombres.strip() == "" or apellidos.strip() == "":
            errores.append("Nombres y apellidos obligatorios.")

        if not re.fullmatch(r"\d{9}", dui):
            errores.append("El DUI debe ser de exactamente 9 dígitos.")
        if not re.fullmatch(r"\d{8}", telefono):
            errores.append("El teléfono debe ser de 8 dígitos.")

        if distrito_sel not in dict_distritos:
            errores.append("Debe seleccionar un distrito válido.")

        if errores:
            for e in errores:
                st.warning(e)
            return

        try:
            cursor.execute(
                """
                INSERT INTO Empleado(
                    Usuario, Contra, Id_Rol, Rol,
                    Nombres, Apellidos, DUI, Telefono,
                    Distrito, Estado
                )
                VALUES(%s,%s,%s,'Promotora',%s,%s,%s,%s,%s,%s)
                """,
                (
                    usuario.strip(), contra.strip(), id_rol_promotora,
                    nombres.strip(), apellidos.strip(),
                    dui, telefono,
                    dict_distritos[distrito_sel], estado
                )
            )
            con.commit()
            st.success("Promotora registrada correctamente.")
        except Exception as e:
            st.error(f"Error: {e}")

    # LISTADO
    st.markdown("### 📋 Promotoras registradas")
    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado, e.Usuario, e.Nombres, e.Apellidos,
                   d.Nombre_distrito, e.Estado
            FROM Empleado e
            LEFT JOIN Distrito d ON e.Distrito = d.Id_Distrito
            WHERE e.Rol = 'Promotora'
            ORDER BY e.Id_Empleado ASC
            """
        )
        promotoras = cursor.fetchall()
        if promotoras:
            df = pd.DataFrame(
                promotoras,
                columns=["ID", "Usuario", "Nombres", "Apellidos", "Distrito", "Estado"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay promotoras registradas.")
    except Exception as e:
        st.error(f"Error al consultar promotoras: {e}")

    cursor.close()
    con.close()


# ============================================================
#                   GESTIÓN DE GRUPOS
# ============================================================
def gestion_grupos():

    st.header("👥 Gestión de grupos")

    con = obtener_conexion()
    cursor = con.cursor()

    # DISTRITOS
    try:
        cursor.execute("SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito")
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos}
    except:
        dict_distritos = {}

    # PROMOTORAS
    try:
        cursor.execute(
            """
            SELECT Id_Empleado, Nombres, Apellidos
            FROM Empleado
            WHERE Rol = 'Promotora'
            """
        )
        promotoras = cursor.fetchall()
        dict_prom = {f"{p[0]} - {p[1]} {p[2]}": p[0] for p in promotoras}
    except:
        dict_prom = {}

    # DIRECTIVAS
    try:
        cursor.execute(
            """
            SELECT Id_Empleado, Nombres, Apellidos
            FROM Empleado
            WHERE Rol = 'Director'
            """
        )
        directores = cursor.fetchall()
        dict_dir = {f"{d[0]} - {d[1]} {d[2]}": d[0] for d in directores}
    except:
        dict_dir = {}

    # TIPO DE MULTA DEFAULT
    try:
        cursor.execute("SELECT Id_Tipo_multa FROM `Tipo de multa` LIMIT 1")
        row = cursor.fetchone()
        default_tipo_multa_id = row[0] if row else None
    except:
        default_tipo_multa_id = None

    st.subheader("➕ Crear nuevo grupo")

    nombre_grupo = st.text_input("Nombre del grupo")
    fecha_inicio = st.date_input("Fecha de inicio", value=date.today())

    distrito_sel = st.selectbox("Distrito", list(dict_distritos.keys()))
    promotora_sel = st.selectbox("Promotora asignada", list(dict_prom.keys()))

    opciones_dir = ["(Sin director)"] + list(dict_dir.keys())
    director_sel = st.selectbox("Director del grupo", opciones_dir)

    if st.button("Crear grupo"):

        if nombre_grupo.strip() == "":
            st.warning("El nombre del grupo es obligatorio.")
            return

        if default_tipo_multa_id is None:
            st.warning("No hay tipos de multa registrados.")
            return

        id_directiva = (
            dict_dir[director_sel] if director_sel in dict_dir else None
        )

        try:
            cursor.execute(
                """
                INSERT INTO Grupo(
                    Nombre_grupo, Tasa_de_interes, Periodicidad_reuniones,
                    Id_Tipo_multa, Reglas_de_prestamo, Fecha_inicio,
                    Id_Promotora, Id_Distrito, Id_Directiva
                )
                VALUES(%s,0.0,7,%s,'Reglas generales',%s,%s,%s,%s)
                """,
                (
                    nombre_grupo,
                    default_tipo_multa_id,
                    fecha_inicio.strftime("%Y-%m-%d"),
                    dict_prom[promotora_sel],
                    dict_distritos[distrito_sel],
                    id_directiva,
                )
            )
            con.commit()
            st.success("Grupo creado correctamente.")
        except Exception as e:
            st.error(f"Error al crear grupo: {e}")

    # TABLA
    st.markdown("### 📋 Grupos registrados")
    try:
        cursor.execute(
            """
            SELECT g.Id_Grupo, g.Nombre_grupo, d.Nombre_distrito,
                   CONCAT(p.Nombres,' ',p.Apellidos) AS Promotora,
                   CONCAT(COALESCE(dir.Nombres,''),' ',COALESCE(dir.Apellidos,'')) AS Director,
                   g.Fecha_inicio
            FROM Grupo g
            JOIN Distrito d ON g.Id_Distrito = d.Id_Distrito
            JOIN Empleado p ON g.Id_Promotora = p.Id_Empleado
            LEFT JOIN Empleado dir ON g.Id_Directiva = dir.Id_Empleado
            ORDER BY g.Id_Grupo ASC
            """
        )
        grupos = cursor.fetchall()
        if grupos:
            df = pd.DataFrame(
                grupos,
                columns=["ID", "Nombre", "Distrito", "Promotora", "Director", "Inicio"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay grupos registrados.")
    except Exception as e:
        st.error(f"Error al cargar grupos: {e}")

    cursor.close()
    con.close()


# ============================================================
#           GESTIÓN DE EMPLEADOS (CORREGIDO)
# ============================================================
def gestion_empleados():
    st.header("🧑‍💻 Gestión de empleados")

    con = obtener_conexion()
    cursor = con.cursor()

    # ROLES
    try:
        cursor.execute("SELECT Id_Roles, Tipo_de_rol FROM Roles")
        roles = cursor.fetchall()
        dict_roles = {f"{r[0]} - {r[1]}": (r[0], r[1]) for r in roles}
    except:
        dict_roles = {}

    # DISTRITOS
    try:
        cursor.execute("SELECT Id_Distrito, Nombre_distrito FROM Distrito")
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos}
    except:
        dict_distritos = {}

    st.subheader("➕ Crear nuevo empleado")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        contra = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
    with col2:
        dui = st.text_input("DUI (9 dígitos)", max_chars=9)
        telefono = st.text_input("Teléfono (8 dígitos)", max_chars=8)

        # VALIDACIONES EN TIEMPO REAL
        if dui and not dui.isdigit():
            st.error("El DUI solo debe contener números.")
        if telefono and not telefono.isdigit():
            st.error("El teléfono solo debe contener números.")

        distrito_sel = st.selectbox("Distrito", list(dict_distritos.keys()))
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    rol_sel = st.selectbox("Rol", list(dict_roles.keys()))

    if st.button("Crear empleado"):

        errores = []

        if not usuario.strip() or not contra.strip():
            errores.append("Usuario y contraseña obligatorios.")
        if not nombres.strip() or not apellidos.strip():
            errores.append("Nombres y apellidos obligatorios.")

        if not re.fullmatch(r"\d{9}", dui):
            errores.append("DUI debe tener exactamente 9 dígitos.")
        if not re.fullmatch(r"\d{8}", telefono):
            errores.append("Teléfono debe tener exactamente 8 dígitos.")

        if errores:
            for e in errores:
                st.warning(e)
            return

        id_rol, rol_texto = dict_roles[rol_sel]
        id_distrito = dict_distritos[distrito_sel]

        try:
            cursor.execute(
                """
                INSERT INTO Empleado(
                    Usuario, Contra, Id_Rol, Rol,
                    Nombres, Apellidos, DUI, Telefono,
                    Distrito, Estado
                )
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    usuario.strip(), contra.strip(),
                    id_rol, rol_texto,
                    nombres.strip(), apellidos.strip(),
                    dui, telefono,
                    id_distrito, estado
                )
            )
            con.commit()
            st.success("Empleado registrado correctamente.")
        except Exception as e:
            st.error(f"Error al registrar empleado: {e}")

    st.markdown("### 📋 Empleados registrados")

    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado, e.Usuario, e.Rol,
                   e.Nombres, e.Apellidos, d.Nombre_distrito, e.Estado
            FROM Empleado e
            LEFT JOIN Distrito d ON e.Distrito = d.Id_Distrito
            ORDER BY e.Id_Empleado ASC
            """
        )
        empleados = cursor.fetchall()
        df = pd.DataFrame(
            empleados,
            columns=["ID", "Usuario", "Rol", "Nombres", "Apellidos", "Distrito", "Estado"]
        )
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar empleados: {e}")

    cursor.close()
    con.close()


# ============================================================
#                   RESUMEN GENERAL
# ============================================================
def resumen_general():
    st.header("📊 Resumen general")

    con = obtener_conexion()
    cursor = con.cursor()

    # GRUPOS
    try:
        cursor.execute(
            """
            SELECT g.Id_Grupo, g.Nombre_grupo, d.Nombre_distrito,
                   CONCAT(p.Nombres,' ',p.Apellidos) AS Promotora,
                   CONCAT(COALESCE(dir.Nombres,''),' ',COALESCE(dir.Apellidos,'')) AS Directiva,
                   g.Fecha_inicio
            FROM Grupo g
            JOIN Distrito d ON g.Id_Distrito = d.Id_Distrito
            JOIN Empleado p ON g.Id_Promotora = p.Id_Empleado
            LEFT JOIN Empleado dir ON g.Id_Directiva = dir.Id_Empleado
            """
        )
        df_grupos = pd.DataFrame(
            cursor.fetchall(),
            columns=["ID", "Grupo", "Distrito", "Promotora", "Directiva", "Inicio"]
        )
    except:
        df_grupos = pd.DataFrame()

    # PROMOTORAS
    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado,
                   CONCAT(e.Nombres,' ',e.Apellidos) AS Promotora,
                   COUNT(g.Id_Grupo) AS TotalGrupos
            FROM Empleado e
            LEFT JOIN Grupo g ON g.Id_Promotora = e.Id_Empleado
            WHERE e.Rol='Promotora'
            GROUP BY e.Id_Empleado
            """
        )
        df_promo = pd.DataFrame(cursor.fetchall(),
            columns=["ID", "Promotora", "Total grupos"])
    except:
        df_promo = pd.DataFrame()

    # DISTRITOS
    try:
        cursor.execute(
            """
            SELECT d.Id_Distrito, d.Nombre_distrito,
                   COUNT(g.Id_Grupo) AS TotalGrupos
            FROM Distrito d
            LEFT JOIN Grupo g ON g.Id_Distrito = d.Id_Distrito
            GROUP BY d.Id_Distrito
            """
        )
        df_dist = pd.DataFrame(cursor.fetchall(),
            columns=["ID", "Distrito", "Grupos"])
    except:
        df_dist = pd.DataFrame()

    cursor.close()
    con.close()

    tab1, tab2, tab3 = st.tabs(["Por grupo", "Por promotora", "Por distrito"])

    with tab1:
        st.dataframe(df_grupos, use_container_width=True)
    with tab2:
        st.dataframe(df_promo, use_container_width=True)
    with tab3:
        st.dataframe(df_dist, use_container_width=True)
