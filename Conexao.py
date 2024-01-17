import mysql.connector

class Conexao:
    
    def __init__(self, host, user, password, database):
        try:
            self.conexao = mysql.connector.connect(host=host, user=user, password=password, database=database)
            self.cursor = self.conexao.cursor()
        except:
            print("Erro na Conexão")
        else:
            print("Conexao estabelecida com sucesso")
        
    def select(self, script):
        self.cursor.execute(script)
        result = self.cursor.fetchall()
        if result != []:
            return result[0]
        else:
            return result
    
    def manipulation(self, script):
        self.cursor.execute(script)
        self.conexao.commit()