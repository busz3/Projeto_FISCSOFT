import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost', user='root', password='', database='fiscsoft'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT matricula, nome_agente, login, perfil, status FROM `agente ibama`")
    usuarios = cursor.fetchall()

    if usuarios:
        print("Usuarios encontrados:")
        for u in usuarios:
            print(f"  Matricula: {u[0]} | Nome: {u[1]} | Login: {u[2]} | Perfil: {u[3]} | Status: {u[4]}")
    else:
        print("Nenhum usuario encontrado. Criando usuario de teste...")
        cursor.execute(
            "INSERT INTO `agente ibama` (matricula, nome_agente, cpf, email, telefone, login, senha, perfil, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ativo')",
            (1, "Admin Teste", "00000000000", "admin@teste.com", "00000000000", "admin", "1234", "admin")
        )
        conn.commit()
        print("Usuario criado com sucesso!")
        print("  Login: admin | Senha: 1234")

    conn.close()
except Error as e:
    print(f"Erro: {e}")
