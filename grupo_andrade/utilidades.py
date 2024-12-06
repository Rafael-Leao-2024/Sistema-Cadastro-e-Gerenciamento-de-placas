from datetime import datetime
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