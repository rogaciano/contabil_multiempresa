import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de e-mail
email_host = os.environ.get('EMAIL_HOST', 'mail.talkiachat.com.br')
email_port = int(os.environ.get('EMAIL_PORT', '465'))
email_use_tls = os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true'
email_use_ssl = os.environ.get('EMAIL_USE_SSL', 'True').lower() == 'true'
email_user = os.environ.get('EMAIL_HOST_USER', 'contabilidade@talkiachat.com.br')
email_password = os.environ.get('EMAIL_HOST_PASSWORD', 'Talkiachat@2025')
default_from = os.environ.get('DEFAULT_FROM_EMAIL', 'contabilidade@talkiachat.com.br')

# Exibir configurações
print(f"Configurações de e-mail:")
print(f"HOST: {email_host}")
print(f"PORT: {email_port}")
print(f"TLS: {email_use_tls}")
print(f"SSL: {email_use_ssl}")
print(f"USER: {email_user}")
print(f"FROM: {default_from}")

# Configurar mensagem
msg = MIMEMultipart()
msg['From'] = default_from
msg['To'] = 'rogaciano@gmail.com'
msg['Subject'] = 'Teste de E-mail Direto'

body = 'Este é um teste de envio de e-mail direto usando smtplib.'
msg.attach(MIMEText(body, 'plain'))

try:
    # Conectar ao servidor
    print("\nConectando ao servidor...")
    
    if email_use_ssl:
        print("Usando conexão SSL")
        server = smtplib.SMTP_SSL(email_host, email_port)
    else:
        print("Usando conexão padrão")
        server = smtplib.SMTP(email_host, email_port)
        
        if email_use_tls:
            print("Iniciando TLS")
            server.starttls()
    
    # Login
    print("Fazendo login...")
    server.login(email_user, email_password)
    
    # Enviar e-mail
    print("Enviando e-mail...")
    text = msg.as_string()
    server.sendmail(default_from, 'rogaciano@gmail.com', text)
    
    # Encerrar conexão
    server.quit()
    
    print("\n✅ E-mail enviado com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro ao enviar e-mail: {str(e)}")
