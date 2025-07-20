from flask_mail import Message
from flask import url_for
from dotenv import load_dotenv
from grupo_andrade.main import mail
import requests
import pytz
import os

load_dotenv()

def format_data(dt):
    """Converte a data para o horário local e formata para exibição."""
    local_tz = pytz.timezone('America/Recife')  # Substitua pelo seu fuso horário
    utc_dt = dt.replace(tzinfo=pytz.utc)  # Assume que a data está em UTC
    local_dt = utc_dt.astimezone(local_tz)  # Converte para o horário local
    return local_dt.strftime('%d/%m/%Y')  # Formato desejado


def format_hora(dt):
    """Converte a data para o horário local e formata para exibição."""
    local_tz = pytz.timezone('America/Recife')  # Substitua pelo seu fuso horário
    utc_dt = dt.replace(tzinfo=pytz.utc)  # Assume que a data está em UTC
    local_dt = utc_dt.astimezone(local_tz)  # Converte para o horário local
    return local_dt.strftime('%H:%M:%S')  # Formato desejado


def format_data_completa(dt):
    """Converte a data para o horário local e formata para exibição."""
    local_tz = pytz.timezone('America/Recife')  # Substitua pelo seu fuso horário
    utc_dt = dt.replace(tzinfo=pytz.utc)  # Assume que a data está em UTC
    local_dt = utc_dt.astimezone(local_tz)  # Converte para o horário local
    return local_dt.strftime('%d/%m/%Y %H:%M:%S.%f')  # Formato desejado


def enviar_email(user, placas):
    mensagem = Message(
        subject='Solicitação de Placas', 
        sender=(user.username, user.email), 
        recipients=['rafaelampaz6@gmail.com']
    )
    detalhes_placas = ""
    for placa in placas:
        detalhes_placas += f'''
Placa:  {placa.placa.upper()}
RENAVAM:{placa.renavan}
CRLV:   {placa.crlv}
Endereço de entrega: {placa.endereco_placa.title()}
Link para detalhes: {url_for('placa_detail', placa_id=placa.id, _external=True)}
'''
    mensagem.body = f'''
Olá Grupo Andrade,
Segue abaixo os detalhes das solicitações de placas:
{detalhes_placas}

Atenciosamente,
{user.username}
Equipe de Atendimento
'''
    mail.send(mensagem)


def pegar_status(payment_id):    
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    PROD_ACCESS_TOKEN = os.environ.get('PROD_ACCESS_TOKEN')
    headers = {
        "Authorization": f"Bearer {PROD_ACCESS_TOKEN}" 
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    valor_pago = None

    if response.status_code == 200 and response.json().get('status') == 'approved':
        payment_info = response.json()  # Converte a resposta para JSON
        status_pagamento = payment_info['status']
        id_pagamento = payment_info['point_of_interaction']['transaction_data']['transaction_id']
        valor_pago = payment_info.get('transaction_amount')
    else:
        payment_info = response.json() 
        status_pagamento = payment_info.get('status')
        id_pagamento = payment_id
    return valor_pago, id_pagamento, status_pagamento


def verificar_email(email):
    CHAVE_API_DE_EMAIL = os.environ.get('CHAVE_API_DE_EMAIL')
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={CHAVE_API_DE_EMAIL}"    
    response = requests.get(url)
    dados = response.json()
    return dados.get('data', {}).get('status') == 'valid' or dados.get('data', {}).get('status') == 'accept_all'


