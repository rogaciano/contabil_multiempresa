import os
import sys
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Configurações básicas
EMAIL_USER = "contabilidade@talkiachat.com.br"
EMAIL_PASSWORD = "Talkiachat@2025"
RECIPIENT = "rogaciano@gmail.com"

# Lista de possíveis configurações para testar
configs = [
    # Configuração 1: SMTP padrão com TLS
    {
        "host": "smtp.talkiachat.com.br",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "SMTP padrão com TLS (porta 587)"
    },
    # Configuração 2: SMTP padrão com SSL
    {
        "host": "smtp.talkiachat.com.br",
        "port": 465,
        "use_tls": False,
        "use_ssl": True,
        "description": "SMTP padrão com SSL (porta 465)"
    },
    # Configuração 3: Mail com SSL
    {
        "host": "mail.talkiachat.com.br",
        "port": 465,
        "use_tls": False,
        "use_ssl": True,
        "description": "Mail com SSL (porta 465)"
    },
    # Configuração 4: Mail com TLS
    {
        "host": "mail.talkiachat.com.br",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Mail com TLS (porta 587)"
    },
    # Configuração 5: Mail com porta 25
    {
        "host": "mail.talkiachat.com.br",
        "port": 25,
        "use_tls": False,
        "use_ssl": False,
        "description": "Mail com porta 25 (sem criptografia)"
    },
    # Configuração 6: SMTP com porta 25
    {
        "host": "smtp.talkiachat.com.br",
        "port": 25,
        "use_tls": False,
        "use_ssl": False,
        "description": "SMTP com porta 25 (sem criptografia)"
    },
    # Configuração 7: POP3 (porta 995)
    {
        "host": "mail.talkiachat.com.br",
        "port": 995,
        "use_tls": False,
        "use_ssl": True,
        "description": "POP3 com SSL (porta 995) - Nota: POP3 geralmente é para receber e-mails, não enviar"
    },
    # Configuração 8: IMAP (porta 993)
    {
        "host": "mail.talkiachat.com.br",
        "port": 993,
        "use_tls": False,
        "use_ssl": True,
        "description": "IMAP com SSL (porta 993) - Nota: IMAP geralmente é para receber e-mails, não enviar"
    },
    # Configuração 9: Mail alternativo
    {
        "host": "mail.talkiachat.com.br",
        "port": 2525,
        "use_tls": True,
        "use_ssl": False,
        "description": "Mail com porta alternativa 2525 com TLS"
    },
    # Configuração 10: Subdomínio alternativo
    {
        "host": "smtp-mail.talkiachat.com.br",
        "port": 587,
        "use_tls": True,
        "use_ssl": False,
        "description": "Subdomínio alternativo com TLS"
    },
]

def test_email_config(config):
    """Testa uma configuração de e-mail específica"""
    print(f"\nTestando: {config['description']}")
    print(f"Host: {config['host']}, Porta: {config['port']}, TLS: {config['use_tls']}, SSL: {config['use_ssl']}")
    
    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT
    msg['Subject'] = f"Teste de configuração: {config['description']}"
    body = f"Este é um teste da configuração: {config['description']}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Conectar ao servidor
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['host'], config['port'], timeout=10)
        else:
            server = smtplib.SMTP(config['host'], config['port'], timeout=10)
        
        # Iniciar TLS se necessário
        if config['use_tls']:
            server.starttls()
        
        # Login
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Enviar e-mail
        server.send_message(msg)
        
        # Fechar conexão
        server.quit()
        
        print("✅ SUCESSO: E-mail enviado com sucesso!")
        return True
    
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def main():
    print("Iniciando testes de configuração de e-mail...")
    print(f"Usuário: {EMAIL_USER}")
    print(f"Destinatário: {RECIPIENT}")
    
    successful_configs = []
    
    for i, config in enumerate(configs, 1):
        print(f"\n[Teste {i}/{len(configs)}]")
        success = test_email_config(config)
        if success:
            successful_configs.append(config)
        
        # Pequena pausa entre os testes para não sobrecarregar o servidor
        if i < len(configs):
            print("Aguardando 3 segundos antes do próximo teste...")
            time.sleep(3)
    
    print("\n\n=== RESUMO DOS TESTES ===")
    if successful_configs:
        print(f"✅ {len(successful_configs)} configurações funcionaram com sucesso:")
        for i, config in enumerate(successful_configs, 1):
            print(f"{i}. {config['description']}")
            print(f"   Host: {config['host']}, Porta: {config['port']}, TLS: {config['use_tls']}, SSL: {config['use_ssl']}")
            
        # Sugerir a melhor configuração (geralmente a primeira que funcionou)
        best_config = successful_configs[0]
        print("\n=== CONFIGURAÇÃO RECOMENDADA PARA .env ===")
        print(f"EMAIL_HOST={best_config['host']}")
        print(f"EMAIL_PORT={best_config['port']}")
        print(f"EMAIL_USE_TLS={'True' if best_config['use_tls'] else 'False'}")
        print(f"EMAIL_USE_SSL={'True' if best_config['use_ssl'] else 'False'}")
        print(f"EMAIL_HOST_USER={EMAIL_USER}")
        print(f"EMAIL_HOST_PASSWORD={EMAIL_PASSWORD}")
        print(f"DEFAULT_FROM_EMAIL={EMAIL_USER}")
    else:
        print("❌ Nenhuma configuração funcionou. Sugestões:")
        print("1. Verifique se a senha está correta")
        print("2. Verifique se o servidor permite acesso SMTP")
        print("3. Verifique se há restrições de firewall")
        print("4. Entre em contato com o suporte do provedor de e-mail")

if __name__ == "__main__":
    main()
