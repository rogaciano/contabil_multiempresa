import os
import django

# Configurar as variáveis de ambiente ANTES de carregar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabil.settings')

# Configurações de e-mail fixas
os.environ['EMAIL_HOST'] = 'mail.talkiachat.com.br'
os.environ['EMAIL_PORT'] = '465'
os.environ['EMAIL_USE_TLS'] = 'False'
os.environ['EMAIL_USE_SSL'] = 'True'
os.environ['EMAIL_HOST_USER'] = 'contabilidade@talkiachat.com.br'
os.environ['EMAIL_HOST_PASSWORD'] = 'Talkiachat@2025'
os.environ['DEFAULT_FROM_EMAIL'] = 'contabilidade@talkiachat.com.br'

# Inicializar o Django
django.setup()

# Importar o módulo de e-mail do Django
from django.core.mail import send_mail
from django.conf import settings

# Exibir as configurações atuais
print("Configurações de e-mail do Django:")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Enviar e-mail
try:
    print("\nEnviando e-mail de teste...")
    
    resultado = send_mail(
        'Teste de E-mail Django - Sistema Contábil',
        'Este é um e-mail de teste enviado pelo Django. Se você está recebendo este e-mail, significa que as configurações de e-mail do Django estão funcionando corretamente.',
        settings.DEFAULT_FROM_EMAIL,
        ['rogaciano@gmail.com'],
        fail_silently=False,
    )
    
    if resultado:
        print(f"\n✅ E-mail enviado com sucesso! ({resultado} mensagens enviadas)")
    else:
        print("\n❌ Falha ao enviar e-mail (nenhuma mensagem enviada)")
        
except Exception as e:
    print(f"\n❌ Erro ao enviar e-mail: {str(e)}")
