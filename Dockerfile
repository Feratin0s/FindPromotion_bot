FROM python

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos locais para o container
# Substitua "./" pelo caminho correto para seu código, se necessário.
COPY . /app

# Dá permissão ao arquivo principal
RUN chmod +x ./main.py

# Instala as dependências necessárias
RUN pip install -r requirements.txt

# Define o usuário padrão (opcional)
USER root

# Define o comando a ser executado ao iniciar o container
CMD ["python", "main.py"]

