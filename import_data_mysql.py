import pandas as pd
import glob
import os
import mysql.connector
import xml.etree.ElementTree as ET


cnx = mysql.connector.connect(user='usuario', password='senha', host='localhost', database='banco de dados', auth_plugin='mysql_native_password')
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
        tipo_carga = str(row['Tipo de Carga']) if 'Tipo de Carga' in df.columns else None
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


cursor.execute("""
CREATE TABLE IF NOT EXISTS navios (
    id_navio VARCHAR(255) NOT NULL,
    nome_navio VARCHAR(255) NOT NULL,
    timestamp VARCHAR(255) NOT NULL,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    velocidade VARCHAR(255) NOT NULL,
    direcao VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_navio, timestamp)
)
""")


def safe_str(value):
    return str(value) if value is not None else ''


xml_files = glob.glob("rastreamento_navios/*.xml")
for file in xml_files:
    tree = ET.parse(file)
    root = tree.getroot()
    id_navio = safe_str(root.attrib.get('ID'))
    nome_navio = safe_str(root.find('Nome').text)
    for ponto_de_dados in root.findall('.//PontoDeDados'):
        timestamp = safe_str(ponto_de_dados.get('Timestamp'))
        latitude = safe_str(ponto_de_dados.find('Latitude').text)
        longitude = safe_str(ponto_de_dados.find('Longitude').text)
        velocidade = safe_str(ponto_de_dados.find('Velocidade').text)
        direcao = safe_str(ponto_de_dados.find('Direcao').text)
        status = safe_str(ponto_de_dados.find('Status').text)
        query = """
        INSERT INTO navios (id_navio, nome_navio, timestamp, latitude, longitude, velocidade, direcao, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (id_navio, nome_navio, timestamp, latitude, longitude, velocidade, direcao, status)
        cursor.execute(query, values)

current_dir = os.getcwd()
csv_files = glob.glob(os.path.join(current_dir, "taxas", "*.csv"))
for file in csv_files:
    table_name = os.path.splitext(os.path.basename(file))[0]
    df = pd.read_csv(file)
    df = df.fillna('')
    columns = ', '.join([f"{col} VARCHAR(255) NOT NULL" for col in df.columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
    placeholders = ', '.join(['%s'] * len(df.columns))
    query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"
    values = [tuple(row) for row in df.values]
    cursor.executemany(query, values)

cnx.commit()
cursor.close()
cnx.close()
