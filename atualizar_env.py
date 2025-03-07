import os
from dotenv import load_dotenv, find_dotenv, set_key

# Encontrar o arquivo .env
dotenv_path = find_dotenv()

if not dotenv_path:
    print("Arquivo .env não encontrado!")
    exit(1)

# Carregar variáveis atuais
load_dotenv(dotenv_path)

# Definir novas configurações
new_settings = {
    'EMAIL_HOST': 'mail.talkiachat.com.br',
    'EMAIL_PORT': '465',
    'EMAIL_USE_TLS': 'False',
    'EMAIL_USE_SSL': 'True',
    'EMAIL_HOST_USER': 'contabilidade@talkiachat.com.br',
    'EMAIL_HOST_PASSWORD': 'Talkiachat@2025',
    'DEFAULT_FROM_EMAIL': 'contabilidade@talkiachat.com.br'
}

# Atualizar o arquivo .env
for key, value in new_settings.items():
    set_key(dotenv_path, key, value)

print("Arquivo .env atualizado com sucesso!")
print("Novas configurações:")
for key, value in new_settings.items():
    print(f"{key}={value}")
