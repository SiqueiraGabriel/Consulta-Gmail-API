import pandas as pd
from Conexao import *
from GmailAPI import *

class Email:
    
    def __init__(self, userId = 'me', maxResults = 500, proxPage = ""):
        self.cadastro_variaveis_iniciais()
        self.busca_informacaoes_email(userId, maxResults, proxPage)
        
        # Se encontrar dados a ser cadastrados no BD
        if len(self.all_email) != 0:
            self.tratamento_dados()
            self.cadastrar_dados_bd()
        else:
            print("Dados atualizados")
        
        # Obter as informações apenas da caixa de entrada
        self.obter_email_caixa_entrada()
        print("Atualizado os emails da Caixa de Entrada")


    def cadastro_variaveis_iniciais(self):
        """
        # Função responsável por cadastrar as variáveis que serão utilizadas ao decorrer do código
        """
         # Responsável por armazenar todas os id de email
        self.all_id_emails = []
        
        # Responsável por armazenar as informações dos emails
        self.all_email = []
        
        # Estabelecer a conexão com o Banco de Dados
        self.conexao = Conexao(host="localhost", user="root", password="", database ="dashboard_gmail")
        
        # Obter o id do último email cadastrado
        if self.conexao.select("SELECT idEmail from Email order by data_email DESC limit 1;") != []:
            self.id_ultimo_email = self.conexao.select("SELECT idEmail from Email order by data_email DESC limit 1;")[0]
        else:
            self.id_ultimo_email = ""
    
    def busca_informacaoes_email(self, userId, maxResults, proxPage):
        """
        # Função responsável por realizar a busca de todas as informações do email
        """
        
        # Buscar o id dos emails, até se chegar ao ultimo id cadastrado no BD
        self.buscar_todos_id_emails(userId, maxResults, proxPage)
        
        # Obter os dados como título e emitente do email
        self.obter_informacoes_email_especifico(userId)
        
        # Armazenar os dados obtidos num Dataframe que será encaminhado ao BD
        self.all_email = pd.DataFrame(self.all_email)

    def cadastrar_dados_bd(self):
        """
        # Função responsável por encaminhar as informações ao BD
        """
        
        # Cadastrar as informações do Email
        self.adicionar_email_bd()
        
        # Vincular o email a Label
        self.adicionar_email_label_bd()
        print("Dados Cadastrados com sucesso!")
    
    def obterDados(self,lista, item):
        """
        # Função responsável por selecionar apenas um valor da lista, utiliza validação caso o valor não exista
        """
        try:
            return lista[item]# Id da mensagem
        except:
            return ""
        
# ---------------------------->> BUSCA DADOS NA API DO GMAIL <<-----------------------------------------------

        
    def buscar_intervalor_id_email_api(self, proxPage=""):
        """
        # Função responsveál por buscar intervalo de id dos emails, a partir da página passada por parâmetro
        """
        if proxPage == "":
            return service.users().messages().list(userId='me',maxResults=500).execute()
        else:
            return service.users().messages().list(userId='me',maxResults=500, pageToken=proxPage).execute()
    
    def selecionar_id_emails(self, lista_emails):
        """
        # Do arquivo Json com as informações do email, vai obter apenas o id e armazenar na variável para futuras consultas
        """
        
        for i in lista_emails['messages']: 
            
            # Verifica se o email já está cadastrado, se é igual ao último 
            if i['id'] == self.id_ultimo_email:
                return False
            else:
                self.all_id_emails.append(i['id']) 
    
                    
    def buscar_todos_id_emails(self, userId = 'me', maxResults = 500, proxPage = ""):
        """
        # Função responsável por realizar as requisições na API dos id dos Emails disponíveis
        """
        while True:
            
            # Armazena o conjunto de idEmail de uma determinada página
            intervalo = self.buscar_intervalor_id_email_api(proxPage)
            
            # Verificar se já foi encantrado o último Id, para encerrar a lista de busca
            if self.selecionar_id_emails(intervalo) == False:
                break
            else:
                # Pegar do arquivo Json, a próxima página disponível para consulta
                proxPage = self.obterDados(intervalo, 'nextPageToken')
                
                # Caso não existir mais páginas
                if proxPage == "":
                    break
                              
    def obter_informacoes_email_especifico(self, userId="me"):
        """
        # Função responsável por percorrer todos os emails obtidos a partir do intervalo, a fim de obter as informações que será encaminhado ao BD
        """
        
        # Loop for para acessar cada email e armazenar suas informações num dataframe
        for id_email in self.all_id_emails[0:100]:
            print(f"ID do Email: {id_email}")
            
            # Variável responsável por armazenas as informações que serão selecionadas do email
            aux_email =  {}
            
            # Variável reposnável para auxiliar nas informações do cabeçalho do email
            aux_header = {} 
            
            # Realizar a requisição na API, para obter as informações específicas do email
            dados_email = service.users().messages().get(userId='me', id=id_email, format='metadata').execute()

            # ------>>  Obter os dados para armazenar no BD << ------
            aux_email['idEmail'] = dados_email['id']
            
            # Obter as labels do email
            aux_email['label'] = dados_email['labelIds'] 
            
            # Obter pequeno resumo do conteúdo do email
            aux_email['resumo'] = dados_email['snippet'].replace("'", "") 
            
            # Obter as informações do header do email
            header_list = dados_email['payload']['headers']

            # Transformar header em dicionario
            for i in header_list:
                aux_header[i['name']] = i['value']

            # Obter as informações específicas do email
            aux_email['destinatario'] = self.obterDados(aux_header,'Delivered-To')# Pessoa que recebeu o email
            aux_email['data']  = self.obterDados(aux_header,'Date') # Recuperar a data do email
            aux_email['titulo'] = self.obterDados(aux_header,'Subject').replace("'", "") # Título do email
            aux_email['emitente'] = self.obterDados(aux_header,'From') # Emitente
            aux_email['mensagemId'] = self.obterDados(aux_header,'Message-ID') # Id da mensagem
            
            # Adicionar as informações obtidas no Dataframe com todas os email
            self.all_email.append(aux_email)
            
            # A fim de teste, mostrar em qual email está buscando
            print(len(self.all_email))
                
                
