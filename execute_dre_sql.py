import os
import django
from django.db import connection

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabil.settings')
django.setup()

# Caminho para o arquivo SQL
sql_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'financial_reports',
    'sql',
    'insert_dre_templates_sqlite.sql'  # Usando a versão SQLite do script
)

# Verificar se o arquivo existe
if not os.path.exists(sql_file_path):
    print(f'Arquivo SQL não encontrado: {sql_file_path}')
    exit(1)

# Ler o conteúdo do arquivo SQL
with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
    sql_content = sql_file.read()

# Executar o SQL
try:
    # Dividir o conteúdo em comandos individuais
    sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    
    print(f"Encontrados {len(sql_commands)} comandos SQL para executar.")
    
    # Primeiro, vamos limpar as tabelas existentes para evitar conflitos
    with connection.cursor() as cursor:
        try:
            print("Limpando tabelas existentes...")
            cursor.execute("DELETE FROM financial_reports_dresection")
            cursor.execute("DELETE FROM financial_reports_dretemplate")
            connection.commit()
            print("Tabelas limpas com sucesso!")
        except Exception as e:
            print(f"Erro ao limpar tabelas: {str(e)}")
    
    # Agora vamos executar cada comando individualmente
    for i, cmd in enumerate(sql_commands):
        if cmd and not cmd.startswith('--'):  # Ignorar comentários
            try:
                print(f"\nExecutando comando {i+1}/{len(sql_commands)}...")
                print(f"Comando: {cmd[:150]}...")  # Mostrar os primeiros 150 caracteres
                
                with connection.cursor() as cursor:
                    cursor.execute(cmd)
                    connection.commit()  # Commit após cada comando
                
                print(f"Comando {i+1} executado e commitado com sucesso!")
                
                # Verificar o estado atual do banco após cada comando
                if i % 5 == 0 or i == len(sql_commands) - 1:  # A cada 5 comandos ou no último
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM financial_reports_dretemplate")
                        template_count = cursor.fetchone()[0]
                        print(f"Número atual de templates DRE: {template_count}")
                        
                        cursor.execute("SELECT COUNT(*) FROM financial_reports_dresection")
                        section_count = cursor.fetchone()[0]
                        print(f"Número atual de seções DRE: {section_count}")
            except Exception as cmd_error:
                print(f"Erro ao executar comando {i+1}: {str(cmd_error)}")
                print(f"Comando com erro: {cmd}")
    
    # Verificação final
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM financial_reports_dretemplate")
        template_count = cursor.fetchone()[0]
        print(f"\nNúmero final de templates DRE no banco de dados: {template_count}")
        
        if template_count > 0:
            cursor.execute("SELECT id, name, tax_regime FROM financial_reports_dretemplate")
            templates = cursor.fetchall()
            print("Templates encontrados:")
            for template in templates:
                print(f"  - ID: {template[0]}, Nome: {template[1]}, Regime: {template[2]}")
        
        cursor.execute("SELECT COUNT(*) FROM financial_reports_dresection")
        section_count = cursor.fetchone()[0]
        print(f"Número final de seções DRE no banco de dados: {section_count}")
        
        if section_count > 0:
            cursor.execute("SELECT id, template_id, name FROM financial_reports_dresection LIMIT 5")
            sections = cursor.fetchall()
            print("Primeiras 5 seções encontradas:")
            for section in sections:
                print(f"  - ID: {section[0]}, Template ID: {section[1]}, Nome: {section[2]}")
    
    print('\nSQL executado com sucesso!')

except Exception as e:
    print(f'Erro ao executar SQL: {str(e)}')
