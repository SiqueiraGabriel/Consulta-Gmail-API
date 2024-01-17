from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# IModificar o escopo de atuacao - Neste caso pode se utilizar .readonly (apenas ler): 
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
  
# Credencias da API
creds = None

# Caso tenha as credencias salvo no arquivo - 1ª vez necessita permitir as credenciais
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# Se não houver o token ou não for válida
if not creds or not creds.valid:

    # Se já foi rodado uma vez, pode liberar a sessão após expiração
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # Recupera as credencias no arquivo, vai abrir o navegador para permitir o acesso
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)

    # Salvar as credenciasi de acesso - Salvar os dados da api
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    result2 = service.users().messages().list(userId='me').execute()

except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f'An error occurred: {error}')