from get_data import GoogleFinance
from datetime import datetime, date
from decimal import Decimal
import json
import pandas as pd 
import chromadb

def get_plans():
    plans = GoogleFinance()
    if plans is None:
        raise ValueError("plans retornou None")
    return plans

plans = get_plans()

# Inicializa o cliente ChromaDB
client = chromadb.HttpClient(host='localhost', port=6333)

# Referência à coleção
collection = client.get_or_create_collection(name="financial_data")

def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo {type(obj)} não é serializável")

# Função para salvar dados em um arquivo JSON
def salvar_em_json(dados, file_path):
    with open(file_path, 'w') as file:
        json.dump(dados, file, indent=4, default=custom_serializer)

# Função para inserir dados no ChromaDB a partir de um arquivo JSON
def insert_into_chromadb(file_path, collection_name):
    with open(file_path, 'r') as file:
        data = json.load(file)  # Carrega os dados do arquivo JSON
        
    for record in data:
        collection.add(
            documents=[json.dumps(record)],
            metadatas=[{"source": collection_name}],
            ids=[record.get("MES", str(record.get("MES")))],  # Unique ID (e.g., based on "MES")
        )

def dre_json():
    file_json = 'files/dre_data.json'
    dre = plans.dre_df_transformation()
    dre = dre.drop(columns=['MES_STR'])
    dre_dict = dre.to_dict(orient='records')  # Converte para uma lista de dicionários
    salvar_em_json(dre_dict, file_json)  # Salva no arquivo JSON
    # insert_into_chromadb(file_json, "dre_data")  # Insere os dados do arquivo JSON no ChromaDB
    
def ativos_json():
    file_json = 'files/ativos_data.json'
    ativos = plans.ativos_df_transformation()
    ativos = ativos.drop(columns=['MES_STR'])
    ativos = ativos[ativos['MES'] >= pd.Timestamp('2023-09-01')]
    ativos = ativos.fillna(0)
    ativos_dict = ativos.to_dict(orient='records')  # Converte para uma lista de dicionários
    salvar_em_json(ativos_dict, file_json)  # Salva no arquivo JSON
    # insert_into_chromadb(file_json, "ativos_data")  # Insere os dados do arquivo JSON no ChromaDB

if __name__ == '__main__':
    # dre_json()
    ativos_json()
