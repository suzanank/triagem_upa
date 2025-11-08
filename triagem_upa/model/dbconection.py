import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="triagem_upa"
        )
        if conexao.is_connected():
            print("Conexão com o banco de dados realizada com sucesso.")
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    

conectar()