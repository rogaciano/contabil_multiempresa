# Guia de Manutenção do Sistema Contábil

Este documento contém procedimentos para evitar problemas comuns após atualizar o código via `git pull`.

## Procedimentos Pós-Atualização

Após executar `git pull` para atualizar o código, siga estes passos para garantir que o sistema continue funcionando corretamente:

### 1. Verificar Alterações Pendentes

Antes de fazer `git pull`, verifique se há alterações locais não commitadas:

```bash
git status
```

Se houver alterações, você pode:
- Commitar as alterações: `git add . && git commit -m "Descrição das alterações"`
- Armazenar temporariamente: `git stash`
- Descartar alterações (cuidado!): `git checkout -- .`

### 2. Atualizar Dependências

Se houver alterações no arquivo `requirements.txt`:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Atualizar Arquivos Estáticos

Sempre execute o collectstatic após um pull para garantir que os arquivos estáticos estejam atualizados:

```bash
python manage.py collectstatic --noinput
```

### 4. Aplicar Migrações de Banco de Dados

Se houver alterações nos modelos:

```bash
python manage.py migrate
```

### 5. Verificar Permissões de Arquivos

Certifique-se de que os diretórios de logs e arquivos estáticos tenham as permissões corretas:

```bash
# Permissões para logs
sudo chown -R www-data:www-data /var/www/contabil/logs
sudo chmod -R 755 /var/www/contabil/logs

# Permissões para arquivos estáticos
sudo chown -R www-data:www-data /var/www/contabil/staticfiles
```

### 6. Reiniciar o Serviço

Reinicie o serviço para aplicar todas as alterações:

```bash
sudo supervisorctl restart contabil
```

### 7. Verificar Status do Serviço

Verifique se o serviço está rodando corretamente:

```bash
sudo supervisorctl status contabil
```

### 8. Verificar Logs de Erro

Se o serviço não iniciar, verifique os logs de erro:

```bash
sudo tail -n 100 /var/log/contabil_err.log
```

## Localização dos Arquivos de Log

O sistema utiliza diferentes arquivos de log para diferentes propósitos:

### Logs do Django

Os logs internos do Django são armazenados em:
```
/var/www/contabil/logs/debug.log    # Log principal do Django
/var/www/contabil/logs/error.log    # Erros do Django
```

### Logs do Gunicorn/Supervisor

Os logs do Gunicorn gerenciados pelo Supervisor estão em:
```
/var/log/contabil_out.log    # Output padrão (stdout)
/var/log/contabil_err.log    # Erros (stderr)
```

### Logs do Nginx

Os logs do servidor web Nginx estão em:
```
/var/log/nginx/access.log    # Requisições recebidas
/var/log/nginx/error.log     # Erros do Nginx
```

### Comandos Úteis para Visualização de Logs

```bash
# Ver logs do Django em tempo real
tail -f /var/www/contabil/logs/debug.log

# Ver erros do Gunicorn
tail -f /var/log/contabil_err.log

# Ver logs do Nginx
tail -f /var/log/nginx/error.log

# Buscar por erros específicos
grep "ERROR" /var/www/contabil/logs/debug.log
grep "500" /var/log/nginx/access.log
```

## Problemas Comuns e Soluções

### Erro 502 Bad Gateway

Este erro geralmente ocorre quando o aplicativo Django não consegue iniciar. Causas comuns:

1. **Problema com permissões de logs**:
   ```bash
   sudo mkdir -p /var/log/contabil
   sudo chown -R www-data:www-data /var/log/contabil
   sudo chmod -R 755 /var/log/contabil
   ```

2. **Dependências faltantes ou desatualizadas**:
   Verifique se todas as dependências necessárias estão instaladas:
   ```bash
   pip install -r requirements.txt
   
   # Dependências específicas que podem não estar no requirements.txt
   pip install whitenoise==6.6.0
   pip install xhtml2pdf
   ```

3. **Configuração incorreta de logs**:
   Verifique se a configuração em `settings.py` está correta:
   ```python
   'file': {
       'level': 'DEBUG',
       'class': 'logging.handlers.RotatingFileHandler',
       'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),
       'maxBytes': 10485760,
       'backupCount': 5,
       'formatter': 'verbose',
   },
   ```

4. **Verificar se o Gunicorn está rodando**:
   ```bash
   ps aux | grep gunicorn
   netstat -tulpn | grep 8000
   ```

5. **Executar Gunicorn manualmente para depuração**:
   ```bash
   cd /var/www/contabil
   /var/www/contabil/venv/bin/gunicorn --bind 127.0.0.1:8000 contabil.wsgi:application --log-level debug
   ```

### Admin com Aparência Incorreta

Se o admin do Django aparecer sem estilos:

```bash
python manage.py collectstatic --noinput
```

### Erro 504 Gateway Time-out nas Contas com IA

Este erro ocorre quando a requisição à API do Gemini ultrapassa o tempo limite configurado no Nginx. Causas e soluções:

1. **Timeout na API do Gemini**:
   - Verifique o timeout configurado no arquivo `accounts/services.py` na classe `GeminiService`:
   ```python
   # Garantir que há um timeout explícito na requisição
   response = requests.post(url, headers=headers, json=data, timeout=60)
   ```
   
