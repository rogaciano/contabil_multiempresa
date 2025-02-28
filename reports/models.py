from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.models import Account, AccountType

class Report(models.Model):
    REPORT_TYPES = [
        ('BS', _('Balanço Patrimonial')),
        ('IS', _('Demonstração do Resultado')),
        ('CF', _('Fluxo de Caixa')),
        ('TB', _('Balancete')),
        ('GL', _('Razão Geral')),
    ]
    
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
            return f'{self.get_type_display()} - {self.start_date} a {self.end_date}'
        return f'{self.get_type_display()} - {self.end_date}'
    
    def get_balance_sheet_data(self):
        """Retorna os dados do Balanço Patrimonial"""
        if self.type != 'BS':
            raise ValueError(_('Este relatório não é um Balanço Patrimonial'))
        
        # Importar Account e AccountType aqui para evitar problemas de escopo
        from accounts.models import Account, AccountType
        from django.db.models import Sum, Q
        from collections import defaultdict
            
        assets = Account.objects.filter(type=AccountType.ASSET, is_active=True).order_by('code')
        liabilities = Account.objects.filter(type=AccountType.LIABILITY, is_active=True).order_by('code')
        equity = Account.objects.filter(type=AccountType.EQUITY, is_active=True).order_by('code')
        
        # Calcular o resultado do período (receitas - despesas)
        revenues = Account.objects.filter(type=AccountType.REVENUE, is_active=True)
        expenses = Account.objects.filter(type=AccountType.EXPENSE, is_active=True)
        
        total_revenue = sum(account.get_balance(end_date=self.end_date) for account in revenues)
        total_expenses = sum(account.get_balance(end_date=self.end_date) for account in expenses)
        net_income = total_revenue - total_expenses
        
        # Calcular saldos individuais
        asset_balances = [(account, account.get_balance(end_date=self.end_date)) for account in assets]
        liability_balances = [(account, account.get_balance(end_date=self.end_date)) for account in liabilities]
        equity_balances = [(account, account.get_balance(end_date=self.end_date)) for account in equity]
        
        # Adicionar o resultado do período ao patrimônio líquido
        retained_earnings = Account.objects.filter(code='3.4', is_active=True).first()
        if retained_earnings:
            # Adicionar o resultado do período à conta de lucros/prejuízos acumulados
            equity_balances = [(account, balance + (net_income if account.code == '3.4' else 0)) 
                             for account, balance in equity_balances]
        else:
            # Se não existir a conta, criar uma entrada virtual
            retained_earnings = Account(code='3.4', name='Lucros ou Prejuízos Acumulados', type=AccountType.EQUITY)
            equity_balances.append((retained_earnings, net_income))
        
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
        asset_balances = calculate_group_totals(asset_balances)
        liability_balances = calculate_group_totals(liability_balances)
        equity_balances = calculate_group_totals(equity_balances)
        
        data = {
            'assets': asset_balances,
            'liabilities': liability_balances,
            'equity': equity_balances,
        }
        
        data['total_assets'] = sum(balance for _, balance in asset_balances if _.level == 1)
        data['total_liabilities'] = sum(balance for _, balance in liability_balances if _.level == 1)
        data['total_equity'] = sum(balance for _, balance in equity_balances if _.level == 1)
        data['total_liabilities_equity'] = data['total_liabilities'] + data['total_equity']
        
        # Verificar se o balanço está equilibrado
        data['is_balanced'] = abs(data['total_assets'] - data['total_liabilities_equity']) < 0.01
        data['difference'] = abs(data['total_assets'] - data['total_liabilities_equity'])
        
        return data
    
    def get_income_statement_data(self):
        """Retorna os dados da Demonstração do Resultado"""
        if self.type != 'IS':
            raise ValueError(_('Este relatório não é uma Demonstração do Resultado'))
            
        from accounts.models import Account, AccountType
        from django.db.models import Sum, Q
        from collections import defaultdict
            
        revenues = Account.objects.filter(type=AccountType.REVENUE, is_active=True).order_by('code')
        expenses = Account.objects.filter(type=AccountType.EXPENSE, is_active=True).order_by('code')
        
        # Calcular saldos individuais
        revenue_balances = [(account, account.get_balance(
            start_date=self.start_date,
            end_date=self.end_date
        )) for account in revenues]
        
        expense_balances = [(account, account.get_balance(
            start_date=self.start_date,
            end_date=self.end_date
        )) for account in expenses]
        
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
        expense_balances = calculate_group_totals(expense_balances)
        
        data = {
            'revenues': revenue_balances,
            'expenses': expense_balances,
        }
        
        data['total_revenue'] = sum(balance for _, balance in revenue_balances if _.level == 1)
        data['total_expenses'] = sum(balance for _, balance in expense_balances if _.level == 1)
        data['net_income'] = data['total_revenue'] - data['total_expenses']
        
        return data
    
    def get_trial_balance_data(self):
        """Retorna os dados do Balancete de Verificação"""
        if self.type != 'TB':
            raise ValueError(_('Este relatório não é um Balancete de Verificação'))
            
        from accounts.models import Account, AccountType
        
        accounts = Account.objects.filter(is_active=True).order_by('code')
        accounts_data = []
        total_debit = 0
        total_credit = 0
        
        for account in accounts:
            balance = account.get_balance(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            if balance != 0:
                # Determinar se o saldo deve ir para débito ou crédito com base no tipo de conta
                if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                    # Para contas de Ativo e Despesa, saldo positivo é débito, negativo é crédito
                    debit = balance if balance > 0 else 0
                    credit = -balance if balance < 0 else 0
                else:
                    # Para contas de Passivo, Patrimônio Líquido e Receita, saldo positivo é crédito, negativo é débito
                    debit = -balance if balance < 0 else 0
                    credit = balance if balance > 0 else 0
                
                accounts_data.append((account, debit, credit))
                total_debit += debit
                total_credit += credit
        
        data = {
            'accounts': accounts_data,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'is_balanced': abs(total_debit - total_credit) < 0.01,
            'difference': abs(total_debit - total_credit)
        }
        
        return data
        
    def get_general_ledger_data(self):
        """Retorna os dados do Razão Geral para uma conta específica"""
        if self.type != 'GL':
            raise ValueError(_('Este relatório não é um Razão Geral'))
            
        from accounts.models import Account
        from transactions.models import Transaction
        from django.db.models import Q
        from datetime import timedelta
        
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
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return {'error': 'Conta não encontrada'}
            
        # Buscar as transações da conta no período
        transactions = Transaction.objects.filter(
            Q(debit_account=account) | Q(credit_account=account),
            date__gte=self.start_date,
            date__lte=self.end_date
        ).order_by('date', 'created_at')
        
        # Calcular saldo inicial (saldo até o dia anterior à data inicial)
        day_before_start = self.start_date - timedelta(days=1)
        initial_balance = account.get_balance(end_date=day_before_start)
        
        # Preparar movimentos com saldo
        movements = []
        running_balance = initial_balance
        
        for transaction in transactions:
            if transaction.debit_account == account:
                amount = transaction.amount
            else:
                amount = -transaction.amount
            
            running_balance += amount
            movements.append({
                'transaction': transaction,
                'amount': amount,
                'balance': running_balance
            })
        
        data = {
            'account': account,
            'initial_balance': initial_balance,
            'movements': movements,
            'final_balance': running_balance
        }
        
        return data
    
    def get_cash_flow_data(self):
        """Retorna os dados do Fluxo de Caixa"""
        if self.type != 'CF':
            raise ValueError(_('Este relatório não é um Fluxo de Caixa'))
            
        from transactions.models import Transaction
        from django.db.models import Sum, Case, When, F, DecimalField
        
        cash_accounts = Account.objects.filter(
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
