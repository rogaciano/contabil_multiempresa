import os
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Carrega os templates padrão de DRE para os diferentes regimes tributários'

    def handle(self, *args, **options):
        # Caminho para o arquivo SQL
        sql_file_path = os.path.join(
            settings.BASE_DIR, 
            'financial_reports', 
            'sql', 
            'insert_dre_templates.sql'
        )
        
        # Verificar se o arquivo existe
        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo SQL não encontrado: {sql_file_path}'))
            return
        
        # Ler o conteúdo do arquivo SQL
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_content = sql_file.read()
        
        # Executar o SQL
        try:
            with connection.cursor() as cursor:
                # Dividir o conteúdo em comandos individuais
                # Isso é necessário porque alguns bancos de dados não suportam múltiplos comandos em uma única execução
                sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
                
                for cmd in sql_commands:
                    if cmd and not cmd.startswith('--'):  # Ignorar comentários
                        cursor.execute(cmd)
            
            self.stdout.write(self.style.SUCCESS('Templates de DRE carregados com sucesso!'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao executar SQL: {str(e)}'))
