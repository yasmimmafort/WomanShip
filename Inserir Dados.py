import pandas as pd
import glob
import os
import mysql.connector
import xml.etree.ElementTree as ET


cnx = mysql.connector.connect(user='root', password='Sh@dow2001', host='localhost', database='logistica', auth_plugin='mysql_native_password')
cursor = cnx.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS tipos_navio (
    nome_navio VARCHAR(255),
    data VARCHAR(255),
    porto VARCHAR(255),
    tipo_custo VARCHAR(255),
    valor VARCHAR(255),
    descricao VARCHAR(255),
    tipo_carga VARCHAR(255),
    volume VARCHAR(255)
)
""")


xlsx_files = glob.glob("tipos_navio/*.xlsx")

for file in xlsx_files:
    df = pd.read_excel(file)
    df = df.fillna('')
    if 'Volume' not in df.columns:
        df['Volume'] = ''
    for _, row in df.iterrows():
        if 'Tipo de Carga' not in df.columns:
            tipo_carga = ''
        else:
            tipo_carga = str(row['Tipo de Carga'])
        query = """
        INSERT INTO tipos_navio (nome_navio, data, porto, tipo_custo, valor, descricao, tipo_carga, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            str(row['Nome do Navio']), str(row['Data']), str(row['Porto']),
            str(row['Tipo de Custo']), str(row['Valor (USD)']), str(row['Descrição']),
            tipo_carga, str(row['Volume'])
        )
        cursor.execute(query, values)


xml_files = glob.glob("rastreamento_navios/*.xml")

for file in xml_files:
    tree = ET.parse(file)
    root = tree.getroot()
    nome_navio = root.find('Nome').text
    for ponto_de_dados in root.findall('Rastreamento/PontoDeDados'):
        timestamp = ponto_de_dados.get('Timestamp')
        latitude = ponto_de_dados.find('Latitude').text
        longitude = ponto_de_dados.find('Longitude').text
        velocidade = ponto_de_dados.find('Velocidade').text
        direcao = ponto_de_dados.find('Direcao').text
        status = ponto_de_dados.find('Status').text



current_dir = os.getcwd()


csv_files = glob.glob(os.path.join(current_dir, "taxas", "*.csv"))


for file in csv_files:
    table_name = os.path.splitext(os.path.basename(file))[0]
    df = pd.read_csv(file)
    df = df.fillna('')
    columns = ', '.join([f"{col} VARCHAR(255)" for col in df.columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
    placeholders = ', '.join(['%s'] * len(df.columns))
    query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"
    values = [tuple(row) for row in df.values]
    cursor.executemany(query, values)


cnx.commit()
cursor.close()
cnx.close()
