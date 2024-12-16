from datetime import datetime
from grupo_andrade import mail
from flask_mail import Message
from flask import url_for, render_template
import pytz

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


def enviar_email(user, placa):
    mensagem = Message(
        'Solicitação de Placa', 
        sender=(user.username, user.email), 
        reply_to=user.email,
        recipients=['rafaelampaz6@gmail.com']
    )
    
    mensagem.body = f'''
Olá Grupo Andrade,

Segue abaixo os detalhes da solicitação da placa:

Placa: {placa.placa.upper()}
RENAVAM: {placa.renavan}
CRLV: {placa.crlv}
Endereço de entrega: {placa.endereco_placa.title()}

Você pode acessar os detalhes completos da solicitação pelo link abaixo:

{url_for('placa_detail', placa_id=placa.id, _external=True)}

Atenciosamente {user.username.lower()},
Equipe de Atendimento
'''   
    mail.send(mensagem)
