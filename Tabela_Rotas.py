import pandas as pd
import mysql.connector

def converter_distancia(distancia):
    distancia_inteira = int(distancia)
    distancia_km = distancia_inteira * 1.852
    return round(distancia_km, 2)


def converter_tempo_medio(tempo_medio):
    rounded_tempo_medio = round(tempo_medio, 2)
    integer_part = int(rounded_tempo_medio)
    decimal_part = rounded_tempo_medio - integer_part
    minutes = int(decimal_part * 60)
    seconds = int((decimal_part * 60 - minutes) * 60)

    formatted_time = f'{integer_part}:{minutes:02}:{seconds:02}'

    return formatted_time

username = 'username'
password = 'password'
host = 'localhost'  # ou '127.0.0.1'
database = 'database'

conn = mysql.connector.connect(
    host=host,
    user=username,
    password=password,
    database=database
)

if conn.is_connected():
    print('Conectado ao MySQL')

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS rotas (
        ID_Rota INT PRIMARY KEY,
        Porto_Origem VARCHAR(255),
        Porto_Destino VARCHAR(255),
        Distancia DECIMAL(10, 2),
        Tempo_Medio VARCHAR(20)
    )
""")

rotas_df = pd.read_csv('rotas.csv')

rotas_df['Distancia'] = rotas_df['Distancia'].apply(converter_distancia)

rotas_df['Tempo_Medio'] = rotas_df['Tempo_Medio'].apply(converter_tempo_medio)

for index, row in rotas_df.iterrows():
    cursor.execute("""
        INSERT INTO rotas (ID_Rota, Porto_Origem, Porto_Destino, Distancia, Tempo_Medio)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Porto_Origem=VALUES(Porto_Origem),
            Porto_Destino=VALUES(Porto_Destino),
            Distancia=VALUES(Distancia),
            Tempo_Medio=VALUES(Tempo_Medio)
    """, tuple(row))

conn.commit()

print("Dados inseridos com sucesso na tabela rotas!")



cursor.close()
conn.close()
