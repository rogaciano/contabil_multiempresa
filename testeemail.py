import os
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente primeiro
load_dotenv()

# Definir configurações de e-mail diretamente no ambiente
os.environ['EMAIL_HOST'] = os.environ.get('EMAIL_HOST', 'mail.talkiachat.com.br')
os.environ['EMAIL_PORT'] = os.environ.get('EMAIL_PORT', '465')
os.environ['EMAIL_USE_TLS'] = os.environ.get('EMAIL_USE_TLS', 'False')
os.environ['EMAIL_USE_SSL'] = os.environ.get('EMAIL_USE_SSL', 'True')
os.environ['EMAIL_HOST_USER'] = os.environ.get('EMAIL_HOST_USER', 'contabilidade@talkiachat.com.br')
os.environ['EMAIL_HOST_PASSWORD'] = os.environ.get('EMAIL_HOST_PASSWORD', 'Talkiachat@2025')
os.environ['DEFAULT_FROM_EMAIL'] = os.environ.get('DEFAULT_FROM_EMAIL', 'contabilidade@talkiachat.com.br')

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabil.settings')
django.setup()

from django.core.mail import send_mail

# Enviar um e-mail de teste
try:
    # Obter configurações do .env
    remetente = os.environ.get('DEFAULT_FROM_EMAIL')
    
    print(f"Usando as seguintes configurações:")
    print(f"EMAIL_HOST: {os.environ.get('EMAIL_HOST')}")
    print(f"EMAIL_PORT: {os.environ.get('EMAIL_PORT')}")
    print(f"EMAIL_USE_TLS: {os.environ.get('EMAIL_USE_TLS')}")
    print(f"EMAIL_USE_SSL: {os.environ.get('EMAIL_USE_SSL')}")
    print(f"EMAIL_HOST_USER: {os.environ.get('EMAIL_HOST_USER')}")
    print(f"DEFAULT_FROM_EMAIL: {remetente}")
    
    send_mail(
        'Teste de Configuração de E-mail',  # assunto
        'Este é um e-mail de teste para verificar se as configurações de e-mail estão funcionando corretamente.',  # mensagem
        remetente,  # remetente (usando a configuração do .env)
        ['rogaciano@gmail.com'],  # destinatário
        fail_silently=False,    
    )
    print("E-mail enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {str(e)}")