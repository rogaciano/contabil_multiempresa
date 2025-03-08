from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Q
from accounts.models import Account, AccountType, Company
import logging

logger = logging.getLogger(__name__)

class Report(models.Model):
    REPORT_TYPES = [
        ('BS', _('Balanço Patrimonial')),
        ('IS', _('Demonstração do Resultado')),
        ('CF', _('Fluxo de Caixa')),
        ('TB', _('Balancete')),
        ('GL', _('Razão Geral')),
    ]
    
    # Constantes para os tipos de relatório
    BALANCE_SHEET = 'BS'
    INCOME_STATEMENT = 'IS'
    CASH_FLOW = 'CF'
    TRIAL_BALANCE = 'TB'
    GENERAL_LEDGER = 'GL'
    
    company = models.ForeignKey(
        Company,
        verbose_name=_('Empresa'),
        on_delete=models.CASCADE,
        related_name='reports'
    )
    type = models.CharField(_('Tipo'), max_length=2, choices=REPORT_TYPES)
    start_date = models.DateField(_('Data Inicial'), null=True, blank=True)
    end_date = models.DateField(_('Data Final'))
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Gerado por'),
        on_delete=models.PROTECT
    )
    generated_at = models.DateTimeField(_('Gerado em'), auto_now_add=True)
    notes = models.TextField(_('Observações'), blank=True)
    
    class Meta:
        verbose_name = _('Relatório')
        verbose_name_plural = _('Relatórios')
        ordering = ['-generated_at']
        
    def __str__(self):
        if self.start_date:
            return f'{self.get_type_display()} - {self.company.name} - {self.start_date} a {self.end_date}'
        return f'{self.get_type_display()} - {self.company.name} - {self.end_date}'
    
    def get_balance_sheet_data(self):
        """Retorna os dados do Balanço Patrimonial"""
        if self.type != 'BS':
            raise ValueError(_('Este relatório não é um Balanço Patrimonial'))
        
        # Importar Account e AccountType aqui para evitar problemas de escopo
        from accounts.models import Account, AccountType
        from django.db.models import Sum, Q
        from collections import defaultdict
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Gerando balanço patrimonial para empresa {self.company.name} (ID: {self.company.id})")
        
        # Obter todas as contas ativas da empresa
        assets = Account.objects.filter(company=self.company, type=AccountType.ASSET, is_active=True).order_by('code')
        liabilities = Account.objects.filter(company=self.company, type=AccountType.LIABILITY, is_active=True).order_by('code')
        equity = Account.objects.filter(company=self.company, type=AccountType.EQUITY, is_active=True).order_by('code')
        
        # Calcular o resultado do período (receitas - despesas)
        revenues = Account.objects.filter(company=self.company, type=AccountType.REVENUE, is_active=True)
        expenses = Account.objects.filter(company=self.company, type=AccountType.EXPENSE, is_active=True)
        
        # Identificar contas de dedução da receita (geralmente começam com 4.2)
        deduction_prefix = '4.2'  # Prefixo comum para contas de dedução da receita
        
        # Separar receitas normais das deduções da receita
        regular_revenues = []
        revenue_deductions = []
        
        for account in revenues:
            if account.code.startswith(deduction_prefix):
                revenue_deductions.append(account)
            else:
                regular_revenues.append(account)
        
        # Calcular total de receitas brutas - usar apenas contas folha
        leaf_regular_revenues = [account for account in regular_revenues if account.is_leaf]
        total_revenue = sum(account.get_balance(end_date=self.end_date) for account in leaf_regular_revenues)
        
        # Calcular total de deduções - usar apenas contas folha
        leaf_revenue_deductions = [account for account in revenue_deductions if account.is_leaf]
        total_deductions = sum(abs(account.get_balance(end_date=self.end_date)) for account in leaf_revenue_deductions)
        
        # Calcular receita líquida
        net_revenue = total_revenue - total_deductions
        
        # Calcular total de despesas - usar apenas contas folha
        leaf_expenses = [account for account in expenses if account.is_leaf]
        total_expenses = sum(abs(account.get_balance(end_date=self.end_date)) for account in leaf_expenses)
        
        # Resultado do período é a receita líquida menos as despesas
        net_income = net_revenue - total_expenses
        
        if net_income < 0:
            # Se for prejuízo (resultado negativo), manter o sinal negativo
            logger.info(f"Resultado negativo (prejuízo): {net_income}")
        else:
            # Se for lucro (resultado positivo), manter o sinal positivo
            logger.info(f"Resultado positivo (lucro): {net_income}")
        
        logger.info(f"Resultado do período: Receitas Brutas ({total_revenue}) - Deduções ({total_deductions}) = Receita Líquida ({net_revenue})")
        logger.info(f"Receita Líquida ({net_revenue}) - Despesas ({total_expenses}) = Resultado ({net_income})")
        
        # Calcular saldos individuais das contas - APENAS PARA CONTAS ANALÍTICAS (FOLHAS)
        asset_balances = []
        for account in assets:
            if account.is_leaf:  # Apenas contas analíticas
                balance = account.get_balance(end_date=self.end_date)
                if balance != 0:
                    asset_balances.append((account, balance))
                    logger.info(f"Conta de ativo (analítica): {account.code} - {account.name}, Saldo: {balance}")
        
        liability_balances = []
        for account in liabilities:
            if account.is_leaf:  # Apenas contas analíticas
                balance = account.get_balance(end_date=self.end_date)
                if balance != 0:
                    liability_balances.append((account, balance))
                    logger.info(f"Conta de passivo (analítica): {account.code} - {account.name}, Saldo: {balance}")
        
        equity_balances = []
        for account in equity:
            if account.is_leaf:  # Apenas contas analíticas
                balance = account.get_balance(end_date=self.end_date)
                if balance != 0:
                    equity_balances.append((account, balance))
                    logger.info(f"Conta de patrimônio líquido (analítica): {account.code} - {account.name}, Saldo: {balance}")
        
        # Verificar se a conta de lucros/prejuízos acumulados existe (código 3.5)
        retained_earnings = Account.objects.filter(
            company=self.company,
            code='3.5',
            is_active=True
        ).first()
        
        # Flag para controlar se o resultado já foi adicionado
        result_added = False
        
        # Para a conta 3.5 (Lucros/Prejuízos Acumulados), o resultado deve manter seu sinal original
        display_net_income = net_income
        
        if retained_earnings:
            logger.info(f"Encontrada conta de lucros acumulados: {retained_earnings.code} - {retained_earnings.name}")
            
            # Verificar se a conta já está na lista de equity_balances
            for i, (account, balance) in enumerate(equity_balances):
                if account.id == retained_earnings.id:
                    # Definir o saldo como o resultado do período (DRE)
                    equity_balances[i] = (account, display_net_income)
                    result_added = True
                    logger.info(f"Definindo saldo da conta {account.code} - {account.name} como o resultado do período ({display_net_income})")
                    break
            
            # Se a conta existe mas não está na lista (improvável, mas possível)
            if not result_added:
                equity_balances.append((retained_earnings, display_net_income))
                result_added = True
                logger.info(f"Adicionando conta {retained_earnings.code} - {retained_earnings.name} com saldo igual ao resultado do período ({display_net_income})")
        else:
            # Se não existir a conta 3.5, criar uma entrada virtual
            # Primeiro verificar se existe a conta pai (3)
            equity_parent = Account.objects.filter(company=self.company, code='3', is_active=True).first()
            
            if not equity_parent:
                logger.warning("Conta pai de patrimônio líquido (3) não encontrada. Criando conta virtual.")
                # Criar uma conta pai virtual se não existir
                equity_parent = Account(
                    code='3',
                    name='Patrimônio Líquido',
                    type=AccountType.EQUITY,
                    company=self.company,
                    is_active=True
                )
                # Não salvamos a conta virtual no banco de dados
            
            # Criar conta virtual de lucros/prejuízos acumulados com código 3.5
            retained_earnings = Account(
                code='3.5', 
                name='Lucros/Prejuízos Acumulados', 
                type=AccountType.EQUITY, 
                company=self.company,
                parent=equity_parent,
                is_active=True
            )
            # Não salvamos a conta virtual no banco de dados
            
            # Adicionar à lista com o resultado do período
            equity_balances.append((retained_earnings, display_net_income))
            result_added = True
            logger.info(f"Criando conta virtual {retained_earnings.code} - {retained_earnings.name} com saldo {display_net_income}")
        
        # Calcular totais usando apenas contas analíticas (folhas)
        total_assets = sum(balance for _, balance in asset_balances)
        total_liabilities = sum(balance for _, balance in liability_balances)
        equity_total = sum(balance for _, balance in equity_balances)
        
        # Agora, calcular os saldos das contas sintéticas (com filhos)
        # Para o Ativo
        synthetic_assets = {}
        for account in assets:
            if not account.is_leaf:
                # Calcular o saldo desta conta sintética somando suas contas analíticas filhas
                synthetic_balance = 0
                for child_account, child_balance in asset_balances:
                    if child_account.code.startswith(account.code + '.') or child_account.code == account.code:
                        synthetic_balance += child_balance
                
                if synthetic_balance != 0:
                    synthetic_assets[account.code] = synthetic_balance
                    asset_balances.append((account, synthetic_balance))
                    logger.info(f"Conta de ativo (sintética): {account.code} - {account.name}, Saldo calculado: {synthetic_balance}")
        
        # Para o Passivo
        synthetic_liabilities = {}
        for account in liabilities:
            if not account.is_leaf:
                # Calcular o saldo desta conta sintética somando suas contas analíticas filhas
                synthetic_balance = 0
                for child_account, child_balance in liability_balances:
                    if child_account.code.startswith(account.code + '.') or child_account.code == account.code:
                        synthetic_balance += child_balance
                
                if synthetic_balance != 0:
                    synthetic_liabilities[account.code] = synthetic_balance
                    liability_balances.append((account, synthetic_balance))
                    logger.info(f"Conta de passivo (sintética): {account.code} - {account.name}, Saldo calculado: {synthetic_balance}")
        
        # Para o Patrimônio Líquido
        synthetic_equity = {}
        for account in equity:
            if not account.is_leaf:
                # Calcular o saldo desta conta sintética somando suas contas analíticas filhas
                synthetic_balance = 0
                for child_account, child_balance in equity_balances:
                    if child_account.code.startswith(account.code + '.') or child_account.code == account.code:
                        synthetic_balance += child_balance
                
                if synthetic_balance != 0:
                    synthetic_equity[account.code] = synthetic_balance
                    equity_balances.append((account, synthetic_balance))
                    logger.info(f"Conta de patrimônio líquido (sintética): {account.code} - {account.name}, Saldo calculado: {synthetic_balance}")
        
        # Ordenar as listas por código de conta
        asset_balances.sort(key=lambda x: x[0].code)
        liability_balances.sort(key=lambda x: x[0].code)
        equity_balances.sort(key=lambda x: x[0].code)
        
        # Calcular a diferença entre ativos e passivos + patrimônio líquido
        difference = total_assets - (total_liabilities + equity_total)
        
        # Preparar dados para o template
        data = {
            'assets': asset_balances,
            'liabilities': liability_balances,
            'equity': equity_balances,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': equity_total,
            'total_liabilities_equity': total_liabilities + equity_total,
            'difference': difference,
            'net_income': net_income,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        
        # Verificar se o balanço está equilibrado
        data['is_balanced'] = abs(data['total_assets'] - data['total_liabilities_equity']) < 0.01
        
        # Logs finais para depuração
        logger.info(f"Balanço Patrimonial - Total de ativos: {data['total_assets']}")
        logger.info(f"Balanço Patrimonial - Total de passivos: {data['total_liabilities']}")
        logger.info(f"Balanço Patrimonial - Total de patrimônio líquido: {data['total_equity']}")
        logger.info(f"Balanço Patrimonial - Total de passivos + patrimônio líquido: {data['total_liabilities_equity']}")
        logger.info(f"Balanço Patrimonial - Diferença: {data['difference']}")
        logger.info(f"Balanço Patrimonial - Está balanceado: {data['is_balanced']}")
        
        return data
    
    def get_income_statement_data(self):
        """Retorna os dados da Demonstração do Resultado"""
        if self.type != 'IS':
            raise ValueError(_('Este relatório não é uma Demonstração do Resultado'))
            
        from accounts.models import Account, AccountType
        from django.db.models import Sum, Q
        from collections import defaultdict
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Gerando DRE para empresa {self.company.name} (ID: {self.company.id})")
            
        # Obter contas de receita e despesa
        revenues = Account.objects.filter(company=self.company, type=AccountType.REVENUE, is_active=True).order_by('code')
        expenses = Account.objects.filter(company=self.company, type=AccountType.EXPENSE, is_active=True).order_by('code')
        
        # Identificar contas de dedução da receita (geralmente começam com 4.2)
        deduction_prefix = '4.2'  # Prefixo comum para contas de dedução da receita
        
        # Separar receitas normais das deduções da receita
        regular_revenues = []
        revenue_deductions = []
        
        logger.info(f"Identificando contas de dedução da receita (prefixo: {deduction_prefix})")
        
        # Separar receitas normais das deduções da receita
        for account in revenues:
            if account.code.startswith(deduction_prefix):
                revenue_deductions.append(account)
                logger.info(f"Conta identificada como dedução da receita: {account.code} - {account.name} (nível: {account.level})")
            else:
                regular_revenues.append(account)
        
        logger.info(f"Total de contas de dedução identificadas: {len(revenue_deductions)}")
        
        # Calcular saldos das receitas normais
        revenue_balances = [(account, account.get_balance(
            start_date=self.start_date,
            end_date=self.end_date
        )) for account in regular_revenues]
        
        # Calcular saldos das deduções da receita (convertendo para positivo)
        deduction_balances = []
        for account in revenue_deductions:
            balance = account.get_balance(
                start_date=self.start_date,
                end_date=self.end_date
            )
            # Converter para valor positivo para exibição na DRE
            # As deduções da receita são contas com natureza devedora (como despesas)
            adjusted_balance = abs(balance)
            logger.info(f"Dedução da receita {account.code} - {account.name}: saldo original = {balance}, ajustado para DRE = {adjusted_balance}")
            deduction_balances.append((account, adjusted_balance))
        
        # Para despesas, garantir que os valores sejam positivos na DRE
        expense_balances = []
        for account in expenses:
            balance = account.get_balance(
                start_date=self.start_date,
                end_date=self.end_date
            )
            # Converter para valor positivo para exibição na DRE
            # As despesas têm saldo devedor (positivo), mas na DRE devem ser apresentadas como positivas
            # para serem subtraídas das receitas
            adjusted_balance = abs(balance)
            logger.info(f"Conta de despesa {account.code} - {account.name}: saldo original = {balance}, ajustado para DRE = {adjusted_balance}")
            expense_balances.append((account, adjusted_balance))
        
        # Calcular totais dos grupos pai
        def calculate_group_totals(accounts_with_balances):
            # Dicionário para armazenar os totais dos grupos
            group_totals = defaultdict(lambda: 0)
            
            # Primeiro, calcular os totais das contas folha
            for account, balance in accounts_with_balances:
                if account.is_leaf:
                    # Adicionar ao total do próprio grupo
                    group_totals[account.code] = group_totals[account.code] + balance
                    
                    # Adicionar aos totais dos grupos pai
                    parent = account.parent
                    while parent:
                        # Verificar se o parent tem código (pode ser uma conta temporária)
                        if hasattr(parent, 'code') and parent.code:
                            group_totals[parent.code] = group_totals[parent.code] + balance
                        parent = parent.parent
            
            # Atualizar os saldos com os totais calculados
            result = []
            for account, original_balance in accounts_with_balances:
                if not account.is_leaf:
                    # Usar o total calculado para grupos
                    result.append((account, group_totals[account.code]))
                else:
                    # Manter o saldo original para contas folha
                    result.append((account, original_balance))
            
            return result
        
        # Aplicar o cálculo de totais para cada tipo de conta
        revenue_balances = calculate_group_totals(revenue_balances)
        deduction_balances = calculate_group_totals(deduction_balances)
        expense_balances = calculate_group_totals(expense_balances)
        
        data = {
            'revenues': revenue_balances,
            'deductions': deduction_balances,
            'expenses': expense_balances,
        }
        
        # Calcular totais
        data['total_revenue'] = sum(balance for _, balance in revenue_balances if _.level == 1)
        
        # Garantir que o total de deduções seja calculado corretamente
        # Primeiro, tentar somar as deduções de nível 1 (contas principais)
        total_deductions = sum(balance for _, balance in deduction_balances if _.level == 1)
        
        # Se não houver contas de dedução de nível 1 ou o total for zero, somar todas as deduções de nível folha
        if total_deductions == 0 and deduction_balances:
            # Somar apenas as contas folha para evitar duplicação
            total_deductions = sum(balance for account, balance in deduction_balances if account.is_leaf)
            logger.info(f"Usando total de deduções baseado em contas folha: {total_deductions}")
            
            # Se ainda for zero, somar todas as deduções
            if total_deductions == 0:
                total_deductions = sum(balance for _, balance in deduction_balances)
                logger.info(f"Usando total de todas as deduções: {total_deductions}")
        
        logger.info(f"Total final de deduções calculado: {total_deductions}")
        data['total_deductions'] = total_deductions
        
        data['total_expenses'] = sum(balance for _, balance in expense_balances if _.level == 1)
        
        # Receita líquida = Receita bruta - Deduções
        data['net_revenue'] = data['total_revenue'] - data['total_deductions']
        
        # Resultado líquido = Receita líquida - Despesas
        data['net_income'] = data['net_revenue'] - data['total_expenses']
        
        logger.info(f"DRE - Total de receitas brutas: {data['total_revenue']}")
        logger.info(f"DRE - Total de deduções da receita: {data['total_deductions']}")
        logger.info(f"DRE - Receita líquida: {data['net_revenue']}")
        logger.info(f"DRE - Total de despesas: {data['total_expenses']}")
        logger.info(f"DRE - Resultado líquido: {data['net_income']}")
        
        return data
    
    def get_trial_balance_data(self):
        """Retorna os dados do Balancete de Verificação"""
        if self.type != 'TB':
            raise ValueError(_('Este relatório não é um Balancete de Verificação'))
            
        from accounts.models import Account, AccountType
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Gerando balancete para empresa {self.company.name} (ID: {self.company.id})")
        
        # Obter apenas contas ativas e ordenar por código
        accounts = Account.objects.filter(company=self.company, is_active=True).order_by('code')
        accounts_data = []
        total_debit = 0
        total_credit = 0
        
        # Primeiro passo: processar apenas contas analíticas (folhas)
        for account in accounts:
            # Verificar se é uma conta analítica (sem filhos)
            if account.is_leaf:
                balance = account.get_balance(
                    start_date=self.start_date,
                    end_date=self.end_date
                )
                
                if balance != 0:
                    # Determinar se o saldo deve ir para débito ou crédito com base no tipo de conta
                    if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                        # Para contas de Ativo e Despesa:
                        # - Débito aumenta o saldo (positivo)
                        # - Crédito diminui o saldo (negativo)
                        debit = balance if balance > 0 else 0
                        credit = -balance if balance < 0 else 0
                    else:
                        # Para contas de Passivo, Patrimônio Líquido e Receita:
                        # - Crédito aumenta o saldo (positivo)
                        # - Débito diminui o saldo (negativo)
                        debit = -balance if balance < 0 else 0
                        credit = balance if balance > 0 else 0
                    
                    accounts_data.append((account, debit, credit))
                    total_debit += debit
                    total_credit += credit
                    logger.info(f"Conta analítica: {account.code} - {account.name}, Débito: {debit}, Crédito: {credit}")
        
        # Segundo passo: calcular os saldos das contas sintéticas (com filhos)
        synthetic_accounts = {}
        
        for account in accounts:
            if not account.is_leaf:
                # Inicializar os totais para esta conta sintética
                synthetic_accounts[account.code] = {'debit': 0, 'credit': 0}
                
                # Encontrar todas as contas analíticas que são descendentes desta conta sintética
                for child_account, child_debit, child_credit in accounts_data:
                    if child_account.code.startswith(account.code + '.') or child_account.code == account.code:
                        synthetic_accounts[account.code]['debit'] += child_debit
                        synthetic_accounts[account.code]['credit'] += child_credit
                
                # Adicionar a conta sintética ao resultado se tiver saldo
                debit = synthetic_accounts[account.code]['debit']
                credit = synthetic_accounts[account.code]['credit']
                
                if debit > 0 or credit > 0:
                    accounts_data.append((account, debit, credit))
                    logger.info(f"Conta sintética: {account.code} - {account.name}, Débito: {debit}, Crédito: {credit}")
                    # Não adicionar aos totais, pois já foram contabilizados através das contas analíticas
        
        # Ordenar o resultado final por código de conta
        accounts_data.sort(key=lambda x: x[0].code)
        
        data = {
            'accounts': accounts_data,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'is_balanced': abs(total_debit - total_credit) < 0.01,
            'difference': abs(total_debit - total_credit)
        }
        
        logger.info(f"Balancete - Total de débitos: {total_debit}")
        logger.info(f"Balancete - Total de créditos: {total_credit}")
        logger.info(f"Balancete - Diferença: {data['difference']}")
        logger.info(f"Balancete - Está balanceado: {data['is_balanced']}")
        
        return data
        
    def get_general_ledger_data(self):
        """Retorna os dados do Razão Geral para uma conta específica"""
        if self.type != 'GL':
            raise ValueError(_('Este relatório não é um Razão Geral'))
            
        from accounts.models import Account, AccountType
        from transactions.models import Transaction
        from django.db.models import Q
        from datetime import timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Obter o ID da conta a partir das notas do relatório
        # As notas do relatório devem conter o ID da conta no formato "account_id:X"
        account_id = None
        for note in self.notes.split('\n'):
            if note.startswith('account_id:'):
                account_id = note.split(':')[1].strip()
                break
                
        if not account_id:
            return {'error': 'Conta não especificada'}
            
        try:
            account = Account.objects.get(pk=account_id, company=self.company)
        except Account.DoesNotExist:
            return {'error': 'Conta não encontrada'}
            
        logger.info(f"Gerando razão para conta {account.code} - {account.name} (Tipo: {account.get_type_display()})")
            
        # Buscar as transações da conta no período
        transactions = Transaction.objects.filter(
            Q(debit_account=account) | Q(credit_account=account),
            company=self.company,
            date__gte=self.start_date,
            date__lte=self.end_date
        ).order_by('date', 'created_at')
        
        # Calcular saldo inicial (saldo até o dia anterior à data inicial)
        day_before_start = self.start_date - timedelta(days=1)
        initial_balance = account.get_balance(end_date=day_before_start)
        
        logger.info(f"Saldo inicial da conta {account.code}: {initial_balance}")
        
        # Preparar movimentos com saldo
        movements = []
        running_balance = initial_balance
        
        for transaction in transactions:
            # Determinar o efeito da transação no saldo com base no tipo de conta
            if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                # Para contas de Ativo e Despesa:
                # - Débito aumenta o saldo (positivo)
                # - Crédito diminui o saldo (negativo)
                if transaction.debit_account == account:
                    amount = transaction.amount  # Débito (positivo)
                else:
                    amount = -transaction.amount  # Crédito (negativo)
            else:
                # Para contas de Passivo, Patrimônio Líquido e Receita:
                # - Crédito aumenta o saldo (positivo)
                # - Débito diminui o saldo (negativo)
                if transaction.credit_account == account:
                    amount = transaction.amount  # Crédito (positivo)
                else:
                    amount = -transaction.amount  # Débito (negativo)
            
            running_balance += amount
            movements.append({
                'transaction': transaction,
                'amount': amount,
                'balance': running_balance
            })
            
            # Comentado para reduzir logs no terminal
            # logger.debug(f"Transação {transaction.id}: {transaction.description}, Valor: {amount}, Novo saldo: {running_balance}")
        
        data = {
            'account': account,
            'initial_balance': initial_balance,
            'movements': movements,
            'final_balance': running_balance
        }
        
        logger.info(f"Saldo final da conta {account.code}: {running_balance}")
        
        return data
    
    def get_cash_flow_data(self):
        """Retorna os dados do Fluxo de Caixa"""
        if self.type != 'CF':
            raise ValueError(_('Este relatório não é um Fluxo de Caixa'))
            
        from transactions.models import Transaction
        from django.db.models import Sum, Case, When, F, DecimalField
        
        cash_accounts = Account.objects.filter(
            company=self.company,
            type=AccountType.ASSET,
            is_active=True,
            code__startswith='1.1.1'  # Considerando que contas de caixa começam com 1.1.1
        )
        
        # Saldo inicial e final
        from datetime import timedelta
        day_before_start = self.start_date - timedelta(days=1)
        initial_balance = sum(
            account.get_balance(end_date=day_before_start)
            for account in cash_accounts
        )
        
        final_balance = sum(
            account.get_balance(end_date=self.end_date)
            for account in cash_accounts
        )
        
        # Todas as transações que afetam contas de caixa
        transactions = Transaction.objects.filter(
            models.Q(debit_account__in=cash_accounts) |
            models.Q(credit_account__in=cash_accounts),
            company=self.company,
            date__range=[self.start_date, self.end_date]
        ).order_by('date')
        
        # Categorizar transações
        operational_transactions = []
        investment_transactions = []
        financing_transactions = []
        
        for transaction in transactions:
            # Determinar se é entrada ou saída de caixa
            is_inflow = transaction.debit_account in cash_accounts
            non_cash_account = transaction.credit_account if is_inflow else transaction.debit_account
            
            # Categorizar com base no código da conta não-caixa
            account_code = non_cash_account.code
            
            # Transações operacionais: receitas (3.x.x) e despesas (4.x.x)
            if account_code.startswith('3') or account_code.startswith('4'):
                operational_transactions.append(transaction)
            # Transações de investimento: ativos não circulantes (1.2.x)
            elif account_code.startswith('1.2'):
                investment_transactions.append(transaction)
            # Transações de financiamento: passivos (2.x.x) e patrimônio líquido (3.x.x)
            elif account_code.startswith('2') or account_code.startswith('3'):
                financing_transactions.append(transaction)
            # Outras transações vão para operacional por padrão
            else:
                operational_transactions.append(transaction)
        
        # Calcular totais por categoria
        def calculate_net_flow(transactions_list):
            inflow = sum(t.amount for t in transactions_list if t.debit_account in cash_accounts)
            outflow = sum(t.amount for t in transactions_list if t.credit_account in cash_accounts)
            return inflow - outflow
        
        operational_net = calculate_net_flow(operational_transactions)
        investment_net = calculate_net_flow(investment_transactions)
        financing_net = calculate_net_flow(financing_transactions)
        
        data = {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'transactions': transactions,
            'operational_transactions': operational_transactions,
            'investment_transactions': investment_transactions,
            'financing_transactions': financing_transactions,
            'operational_net': operational_net,
            'investment_net': investment_net,
            'financing_net': financing_net,
            'total_net_flow': operational_net + investment_net + financing_net,
        }
        
        return data
