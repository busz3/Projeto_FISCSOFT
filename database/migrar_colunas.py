import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config.database import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def migrar():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor()

        colunas_necessarias = {
            "data_cadastro": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "ultimo_acesso": "DATETIME DEFAULT NULL",
            "cadastrado_por": "VARCHAR(100) DEFAULT NULL",
            "atualizado_por": "VARCHAR(100) DEFAULT NULL",
        }

        cursor.execute("SHOW COLUMNS FROM `agente ibama`")
        colunas_existentes = {row[0] for row in cursor.fetchall()}

        for nome, definicao in colunas_necessarias.items():
            if nome not in colunas_existentes:
                cursor.execute(f"ALTER TABLE `agente ibama` ADD COLUMN {nome} {definicao}")
                print(f"Coluna '{nome}' adicionada com sucesso.")
            else:
                print(f"Coluna '{nome}' ja existe.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Migracao concluida!")
    except Exception as e:
        print(f"Erro na migracao: {e}")

if __name__ == "__main__":
    migrar()
