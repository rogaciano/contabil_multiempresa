from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages

from .models import CompanyInfo, FiscalYear
from accounts.models import Account, AccountType
from transactions.models import Transaction

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter o mês atual
        today = timezone.now()
        first_day = today.replace(day=1)
        
        # Calcular receitas e despesas do mês
        revenues = Account.objects.filter(type=AccountType.REVENUE)
        expenses = Account.objects.filter(type=AccountType.EXPENSE)
        
        monthly_revenue = sum(account.get_balance(start_date=first_day) for account in revenues)
        monthly_expense = sum(account.get_balance(start_date=first_day) for account in expenses)
        
        # Obter últimas transações
        recent_transactions = Transaction.objects.all().order_by('-date', '-created_at')[:5]
        
        # Calcular totais de ativos, passivos e patrimônio líquido
        assets = Account.objects.filter(type=AccountType.ASSET, is_active=True)
        liabilities = Account.objects.filter(type=AccountType.LIABILITY, is_active=True)
        equity = Account.objects.filter(type=AccountType.EQUITY, is_active=True)
        
        total_assets = sum(account.get_balance() for account in assets)
        total_liabilities = sum(account.get_balance() for account in liabilities)
        total_equity = sum(account.get_balance() for account in equity)
        
        # Calcular o resultado acumulado (receitas - despesas)
        total_revenue = sum(account.get_balance() for account in revenues)
        total_expense = sum(account.get_balance() for account in expenses)
        net_income_accumulated = total_revenue - total_expense
        
        # Adicionar o resultado acumulado ao patrimônio líquido
        total_equity_with_income = total_equity + net_income_accumulated
        
        # Verificar se o balanço está equilibrado
        total_liabilities_equity = total_liabilities + total_equity_with_income
        is_balanced = abs(total_assets - total_liabilities_equity) < 0.01  # Tolerância para erros de arredondamento
        difference = abs(total_assets - total_liabilities_equity)
        
        # Contar o número total de contas e transações do mês
        total_accounts = Account.objects.filter(is_active=True).count()
        transactions_this_month = Transaction.objects.filter(date__gte=first_day).count()
        
        context.update({
            'monthly_revenue': monthly_revenue,
            'monthly_expense': monthly_expense,
            'net_income': monthly_revenue - monthly_expense,
            'recent_transactions': recent_transactions,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'net_income_accumulated': net_income_accumulated,
            'total_equity_with_income': total_equity_with_income,
            'total_liabilities_equity': total_liabilities_equity,
            'is_balanced': is_balanced,
            'difference': difference,
            'total_accounts': total_accounts,
            'transactions_this_month': transactions_this_month,
        })
        
        return context

class CompanyInfoView(LoginRequiredMixin, DetailView):
    model = CompanyInfo
    template_name = 'core/company_info.html'
    
    def get_object(self, queryset=None):
        return CompanyInfo.objects.first()

class CompanyInfoUpdateView(LoginRequiredMixin, UpdateView):
    model = CompanyInfo
    template_name = 'core/company_info_form.html'
    fields = ['name', 'cnpj', 'address', 'phone', 'email', 'website', 'logo']
    success_url = reverse_lazy('company_info')
    
    def get_object(self, queryset=None):
        return CompanyInfo.objects.first()
    
    def form_valid(self, form):
        messages.success(self.request, 'Informações da empresa atualizadas com sucesso!')
        return super().form_valid(form)

class FiscalYearListView(LoginRequiredMixin, ListView):
    model = FiscalYear
    template_name = 'core/fiscal_year_list.html'
    context_object_name = 'fiscal_years'

class FiscalYearDetailView(LoginRequiredMixin, DetailView):
    model = FiscalYear
    template_name = 'core/fiscal_year_detail.html'

class FiscalYearCreateView(LoginRequiredMixin, CreateView):
    model = FiscalYear
    template_name = 'core/fiscal_year_form.html'
    fields = ['year', 'start_date', 'end_date', 'notes']
    success_url = reverse_lazy('fiscal_year_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ano fiscal criado com sucesso!')
        return super().form_valid(form)

class FiscalYearUpdateView(LoginRequiredMixin, UpdateView):
    model = FiscalYear
    template_name = 'core/fiscal_year_form.html'
    fields = ['year', 'start_date', 'end_date', 'notes']
    success_url = reverse_lazy('fiscal_year_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ano fiscal atualizado com sucesso!')
        return super().form_valid(form)

class FiscalYearCloseView(LoginRequiredMixin, UpdateView):
    model = FiscalYear
    template_name = 'core/fiscal_year_close.html'
    fields = ['notes']
    success_url = reverse_lazy('fiscal_year_list')
    
    def form_valid(self, form):
        fiscal_year = form.instance
        fiscal_year.is_closed = True
        fiscal_year.closed_by = self.request.user
        fiscal_year.closed_at = timezone.now()
        messages.success(self.request, 'Ano fiscal fechado com sucesso!')
        return super().form_valid(form)
