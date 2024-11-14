FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /src

# Instala o Poetry
RUN pip install --no-cache-dir poetry

# Copie apenas os arquivos necessários para instalar as dependências
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Copie o código do aplicativo
COPY . .

# Exponha a porta que o Streamlit usará
EXPOSE 8502

# Comando para executar o Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0"]
