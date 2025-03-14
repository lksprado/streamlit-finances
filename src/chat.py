import streamlit as st
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import tiktoken

load_dotenv()

# Configuração da API e do ID do Assistente # asst_bWjV0p7J0MUiSt8nbl4TuMhG
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
client = OpenAI(api_key=os.getenv("YOUR_OPENAI_API_KEY"))



# Função para contar tokens
def count_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = enc.encode(text)
    return len(tokens)

# Função para enviar a pergunta ao assistente e obter a resposta
def responder_pergunta(pergunta):
    # Cria um novo thread com a mensagem do usuário

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"hoje é dia {datetime.now()} {pergunta}",  # A pergunta do usuário é enviada diretamente
            }
        ]
    )

    # Envia o thread para o assistente (como uma nova execução)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    # Aguarda a conclusão da execução
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(1)


    # Obtém a última mensagem do thread
    message_response = client.beta.threads.messages.list(thread_id=thread.id)
    messages = message_response.data

    # Extrai e retorna a resposta mais recente
    latest_message = messages[0]
    latest_message = latest_message.content[0].text.value.strip()
    
    input = count_tokens(pergunta)
    output = count_tokens(latest_message)
    total = input+output
    print(f"Tokens input:{input}")
    print(f"Tokens output: {output}")
    print(f"Total: {total}") 
    print("----------------")         
    return latest_message

# # Interface do Streamlit
# st.title("Agente de Atendimento - Pergunte ao Assistente")

# # Caixa de entrada para perguntas
# pergunta = st.text_input("Digite sua pergunta:")

# # Quando uma pergunta é feita, envia para o assistente e exibe a resposta
# if pergunta:
#     resposta = responder_pergunta(pergunta)

if __name__ == "__main__":
    pergunta = "Considerando resultados do mês passado faça recomendações para despesas e para os ativos"
    resposta = responder_pergunta(pergunta)
    print(resposta)