# ---------------------------->> FORMATACAO DOS DADOS <<-----------------------------------------------
        
    def formatar_data(self, lista):
        """
        # Função responsável por realizar o tratamento da data de uma determinada lista, removendo informações do fuso horário, deixando apenas data e hora
        """
        
        for i in range(0, len(lista)):

            # Verificar se a data apresenta o dia da semana
            if (',' in lista[i]) == False:
                aux = ["",lista[i]][1]
            else:
                # Obter a data, desconsiderando o dia da semana
                aux = lista[i].split(",")[1]

            # Separar onde as colunas apresentam o fusso horário
            if "+" in aux:
                aux = aux.split('+')
            elif "-" in aux:
                aux = aux.split("-")
            else:
                aux = aux.split("GMT")

            # Atribuir a lista o valor formatado
            lista[i] = aux[0].strip()

        # Retorna os valores já tratados    
        return lista

    def formatar_remetente(self, lista):
        """
        # Função responsável por quebrar as informações do email do remetente, a fim de obter o email, nome e domínio
        """
        
        remetente = [[],[],[]]

        for i in range(0, len(lista)):
    
            # Se houver o nome do remetente
            if ('<' in lista[i]) == True:
                aux = lista[i].replace(">","").split("<")
                remetente[0].append(aux[0].replace('"',"").strip()) # Obter o Nome do emitente
                remetente[1].append(aux[1]) # Obter o email do remetente
                remetente[2].append((aux[1].split("@"))[1]) # Obter o domínio do emitente
            else:
                remetente[0].append("Outro")
                remetente[1].append("outro")
                remetente[2].append("outro.com")

        return remetente

    def formatar_link(self, lista):
        """
        # Função responsável por criar o link do email, a partir de uma busca a partir do código do email
        """
        
        for i in range(0, len(lista)):
            aux = str(lista[i]).replace("<","").replace(">","") # Retirar os caracteres inválidos
            lista[i] = f'https://mail.google.com/mail/u/2/#search/rfc822msgid:{aux}' 
        
        # Retorna o link formatado
        return lista

    
    def separar_email_label(self, lista):
        """
        # Função responsável por converter a string com as labels do email numa lista a ser enviada ao BD
        """
        

        # Dicionário responsável por armazenar os valores da Label e seu respectivo email
        self.email_label = {'idEmail':[], 'idLabel': []}

        for i in range(0, len(lista)):

            # Obter os valores iniciais
            idEmail = lista.idEmail.iloc[i]
            labels = str(lista.label.iloc[i]).replace("[", "").replace("]","").replace("'","").split(",")

            #Separar as labels a partir do id do Email
            for label in labels:
                self.email_label['idEmail'].append(idEmail)
                self.email_label['idLabel'].append(label.strip())

    def tratamento_dados(self):
        """
        # Função responsável por tratar os dados do email antes de encaminhar ao BD
        """
        
        # Formatar o link dos email
        self.all_email.mensagemId = self.formatar_link(self.all_email.mensagemId)
        
        # Formatar a data
        self.all_email.data = pd.to_datetime(self.formatar_data(self.all_email.data))
        
        # Formatar as informações do emitente
        emitente =  self.formatar_remetente(self.all_email.emitente)
        self.all_email["emitente_nome"] = emitente[0]
        self.all_email["emitente_email"] = emitente[1]
        self.all_email["emitente_dominio"] = emitente[2]
        self.all_email = self.all_email.drop("emitente", axis=1)
        
        # Separar as informações da Label e vincular ao id do Email
        self.separar_email_label(lista=self.all_email[['idEmail', 'label']])
        
