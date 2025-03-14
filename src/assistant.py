import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import io

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da API
client = OpenAI(api_key=os.getenv("YOUR_OPENAI_API_KEY"))

# Função para criar o assistente com File Search habilitado
def create_assistant_with_file_search():
    assistant = client.beta.assistants.create(
        name="Meu ajudante de vendas",
        instructions="Você é um assistente para me ajudar com vendas.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],  # Habilitando o file_search
    )
    print(f"Assistente criado com ID: {assistant}")
    return assistant

# Criar um Vector Store para armazenar arquivos
def create_vector_store():
    vector_store = client.vector_stores.create(name="Finances")
    print(f"Vector Store criado com ID: {vector_store.id}")
    return vector_store

# Carregar os arquivos JSON no Vector Store e aguardar o processamento
def upload_files_to_vector_store(vector_store, file_paths):
    file_streams = []
    for file_path in file_paths:
        try:
            with open(file_path, "rb") as file:
                # Cria um objeto BytesIO e adiciona o atributo 'name'
                file_stream = io.BytesIO(file.read())
                file_stream.name = os.path.basename(file_path)
                file_streams.append(file_stream)
            print(f"Arquivo {file_path} preparado para upload.")
        except FileNotFoundError:
            print(f"Arquivo {file_path} não encontrado.")

    if file_streams:
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
        print(f"Status do upload: {file_batch.status}")
        print(f"Contagem de arquivos: {file_batch.file_counts}")
    else:
        print("Nenhum arquivo foi preparado para upload.")

# Atualizar o assistente para usar o Vector Store
def update_assistant_with_vector_store(assistant, vector_store):
    client.beta.assistants.update(
        assistant_id=assistant,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    print("Assistente atualizado para usar o Vector Store.")

def delete_file_from_vector_store(vector_store_id, file_id):
    try:
        # Exclui o arquivo da vector store
        openai.VectorStoreFile.delete(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
        print(f"Arquivo {file_id} removido da vector store {vector_store_id}.")

        # Exclui o arquivo do armazenamento de arquivos
        openai.File.delete(file_id)
        print(f"Arquivo {file_id} excluído do armazenamento de arquivos.")
    except Exception as e:
        print(f"Ocorreu um erro ao excluir o arquivo: {e}")
        
        
def list_vector_store_files(vector_store):
    try:
        # Lista os arquivos associados à vector store
        file_list = client.vector_stores.files.list(vector_store_id=vector_store)
        
        if not file_list:
            print("Nenhum arquivo encontrado na vector store.")
            return

        # Itera sobre cada arquivo e obtém detalhes
        for file_item in file_list:
            file_details = client.files.retrieve(file_id=file_item.id)
            print(f"ID do Arquivo: {file_details.id}")
            print(f"Nome do Arquivo: {file_details.filename}")
            print(f"Tamanho (bytes): {file_details.bytes}")
            print(f"Data de Criação: {file_details.created_at}")
            print("-" * 40)

    except Exception as e:
        print(f"Ocorreu um erro ao listar os arquivos: {e}")


if __name__ == '__main__':

    # # Criar o assistente com file_search habilitado
    # # assistant = create_assistant_with_file_search()
    # assistant = os.getenv("ASSISTANT_ID")

    # # Criar um Vector Store e fazer o upload dos arquivos JSON
    # vector_store = create_vector_store()
    # upload_files_to_vector_store(vector_store, ["files/dre_data.json", "files/ativos_data.json"])

    # # Atualizar o assistente com o Vector Store criado
    # update_assistant_with_vector_store(assistant, vector_store)
    
    vector_id = os.getenv("VECTOR_ID")
    # Chame essa função antes de fazer o upload de novos arquivos
    a = list_vector_store_files(vector_id)
    print(a)