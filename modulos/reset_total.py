import mysql.connector
from modulos.conexion import obtener_conexion


def ejecutar_reset_total():
    con = obtener_conexion()
    cursor = con.cursor()

    print("🧨 Reiniciando toda la base de datos CVX…")

    # ---------------------------------------------------------------
    # 1. ELIMINAR TODAS LAS TABLAS (orden correcto)
    # ---------------------------------------------------------------
    tablas = [
        "caja_movimientos",
        "caja_reunion",
        "caja_general",
        "Cuotas_prestamo",
        "Prestamo",
        "Ahorro",
        "Multa",
        "Tipo_de_multa",
        "Asistencia",
        "Reunion",
        "Gastos_grupo",
        "Socia"
    ]

    for t in tablas:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")
            print(f"✔ Eliminada tabla: {t}")
        except Exception as e:
            print(f"❌ Error eliminando {t}: {e}")

    # ---------------------------------------------------------------
    # 2. CREAR TABLAS DESDE CERO
    # ---------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE Socia(
            Id_Socia INT AUTO_INCREMENT PRIMARY KEY,
            Nombre VARCHAR(100),
            DUI VARCHAR(20),
            Telefono VARCHAR(20),
            Sexo VARCHAR(1)
        );
    """)

    cursor.execute("""
        CREATE TABLE Reunion(
            Id_Reunion INT AUTO_INCREMENT PRIMARY KEY,
            Fecha_reunion DATE,
            Observaciones TEXT,
            Acuerdos TEXT,
            Tema_central TEXT,
            Id_Grupo INT
        );
    """)

    cursor.execute("""
        CREATE TABLE Asistencia(
            Id_Asistencia INT AUTO_INCREMENT PRIMARY KEY,
            Id_Reunion INT,
            Id_Socia INT,
            Estado_asistencia VARCHAR(20),
            Fecha DATE
        );
    """)

    cursor.execute("""
        CREATE TABLE Tipo_de_multa(
            Id_Tipo_multa INT AUTO_INCREMENT PRIMARY KEY,
            `Tipo de multa` VARCHAR(255),
            Monto_base DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE Multa(
            Id_Multa INT AUTO_INCREMENT PRIMARY KEY,
            Monto DECIMAL(10,2),
            Fecha_aplicacion DATE,
            Estado VARCHAR(20),
            Id_Tipo_multa INT,
            Id_Socia INT
        );
    """)

    cursor.execute("""
        CREATE TABLE Ahorro(
            Id_Ahorro INT AUTO_INCREMENT PRIMARY KEY,
            `Fecha del aporte` DATE,
            `Monto del aporte` DECIMAL(10,2),
            `Tipo de aporte` VARCHAR(50),
            `Comprobante digital` TEXT,
            `Saldo acumulado` DECIMAL(10,2),
            Id_Socia INT
        );
    """)

    cursor.execute("""
        CREATE TABLE Prestamo(
            Id_Préstamo INT AUTO_INCREMENT PRIMARY KEY,
            `Fecha del préstamo` DATE,
            `Monto prestado` DECIMAL(10,2),
            `Interes_total` DECIMAL(10,2),
            `Tasa de interes` DECIMAL(10,2),
            `Plazo` INT,
            `Cuotas` INT,
            `Saldo pendiente` DECIMAL(10,2),
            Estado_del_prestamo VARCHAR(50),
            Id_Grupo INT,
            Id_Socia INT,
            Id_Caja INT
        );
    """)

    cursor.execute("""
        CREATE TABLE Cuotas_prestamo(
            Id_Cuota INT AUTO_INCREMENT PRIMARY KEY,
            Id_Prestamo INT,
            Numero_cuota INT,
            Fecha_programada DATE,
            Monto_cuota DECIMAL(10,2),
            Estado VARCHAR(20),
            Id_Caja INT
        );
    """)

    cursor.execute("""
        CREATE TABLE Gastos_grupo(
            Id_Gasto INT AUTO_INCREMENT PRIMARY KEY,
            Fecha_gasto DATE,
            Descripcion TEXT,
            Monto DECIMAL(10,2),
            Responsable VARCHAR(100),
            DUI VARCHAR(10),
            Id_Caja INT
        );
    """)

    cursor.execute("""
        CREATE TABLE caja_general(
            id INT PRIMARY KEY,
            saldo_actual DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE caja_reunion(
            id_caja INT AUTO_INCREMENT PRIMARY KEY,
            fecha DATE,
            saldo_inicial DECIMAL(10,2),
            ingresos DECIMAL(10,2),
            egresos DECIMAL(10,2),
            saldo_final DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE caja_movimientos(
            id_mov INT AUTO_INCREMENT PRIMARY KEY,
            id_caja INT,
            tipo VARCHAR(20),
            categoria VARCHAR(255),
            monto DECIMAL(10,2)
        );
    """)

    # ---------------------------------------------------------------
    # 3. INSERTAR LA CAJA GENERAL INICIAL
    # ---------------------------------------------------------------
    cursor.execute("INSERT INTO caja_general VALUES (1, 0.00)")

    con.commit()
    print("✔ BASE DE DATOS REINICIADA COMPLETAMENTE 🧨")


# Ejecutar si se corre directamente
if __name__ == "__main__":
    ejecutar_reset_total()
