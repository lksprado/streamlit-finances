# Use uma imagem base do Python
FROM python:3.12-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo requirements.txt para o container
COPY requirements.txt ./

# Instala as dependências usando o pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/'        /etc/locale.gen \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

RUN apt-get update && apt-get install -y curl

# Copia o restante do código do projeto para o container
COPY . .
COPY .env .env

# Define variáveis de ambiente para o Streamlit
ENV STREAMLIT_SERVER_PORT=8502
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Exponha a porta para o Streamlit
EXPOSE 8502

# Comando para executar o Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0"]
