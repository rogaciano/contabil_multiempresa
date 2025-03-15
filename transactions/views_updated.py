from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import csv
from datetime import datetime
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from django.db import transaction as db_transaction

from .models import Transaction
from accounts.models import Account
from .forms import TransactionForm
from core.models import FiscalYear

# Importar as views de templates do novo módulo
from .template_views import (
    TransactionTemplateListView, TransactionTemplateDetailView,
    TransactionTemplateCreateView, TransactionTemplateUpdateView,
    TransactionTemplateDeleteView, TransactionTemplateEditView,
    TransactionTemplateItemUpdateView, TransactionTemplateItemDeleteView,
    transaction_template_item_create, TransactionFromTemplateView,
    account_search
)


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            company=self.request.user.company
        ).select_related('debit_account', 'credit_account')
        
        # Filtros
        search_query = self.request.GET.get('search', '')
        account_id = self.request.GET.get('account', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(reference__icontains=search_query) |
                Q(debit_account__name__icontains=search_query) |
                Q(credit_account__name__icontains=search_query)
            )
        
        if account_id:
            queryset = queryset.filter(
                Q(debit_account_id=account_id) |
                Q(credit_account_id=account_id)
            )
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        return queryset.order_by('-date', '-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar contas para o filtro
        context['accounts'] = Account.objects.filter(
            company=self.request.user.company,
            is_active=True
        ).order_by('code')
        
        # Adicionar filtros atuais ao contexto
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'account': self.request.GET.get('account', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.company:
            messages.error(request, _('Selecione uma empresa para continuar.'))
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.user.company.id
        return kwargs
    
    def form_valid(self, form):
        form.instance.company = self.request.user.company
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Transação criada com sucesso!'))
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def dispatch(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.company != request.user.company:
            messages.error(request, _('Você não tem permissão para editar esta transação.'))
            return redirect('transaction_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.user.company.id
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Transação atualizada com sucesso!'))
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Transação excluída com sucesso!'))
        return super().delete(request, *args, **kwargs)


class TransactionImportView(LoginRequiredMixin, View):
    template_name = 'transactions/transaction_import.html'
    
    def post(self, request, *args, **kwargs):
        if 'csv_file' not in request.FILES:
            messages.error(request, _('Nenhum arquivo foi enviado.'))
            return render(request, self.template_name)
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, _('O arquivo deve estar no formato CSV.'))
            return render(request, self.template_name)
        
        # Processar o arquivo CSV
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            # Verificar cabeçalhos
            required_headers = ['date', 'description', 'debit_account', 'credit_account', 'value']
            if not all(header in reader.fieldnames for header in required_headers):
                messages.error(request, _('O arquivo CSV não contém todos os campos necessários.'))
                return render(request, self.template_name)
            
            # Importar transações
            success_count = 0
            error_count = 0
            
            with db_transaction.atomic():
                for row in reader:
                    try:
                        # Obter contas
                        debit_account = Account.objects.get(
                            company=request.user.company,
                            code=row['debit_account']
                        )
                        credit_account = Account.objects.get(
                            company=request.user.company,
                            code=row['credit_account']
                        )
                        
                        # Criar transação
                        Transaction.objects.create(
                            company=request.user.company,
                            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                            description=row['description'],
                            reference=row.get('reference', ''),
                            debit_account=debit_account,
                            credit_account=credit_account,
                            value=Decimal(row['value']),
                            created_by=request.user
                        )
                        
                        success_count += 1
                    except (Account.DoesNotExist, ValueError, InvalidOperation):
                        error_count += 1
            
            if success_count > 0:
                messages.success(request, _('Importação concluída: {} transações importadas com sucesso.').format(success_count))
            
            if error_count > 0:
                messages.warning(request, _('Ocorreram erros ao importar {} transações.').format(error_count))
                
        except Exception as e:
            messages.error(request, _('Erro ao processar o arquivo: {}').format(str(e)))
        
        return redirect('transaction_list')
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class TransactionExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Obter transações filtradas
        queryset = Transaction.objects.filter(
            company=request.user.company
        ).select_related('debit_account', 'credit_account')
        
        # Aplicar filtros
        search_query = request.GET.get('search', '')
        account_id = request.GET.get('account', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(reference__icontains=search_query) |
                Q(debit_account__name__icontains=search_query) |
                Q(credit_account__name__icontains=search_query)
            )
        
        if account_id:
            queryset = queryset.filter(
                Q(debit_account_id=account_id) |
                Q(credit_account_id=account_id)
            )
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        # Ordenar transações
        queryset = queryset.order_by('-date', '-id')
        
        # Criar resposta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions_{}.csv"'.format(
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        
        # Escrever cabeçalhos
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Data', 'Descrição', 'Referência', 
            'Conta de Débito (Código)', 'Conta de Débito (Nome)',
            'Conta de Crédito (Código)', 'Conta de Crédito (Nome)',
            'Valor'
        ])
        
        # Escrever dados
        for transaction in queryset:
            writer.writerow([
                transaction.id,
                transaction.date.strftime('%Y-%m-%d'),
                transaction.description,
                transaction.reference,
                transaction.debit_account.code,
                transaction.debit_account.name,
                transaction.credit_account.code,
                transaction.credit_account.name,
                transaction.value
            ])
        
        return response


class JournalView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/journal.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(
            company=self.request.user.company
        ).select_related('debit_account', 'credit_account')
        
        # Filtrar por período fiscal
        fiscal_year_id = self.request.GET.get('fiscal_year', '')
        if fiscal_year_id:
            try:
                fiscal_year = FiscalYear.objects.get(id=fiscal_year_id, company=self.request.user.company)
                queryset = queryset.filter(date__gte=fiscal_year.start_date, date__lte=fiscal_year.end_date)
            except FiscalYear.DoesNotExist:
                pass
        
        return queryset.order_by('date', 'id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar anos fiscais ao contexto
        context['fiscal_years'] = FiscalYear.objects.filter(
            company=self.request.user.company
        ).order_by('-start_date')
        
        # Adicionar filtro atual ao contexto
        context['current_fiscal_year'] = self.request.GET.get('fiscal_year', '')
        
        return context
