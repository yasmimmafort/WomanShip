import pandas as pd
import os
import glob
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

multas_df = pd.read_csv('multas_portuarias_atualizado.csv')
portos_df = pd.read_csv('portos.csv')
rotas_df = pd.read_csv('rotas.csv')
taxas_df = pd.read_csv('taxas_portuarias.csv')

xml_dir = "/rastreamento_navios"

navios_data = []

#Extração arquivo xml
for xml_file in glob.glob(os.path.join(xml_dir, "*.xml")):
    with open(xml_file, 'r') as file:
        soup = BeautifulSoup(file, 'xml')
        navio_id = soup.find('Navio')['ID']
        nome_navio = soup.find('Nome').text
        pontos_de_dados = soup.find_all('PontoDeDados')
        for ponto in pontos_de_dados:
            timestamp = ponto['Timestamp']
            latitude = ponto.find('Latitude').text
            longitude = ponto.find('Longitude').text
            velocidade = ponto.find('Velocidade').text
            direcao = ponto.find('Direcao').text
            status = ponto.find('Status').text
            navios_data.append([navio_id, nome_navio, timestamp, latitude, longitude, velocidade, direcao, status])

navios_df = pd.DataFrame(navios_data, columns=['ID_Navio', 'Nome_Navio', 'Timestamp', 'Latitude', 'Longitude', 'Velocidade', 'Direcao', 'Status'])

#Transformação de dados

multas_df.fillna({'Valor': 0}, inplace=True)

multas_df['Data_Multa'] = pd.to_datetime(multas_df['Data_Multa'])

#Carregamento de Dados

engine = create_engine('mysql:///logistica.db')

# Carregar os dados
multas_df.to_sql('multas_portuarias', engine, if_exists='append', index=False)
portos_df.to_sql('portos', engine, if_exists='append', index=False)
rotas_df.to_sql('rotas', engine, if_exists='append', index=False)
taxas_df.to_sql('taxas_portuarias', engine, if_exists='append', index=False)
navios_df.to_sql('rastreamento_navios', engine, if_exists='append', index=False)
