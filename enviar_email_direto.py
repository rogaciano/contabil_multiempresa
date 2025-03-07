import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações de e-mail fixas (sem depender do .env)
EMAIL_HOST = 'mail.talkiachat.com.br'
EMAIL_PORT = 465
EMAIL_USE_SSL = True  # Usar SSL para porta 465
EMAIL_HOST_USER = 'contabilidade@talkiachat.com.br'
EMAIL_HOST_PASSWORD = 'Talkiachat@2025'
DEFAULT_FROM_EMAIL = 'contabilidade@talkiachat.com.br'

# Destinatário
to_email = 'rogaciano@gmail.com'

# Exibir configurações
print(f"Enviando e-mail com as seguintes configurações:")
print(f"HOST: {EMAIL_HOST}")
print(f"PORT: {EMAIL_PORT}")
print(f"SSL: {EMAIL_USE_SSL}")
print(f"USER: {EMAIL_HOST_USER}")
print(f"FROM: {DEFAULT_FROM_EMAIL}")
print(f"TO: {to_email}")

# Configurar mensagem
msg = MIMEMultipart()
msg['From'] = DEFAULT_FROM_EMAIL
msg['To'] = to_email
msg['Subject'] = 'Teste de E-mail - Sistema Contábil'

body = '''
Olá,

Este é um e-mail de teste do Sistema Contábil.

Se você está recebendo este e-mail, significa que as configurações de e-mail estão funcionando corretamente.

Atenciosamente,
Sistema Contábil
'''
msg.attach(MIMEText(body, 'plain'))

try:
    # Conectar ao servidor usando SSL (para porta 465)
    print("\nConectando ao servidor com SSL...")
    server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT)
    
    # Login
    print("Fazendo login...")
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    
    # Enviar e-mail
    print("Enviando e-mail...")
    text = msg.as_string()
    server.sendmail(DEFAULT_FROM_EMAIL, to_email, text)
    
    # Encerrar conexão
    server.quit()
    
    print("\n✅ E-mail enviado com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro ao enviar e-mail: {str(e)}")
