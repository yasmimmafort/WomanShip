import pandas as pd
import pymysql
import xml.etree.ElementTree as ET
import glob
import os

# Função para ler arquivos XML
def read_xml_files(path):
    xml_data = []
    for xml_file in glob.glob(f"{path}/*.xml"):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        xml_data.append(root)
    return xml_data

# Função para ler arquivos Excel
def read_excel_files(path):
    excel_data = []
    for excel_file in glob.glob(f"{path}/*.xlsx"):
        df = pd.read_excel(excel_file)
        excel_data.append(df)
    return excel_data

# Função para ler arquivos CSV
def read_csv_files(path):
    csv_data = []
    for csv_file in glob.glob(f"{path}/*.csv"):
        df = pd.read_csv(csv_file)
        csv_data.append(df)
    return csv_data

# Caminhos para os diretórios
current_dir = os.path.dirname(os.path.abspath(__file__))
xml_path = os.path.join(current_dir, 'rastreamento_navios')
excel_path_tipos_navio = os.path.join(current_dir, 'tipos_navio')
csv_path_taxas = os.path.join(current_dir, 'taxas')

# Ler os arquivos
xml_data = read_xml_files(xml_path)
excel_data_tipos_navio = read_excel_files(excel_path_tipos_navio)
csv_data_taxas = read_csv_files(csv_path_taxas)

# Função para transformar dados XML em um DataFrame estruturado
def transform_xml_to_dataframe(xml_data):
    rows = []
    for root in xml_data:
        navio_id = root.attrib.get('ID')
        navio_nome = root.find('Nome').text
        # Pegar apenas a primeira ocorrência de rastreamento
        rastreamento = root.find('Rastreamento/PontoDeDados')
        if rastreamento is not None:
            timestamp = rastreamento.attrib.get('Timestamp')
            # Converter o timestamp para o formato adequado
            timestamp = pd.to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'NavioID': navio_id,
                'Nome': navio_nome,
                'Timestamp': timestamp,
                'Latitude': rastreamento.find('Latitude').text,
                'Longitude': rastreamento.find('Longitude').text,
                'Velocidade': rastreamento.find('Velocidade').text,
                'Direcao': rastreamento.find('Direcao').text,
                'Status': rastreamento.find('Status').text
            }
            rows.append(row)
    df = pd.DataFrame(rows)
    df.drop_duplicates(inplace=True)
    return df

# Transformar os dados XML
xml_df = transform_xml_to_dataframe(xml_data)

# Função para padronizar os dados de custos em Excel
def standardize_excel_data(excel_data):
    standardized_data = []
    for df in excel_data:
        df['Valor (USD)'] = df['Valor (USD)'].apply(lambda x: float(str(x).replace(',', '.')))
        standardized_data.append(df)
    return standardized_data

# Padronizar os dados Excel
standardized_excel_data = standardize_excel_data(excel_data_tipos_navio)

# Função para tratar dados ausentes e inconsistências nos dados CSV
def clean_csv_data(csv_data):
    cleaned_data = []
    for df in csv_data:
        df.fillna(0, inplace=True)
        cleaned_data.append(df)
    return cleaned_data

# Tratar dados CSV
cleaned_csv_data = clean_csv_data(csv_data_taxas)

# Conectar ao banco de dados MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Sh@dow2001',
    db='logistica',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Função para criar tabelas
def create_table(df, table_name, connection):
    columns = ', '.join([f'`{col}` VARCHAR(255)' for col in df.columns])
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    with connection.cursor() as cursor:
        cursor.execute(sql)
    connection.commit()

# Função para inserir dados
def insert_data(df, table_name, connection):
    columns = ', '.join([f'`{col}`' for col in df.columns])
    values_placeholder = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder})"

    with connection.cursor() as cursor:
        for row in df.itertuples(index=False, name=None):
            # Substituir NaN por None
            row = tuple(None if pd.isna(x) else x for x in row)
            cursor.execute(sql, row)
    connection.commit()

# Criar tabela rastreamento_navios
create_table(xml_df, 'rastreamento_navios', connection)

# Inserir dados na tabela rastreamento_navios
insert_data(xml_df, 'rastreamento_navios', connection)

# Criar tabelas e inserir dados para os arquivos Excel
for i, df in enumerate(standardized_excel_data):
    table_name = f'tipos_navio_{i+1}'
    create_table(df, table_name, connection)
    insert_data(df, table_name, connection)

# Criar tabelas e inserir dados para os arquivos CSV
for i, df in enumerate(cleaned_csv_data):
    table_name = f'taxas_{i+1}'
    create_table(df, table_name, connection)
    insert_data(df, table_name, connection)

# Fechar a conexão
connection.close()
