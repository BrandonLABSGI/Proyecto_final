from modulos.conexion import obtener_conexion


# ============================================================
# 🔵 OBTENER REGLAS INTERNAS POR GRUPO
# ============================================================
def obtener_reglas(id_grupo=1):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT *
        FROM reglas_grupo
        WHERE Id_Grupo = %s
        LIMIT 1
    """, (id_grupo,))

    row = cur.fetchone()
    return row if row else {}


# ============================================================
# 🔵 GUARDAR / ACTUALIZAR REGLAS INTERNAS
# ============================================================
def guardar_reglas(id_grupo, ciclo_inicio, ciclo_fin, monto_ahorro, multa_inasistencia, multa_mora):

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ¿Ya existen reglas?
    cur.execute("""
        SELECT Id_Reglas
        FROM reglas_grupo
        WHERE Id_Grupo=%s
    """, (id_grupo,))
    fila = cur.fetchone()

    if fila:
        # UPDATE
        cur.execute("""
            UPDATE reglas_grupo
            SET ciclo_inicio=%s,
                ciclo_fin=%s,
                monto_ahorro=%s,
                multa_inasistencia=%s,
                multa_mora=%s
            WHERE Id_Grupo=%s
        """, (ciclo_inicio, ciclo_fin, monto_ahorro, multa_inasistencia, multa_mora, id_grupo))

    else:
        # INSERT
        cur.execute("""
            INSERT INTO reglas_grupo
            (Id_Grupo, ciclo_inicio, ciclo_fin, monto_ahorro, multa_inasistencia, multa_mora)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_grupo, ciclo_inicio, ciclo_fin, monto_ahorro, multa_inasistencia, multa_mora))

    con.commit()
    return True
