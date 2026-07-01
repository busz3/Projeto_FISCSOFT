import mysql.connector

conn = mysql.connector.connect(host="localhost", user="root", password="", database="fiscsoft")
c = conn.cursor()

try:
    c.execute("ALTER TABLE `agente ibama` ADD COLUMN perfil VARCHAR(30) DEFAULT 'Agente' AFTER status")
    print("Coluna 'perfil' adicionada")
except Exception as e:
    print(f"Coluna perfil: {e}")

c.execute("UPDATE `agente ibama` SET perfil = 'Administrador' WHERE login = 'admin'")
c.execute("UPDATE `agente ibama` SET perfil = 'Agente' WHERE login IN ('maria', 'pedro')")
conn.commit()

c.execute("SELECT login, nome_agente, perfil, status FROM `agente ibama`")
for row in c.fetchall():
    print(f"  {row}")

conn.close()
