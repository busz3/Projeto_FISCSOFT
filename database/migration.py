import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='fiscsoft'
    )
    if conn.is_connected():
        cursor = conn.cursor()

        cursor.execute("SHOW COLUMNS FROM `agente ibama`")
        colunas = [c[0] for c in cursor.fetchall()]
        print("Colunas atuais:", colunas)

        if "login" not in colunas:
            cursor.execute("ALTER TABLE `agente ibama` ADD COLUMN `login` VARCHAR(100) NOT NULL AFTER `telefone`")
            print("Coluna login adicionada")

        if "perfil" not in colunas:
            cursor.execute("ALTER TABLE `agente ibama` ADD COLUMN `perfil` ENUM('admin','operador','agente') NOT NULL DEFAULT 'agente' AFTER `login`")
            print("Coluna perfil adicionada")

        if "status" not in colunas:
            cursor.execute("ALTER TABLE `agente ibama` ADD COLUMN `status` ENUM('ativo','inativo') NOT NULL DEFAULT 'ativo' AFTER `perfil`")
            print("Coluna status adicionada")

        conn.commit()

        cursor.execute("SHOW COLUMNS FROM `agente ibama`")
        print("\nEstrutura final:")
        for c in cursor.fetchall():
            print(f"  {c[0]} - {c[1]}")

        conn.close()
        print("\nMigration concluida com sucesso!")

except Error as e:
    print(f"Erro: {e}")
