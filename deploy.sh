#!/bin/bash
# Script de atualização segura para o Sistema Contábil

echo "=========================================================="
echo "   Script de Atualização do Sistema Contábil"
echo "=========================================================="

# Diretório da aplicação
APP_DIR="/var/www/contabil"
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Criar diretório de backup se não existir
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Criando diretório de backup..."
    mkdir -p $BACKUP_DIR
fi

# 1. Backup do banco de dados
echo "1. Fazendo backup do banco de dados..."
cp $APP_DIR/db.sqlite3 $BACKUP_DIR/db.sqlite3.bak.$TIMESTAMP
echo "   Backup salvo em $BACKUP_DIR/db.sqlite3.bak.$TIMESTAMP"

# 2. Backup dos arquivos de configuração
echo "2. Fazendo backup dos arquivos de configuração..."
if [ -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env $BACKUP_DIR/.env.bak.$TIMESTAMP
    echo "   Backup do .env salvo em $BACKUP_DIR/.env.bak.$TIMESTAMP"
fi

# 3. Atualizar código do repositório
echo "3. Atualizando código do repositório..."
cd $APP_DIR
git stash  # Salva alterações locais, se houver
git pull   # Atualiza o código do repositório

# 4. Atualizar dependências
echo "4. Atualizando dependências Python..."
$APP_DIR/venv/bin/pip install -r requirements.txt

# 5. Aplicar migrações do banco de dados
echo "5. Aplicando migrações do banco de dados..."
$APP_DIR/venv/bin/python manage.py migrate

# 6. Coletar arquivos estáticos
echo "6. Coletando arquivos estáticos..."
$APP_DIR/venv/bin/python manage.py collectstatic --noinput

# 7. Corrigir permissões
echo "7. Corrigindo permissões de arquivos e diretórios..."
chown -R www-data:www-data $APP_DIR
chmod 664 $APP_DIR/db.sqlite3
chmod 775 $APP_DIR

# Permissões para diretórios
find $APP_DIR -type d -exec chmod 775 {} \;

# Permissões para arquivos
find $APP_DIR -type f -exec chmod 664 {} \;

# Permissões para arquivos de log
if [ -f "$APP_DIR/debug.log" ]; then
    chown www-data:www-data $APP_DIR/debug.log
    chmod 664 $APP_DIR/debug.log
fi

# 8. Verificar configuração do socket
echo "8. Verificando configuração do socket..."
if [ -f "/etc/nginx/sites-available/contabil" ]; then
    NGINX_SOCKET=$(grep -o "unix:[^;]*" /etc/nginx/sites-available/contabil | head -1)
    SUPERVISOR_SOCKET=$(grep -o "unix:[^ ]*" /etc/supervisor/conf.d/contabil.conf | head -1)
    
    echo "   Socket no Nginx: $NGINX_SOCKET"
    echo "   Socket no Supervisor: $SUPERVISOR_SOCKET"
    
    if [ "$NGINX_SOCKET" != "$SUPERVISOR_SOCKET" ]; then
        echo "   AVISO: Os sockets configurados no Nginx e no Supervisor são diferentes!"
        echo "   Considere alinhar as configurações."
    else
        echo "   Configuração de socket OK."
    fi
    
    # Garantir que o diretório do socket existe e tem permissões corretas
    SOCKET_DIR=$(echo $NGINX_SOCKET | sed 's|unix:||' | xargs dirname)
    if [ -n "$SOCKET_DIR" ] && [ "$SOCKET_DIR" != "." ]; then
        echo "   Garantindo permissões para o diretório do socket: $SOCKET_DIR"
        mkdir -p $SOCKET_DIR
        chown www-data:www-data $SOCKET_DIR
        chmod 775 $SOCKET_DIR
    fi
fi

# 9. Reiniciar serviços
echo "9. Reiniciando serviços..."
echo "   Reiniciando Supervisor..."
supervisorctl reread
supervisorctl update
supervisorctl restart contabil

echo "   Reiniciando Nginx..."
systemctl restart nginx

# 10. Verificar status dos serviços
echo "10. Verificando status dos serviços..."
echo "   Status do Supervisor:"
supervisorctl status contabil
echo "   Status do Nginx:"
systemctl status nginx --no-pager | head -5

echo "=========================================================="
echo "   Atualização concluída!"
echo "=========================================================="
echo "Lembre-se de verificar os logs em caso de problemas:"
echo "   - Logs do Supervisor: /var/log/contabil.log e /var/log/contabil_err.log"
echo "   - Logs do Nginx: /var/log/nginx/error.log"
echo "=========================================================="