# ---------------------------->> ENVIO AO BD <<-----------------------------------------------
    
    def adicionar_email_bd(self):
        """
        # Função responsável por encaminhar as informações obtidas no banco de dados
        """
        
        # Lista com todos os emails obtidos
        emails = self.all_email

        for i in range(0, len(emails)):
            print(i)

            # Verificar se a emitente dominio já existe
            if self.conexao.select(f"SELECT * FROM Empresa where email_dominio = '{emails.iloc[i].emitente_dominio }';") == []:
                self.conexao.manipulation(f"INSERT INTO Empresa(email_dominio) values ('{emails.iloc[i].emitente_dominio}');")
                print("Cadastrado Empresa")
                
            idEmpresa = self.conexao.select(f"SELECT idEmpresa FROM Empresa where email_dominio = '{emails.iloc[i].emitente_dominio }';")[0]

            # Verificar se o emitente já foi cadastrado 
            if self.conexao.select(f"SELECT * FROM Emitente where email = '{emails.iloc[i].emitente_email}';") == []:
                self.conexao.manipulation(f"INSERT INTO Emitente(nome, email, idEmpresa) values('{emails.iloc[i].emitente_nome}','{emails.iloc[i].emitente_email}','{idEmpresa}');")
                print("Cadastrado Emitente")

                
            idEmitente = self.conexao.select(f"SELECT idEmitente FROM Emitente where email = '{emails.iloc[i].emitente_email}';")[0]

            try:
                # Verificar se o email já foi cadastrado
                if conexao.select(f"SELECT * FROM Email where idEmail = '{emails.iloc[i].idEmail}';") == []:
                    self.conexao.manipulation(f"INSERT INTO Email(idEmail, titulo, resumo, data_email, destinatario_email, link, idEmitente) values('{emails.iloc[i].idEmail}','{emails.iloc[i].titulo}','{emails.iloc[i].resumo}', '{emails.iloc[i].data}','{emails.iloc[i].destinatario}', '{emails.iloc[i].mensagemId}','{idEmitente}');")  
            except:
                print("Erro ao cadastrar um email.")
                print(f"INSERT INTO Email(idEmail, titulo, resumo, data_email, destinatario_email, link, idEmitente) values('{emails.iloc[i].idEmail}','{emails.iloc[i].titulo}','{emails.iloc[i].resumo}', '{emails.iloc[i].data}','{emails.iloc[i].destinatario}', '{emails.iloc[i].mensagemId}','{idEmitente}');")  
                    
    def adicionar_labels_bd(self):
        """
        # Função responsável por adicionar todas as labels disponíveis ao BD
        """
    
        # Requisição a API, a fim de obter todas as labels
        labels = pd.DataFrame(service.users().labels().list(userId='me').execute()['labels'])[['id','name']]

        for i in range(0, len(labels)):
            if conexao.select(f"SELECT idLabel from Label where nome = '{labels.iloc[i]['name']}';") == []:
                print(f"INSERT INTO Label(idLabel, nome) values('{labels.iloc[i].id}','{labels.iloc[i]['name']}');")

    def adicionar_email_label_bd(self):
        """
        # Função responsável por cadastrar as informações da tabela email_label (entidade associativa de Email com a Label)
        """
        # Verificar o cadastro das labels
        self.adicionar_labels_bd()
        
        email_label = pd.DataFrame(self.email_label)
        
        try:
            for i in range(0, len(email_label)):
                # Verifica se já foi realizado a ligacao
                if self.conexao.select(f"SELECT * FROM Email_Label where idLabel = '{email_label.iloc[i].idLabel}' & idEmail = '{email_label.iloc[i].idEmail}';") == []:
                    self.conexao.manipulation(f"{email_label.iloc[i].idEmail}', '{email_label.iloc[i].idLabel}")
        except:
            print(f"Houve um erro ao cadastrar a Label {email_label}")
            
    def obter_email_caixa_entrada(self):
        """
        # Função responsável por obter todos os email presentes na caixa de entrada do Email
        """
        try:
            # Realizar a busca dos Ids de emails que estão na caixa de entrada
            aux = service.users().messages().list(userId='me',maxResults=500, labelIds="INBOX").execute()["messages"]
            df_caixaEntrada = []

            # Recuperar as informações da tabela Email (evitar buscar novamente)
            for item in aux:
                df_caixaEntrada.append(self.conexao.select(f"SELECT idEmail, titulo, data_email, destinatario_email, idEmitente FROM Email where idEmail = '{item['id']}';"))

            # Cadastrar as informações no BD (desconsidera títulos repetidos)
            self.cadastrar_bd_caixa_entrada(pd.DataFrame(df_caixaEntrada).drop_duplicates(subset=1))
        except Exception as erro:
            print("Não Apresenta nenhum email na caixa de Entrada (OBAA)")

    def cadastrar_bd_caixa_entrada(self, df_caixaEntrada):
    
        # Excluir todos os emails da Caixa de Entrada (bd)
        self.conexao.manipulation("delete from caixa_entrada;")

        # Adicionar os emails na caixa de entrada no BD
        for i in range(len(df_caixaEntrada)):
            aux = df_caixaEntrada.iloc[i]
            self.conexao.manipulation(f"INSERT INTO caixa_entrada(idCaixEntrada, titulo, data_email, destinatario_email, idEmitente) values(