import os
import django
import logging
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabil.settings')
django.setup()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('diagnose_accounts')

# Importar modelos
from accounts.models import Account, Company, AccountType
from transactions.models import Transaction

def diagnose_accounts():
    """Função para diagnosticar problemas nas contas e seus saldos."""
    # Obter empresa ativa
    try:
        company = Company.objects.first()
        logger.info(f"Diagnosticando contas para empresa: {company.name} (ID: {company.id})")
    except Company.DoesNotExist:
        logger.error("Nenhuma empresa encontrada")
        return
    
    # Obter todas as contas da empresa
    all_accounts = Account.objects.filter(company=company).order_by('code')
    
    # Exibir estrutura de contas
    logger.info("=== ESTRUTURA DE CONTAS ===")
    for account in all_accounts:
        parent_code = account.parent.code if account.parent else "Nenhum"
        logger.info(f"Conta: {account.code} - {account.name} - Tipo: {account.type} - Pai: {parent_code} - is_leaf: {account.is_leaf}")
    
    # Analisar contas de ativo
    logger.info("\n=== CONTAS DE ATIVO ===")
    asset_accounts = Account.objects.filter(company=company, type=AccountType.ASSET, is_active=True)
    
    # Separar contas folha e não-folha
    leaf_assets = [account for account in asset_accounts if account.is_leaf]
    non_leaf_assets = [account for account in asset_accounts if not account.is_leaf]
    
    # Exibir saldos das contas folha
    logger.info("--- Contas Folha ---")
    total_leaf_assets = Decimal('0.00')
    for account in leaf_assets:
        balance = account.get_balance()
        total_leaf_assets += balance
        logger.info(f"Conta: {account.code} - {account.name} - Saldo: {balance}")
    
    logger.info(f"Total de ativos (apenas folhas): {total_leaf_assets}")
    
    # Exibir saldos das contas não-folha
    logger.info("\n--- Contas Não-Folha ---")
    for account in non_leaf_assets:
        balance = account.get_balance()
        logger.info(f"Conta: {account.code} - {account.name} - Saldo: {balance}")
    
    # Exibir transações
    logger.info("\n=== TRANSAÇÕES ===")
    transactions = Transaction.objects.filter(company=company)
    for t in transactions:
        logger.info(f"ID: {t.id}, Data: {t.date}, Descrição: {t.description}, Valor: {t.amount}")
        logger.info(f"  Débito: {t.debit_account.code} - {t.debit_account.name}")
        logger.info(f"  Crédito: {t.credit_account.code} - {t.credit_account.name}")

if __name__ == "__main__":
    diagnose_accounts()