2. **Ajustar timeout no Nginx**:
   - Aumente o timeout no arquivo de configuração do Nginx:
   ```bash
   # Edite o arquivo de configuração do Nginx
   sudo nano /etc/nginx/sites-available/contabil.conf
   
   # Adicione ou ajuste as seguintes linhas
   proxy_connect_timeout 300;
   proxy_send_timeout 300;
   proxy_read_timeout 300;
   ```

3. **Ajustar timeout no Gunicorn**:
   - Verifique se o timeout do Gunicorn está configurado adequadamente:
   ```bash
   # No arquivo de configuração do supervisor
   command=/var/www/contabil/venv/bin/gunicorn --workers 3 --timeout 300 --bind 127.0.0.1:8000 contabil.wsgi:application
   ```

4. **Implementar logging detalhado**:
   - Adicione logs detalhados para diagnosticar problemas na API:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   # Antes da chamada à API
   logger.info(f"Iniciando chamada à API do Gemini para company_id={company_id}")
   
   try:
       # Chamada à API com timeout
       response = requests.post(url, headers=headers, json=data, timeout=60)
       # Processamento da resposta
   except requests.exceptions.Timeout:
       logger.error(f"Timeout na chamada à API do Gemini para company_id={company_id}")
       # Tratamento do erro
   except Exception as e:
       logger.error(f"Erro na chamada à API do Gemini: {str(e)}")
       # Tratamento do erro
   ```

5. **Reiniciar serviços**:
   ```bash
   sudo supervisorctl restart contabil
   sudo systemctl restart nginx
   ```

### Erro 500 no Cadastro de Email

Este erro pode ocorrer durante o processo de registro de usuários quando o sistema tenta enviar o email de ativação. Causas comuns e soluções:

1. **Problemas com configuração de email**:
   - Verifique se as configurações de email no `settings.py` estão corretas:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.example.com')
   EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
   EMAIL_USE_TLS = False
   EMAIL_USE_SSL = True
   EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'user@example.com')
   EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'password')
   DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'user@example.com')
   ```

2. **Problemas com o servidor SMTP**:
   - Verifique se o servidor SMTP está acessível a partir do servidor:
   ```bash
   # Teste a conexão com o servidor SMTP
   telnet mail.example.com 465
   ```

3. **Tratamento de erros no envio de email**:
   - Certifique-se de que a view `UserRegistrationView` em `core/views.py` tem tratamento adequado de erros:
   ```python
   try:
       # Código para enviar email
       send_mail(...)
   except Exception as e:
       # Registrar o erro, mas não impedir o registro
       logger.error(f"Erro ao enviar email de ativação: {str(e)}")
       # Ativar o usuário mesmo sem o email
       user.is_active = True
       user.save()
   ```

4. **Permissões de arquivo para templates de email**:
   - Verifique se os templates de email têm as permissões corretas:
   ```bash
   sudo chown -R www-data:www-data /var/www/contabil/templates/core/email
   sudo chmod -R 644 /var/www/contabil/templates/core/email/*.html
   ```

5. **Verificar logs para erros específicos**:
   ```bash
   grep "email" /var/log/contabil_err.log
   grep "send_mail" /var/www/contabil/logs/debug.log
   ```

### Erro ao Fazer Pull

Se o git não permitir pull devido a alterações locais:

```bash
# Opção 1: Commit das alterações
git add .
git commit -m "Alterações locais"

# Opção 2: Stash das alterações
git stash

# Depois do pull, aplique o stash novamente
git stash pop
```

## Script de Manutenção Automática

Para automatizar o processo, você pode criar um script de manutenção:

```bash
#!/bin/bash
# Script de manutenção para o sistema contábil

echo "Iniciando manutenção do sistema contábil em $(date)"

# Diretório do projeto
cd /var/www/contabil

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar código
git stash
git pull origin main
git stash pop

# Atualizar dependências
pip install -r requirements.txt

# Garantir que dependências críticas estejam instaladas
pip install whitenoise==6.6.0
pip install xhtml2pdf

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar permissões
# Logs do Django
mkdir -p /var/www/contabil/logs
chown -R www-data:www-data /var/www/contabil/logs
chmod -R 755 /var/www/contabil/logs

# Logs do sistema
mkdir -p /var/log/contabil
chown -R www-data:www-data /var/log/contabil
chmod -R 755 /var/log/contabil

# Arquivos estáticos
chown -R www-data:www-data /var/www/contabil/staticfiles

# Reiniciar serviço
supervisorctl restart contabil

# Verificar status do serviço
echo "Status do serviço:"
supervisorctl status contabil

echo "Manutenção concluída em $(date)"
```

Salve este script em `/var/www/contabil/scripts/update.sh` e torne-o executável:
```bash
chmod +x /var/www/contabil/scripts/update.sh
```

Após isso, você pode executar a atualização com um único comando:
```bash
sudo /var/www/contabil/scripts/update.sh
```


Apos o 
git reset --hard origin/main
git pull

sudo touch /var/www/contabil/debug.log
sudo chown www-data:www-data /var/www/contabil/debug.log
sudo chmod 644 /var/www/contabil/debug.log

sudo supervisorctl restart contabil

sudo supervisorctl status contabil