import os
import re
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações corretas para o servidor de e-mail
correct_settings = {
    'EMAIL_HOST': 'mail.talkiachat.com.br',
    'EMAIL_PORT': '465',
    'EMAIL_USE_TLS': 'False',
    'EMAIL_USE_SSL': 'True',
    'EMAIL_HOST_USER': 'contabilidade@talkiachat.com.br',
    'EMAIL_HOST_PASSWORD': 'Talkiachat@2025',
    'DEFAULT_FROM_EMAIL': 'contabilidade@talkiachat.com.br'
}

# Verificar as configurações atuais no ambiente
print("Configurações atuais no ambiente:")
for key in correct_settings:
    value = os.environ.get(key)
    print(f"{key}: {value}")

# Verificar as configurações no arquivo settings.py
settings_path = os.path.join('contabil', 'settings.py')

if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings_content = f.read()
    
    print("\nConfigurações no arquivo settings.py:")
    
    for key in correct_settings:
        pattern = rf"{key}\s*=\s*.*"
        matches = re.findall(pattern, settings_content)
        if matches:
            for match in matches:
                print(match.strip())
        else:
            print(f"{key}: Não encontrado")
    
    # Verificar se há conflito entre TLS e SSL
    if "EMAIL_USE_TLS = True" in settings_content and "EMAIL_USE_SSL = True" in settings_content:
        print("\n⚠️ ALERTA: Tanto EMAIL_USE_TLS quanto EMAIL_USE_SSL estão definidos como True no settings.py!")
        print("Isso causa um erro, pois eles são mutuamente exclusivos.")
else:
    print(f"\nArquivo {settings_path} não encontrado!")

# Verificar o arquivo .env
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    print("\nConfigurações no arquivo .env:")
    
    for key in correct_settings:
        pattern = rf"{key}\s*=\s*.*"
        matches = re.findall(pattern, env_content)
        if matches:
            for match in matches:
                print(match.strip())
        else:
            print(f"{key}: Não encontrado")
    
    # Verificar se há conflito entre TLS e SSL
    if "EMAIL_USE_TLS=True" in env_content and "EMAIL_USE_SSL=True" in env_content:
        print("\n⚠️ ALERTA: Tanto EMAIL_USE_TLS quanto EMAIL_USE_SSL estão definidos como True no .env!")
        print("Isso causa um erro, pois eles são mutuamente exclusivos.")
else:
    print(f"\nArquivo {env_path} não encontrado!")

print("\nConfigurações recomendadas:")
for key, value in correct_settings.items():
    print(f"{key}={value}")
