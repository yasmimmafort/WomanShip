# WomanShip
Projeto final do curso de engenharia de dados com objetivo de melhorar a logística de transportes maritimos

# Importação de Dados para MySQL

Este script Python foi desenvolvido para importar dados de diferentes fontes (Excel, XML e CSV) para um banco de dados MySQL. Ele automatiza o processo de criação de tabelas e inserção de dados, garantindo que os dados estejam estruturados de acordo com as necessidades do projeto de logística marítima.

## Pré-requisitos

- Python 3.x instalado
- Bibliotecas necessárias: `pandas`, `mysql-connector-python`

Instale as bibliotecas usando o seguinte comando:
```bash
pip install pandas mysql-connector-python
```

Certifique-se de ter acesso ao servidor MySQL com as credenciais apropriadas para criar bancos de dados e tabelas.

Estrutura do Projeto
O projeto está estruturado da seguinte forma:

```
projeto/
│
├── tipos_navio/
│   ├── arquivo1.xlsx
│   ├── arquivo2.xlsx
│   └── ...
│
├── rastreamento_navios/
│   ├── arquivo1.xml
│   ├── arquivo2.xml
│   └── ...
│
└── taxas/
    ├── arquivo1.csv
    ├── arquivo2.csv
    └── ...
```
* **tipos\_navio/**: Contém arquivos Excel com informações sobre tipos de navios.
* **rastreamento\_navios/**: Contém arquivos XML com dados de rastreamento de navios.
* **taxas/**: Contém arquivos CSV com informações de taxas.

**Configuração do Banco de Dados** 
* Certifique-se de que o servidor MySQL esteja em execução.
* Edite as credenciais de conexão no script `import_data_mysql.py`:
```python
cnx = mysql.connector.connect(user='usuario', password='senha', host='localhost', database='banco_de_dados', auth_plugin='mysql_native_password')
```
**Execução do Script** 
Execute o script `import_data_mysql.py` para importar os dados para o banco de dados MySQL:
```bash
python import_data_mysql.py
```
O script irá criar tabelas no banco de dados conforme necessário e inserir os dados de cada fonte de acordo com a estrutura definida.
“Detalhes Técnicos ----------------- * 
**Manipulação de Dados** 
* **Excel**: Utiliza a biblioteca `pandas` para ler dados de arquivos `.xlsx`.
   * **XML**: Utiliza `xml.etree.ElementTree` para parsear e extrair dados de arquivos `.xml`.
   * **CSV**: Manipula dados de arquivos `.csv` diretamente com `pandas`.”
**Criação de Tabelas**
* Cada fonte de dados (tipos de navio, rastreamento de navios e taxas) é mapeada para tabelas MySQL correspondentes.
  * As tabelas são criadas dinamicamente com base nos dados extraídos de cada arquivo.

