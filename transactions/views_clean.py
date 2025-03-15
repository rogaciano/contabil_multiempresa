"""
Views relacionadas às transações básicas do sistema contábil.
Este módulo contém apenas as funcionalidades estáveis de transações,
sem as funcionalidades de templates que foram movidas para transaction_templates.py.
"""
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction as db_transaction

from .models import Transaction
from accounts.models import Account
from .forms import TransactionForm
from core.models import FiscalYear


class TransactionListView(LoginRequiredMixin, ListView):
    """
    View para listar transações com filtros
    """
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar transações pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtros
        account_id = self.request.GET.get('account')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search = self.request.GET.get('search')
        
        if account_id:
            queryset = queryset.filter(
                Q(debit_account_id=account_id) | Q(credit_account_id=account_id)
            )
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(document_number__icontains=search) |
                Q(notes__icontains=search)
            )
            
        return queryset.order_by('-date', '-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar filtros atuais ao contexto
        context['current_filters'] = {
            'account': self.request.GET.get('account'),
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date'),
            'search': self.request.GET.get('search'),
        }
        
        # Filtrar contas pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            context['accounts'] = Account.objects.filter(company_id=company_id, is_active=True)
        else:
            context['accounts'] = Account.objects.filter(is_active=True)
            
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """
    View para exibir detalhes de uma transação
    """
    model = Transaction
    template_name = 'transactions/transaction_detail.html'


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar uma nova transação
    """
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem uma empresa selecionada
        """
        company_id = request.session.get('current_company_id')
        if not company_id:
            messages.error(request, _('Selecione uma empresa para continuar.'))
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Passa o company_id para o formulário
        """
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('current_company_id')
        return kwargs
    
    def form_valid(self, form):
        """
        Define a empresa da transação como a empresa atual do usuário
        """
        form.instance.company_id = self.request.session.get('current_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Transação criada com sucesso!'))
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para atualizar uma transação existente
    """
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para editar a transação
        """
        transaction = self.get_object()
        company_id = request.session.get('current_company_id')
        if transaction.company_id != company_id:
            messages.error(request, _('Você não tem permissão para editar esta transação.'))
            return redirect('transaction_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Passa o company_id para o formulário
        """
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('current_company_id')
        return kwargs
    
    def form_valid(self, form):
        """
        Salva a transação e exibe mensagem de sucesso
        """
        messages.success(self.request, _('Transação atualizada com sucesso!'))
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir uma transação
    """
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
    
    def delete(self, request, *args, **kwargs):
        """
        Exclui a transação e exibe mensagem de sucesso
        """
        messages.success(request, _('Transação excluída com sucesso!'))
        return super().delete(request, *args, **kwargs)


class TransactionImportView(LoginRequiredMixin, View):
    """
    View para importar transações a partir de um arquivo CSV
    """
    template_name = 'transactions/transaction_import.html'
    
    def post(self, request, *args, **kwargs):
        """
        Processa o arquivo CSV e importa as transações
        """
        if 'csv_file' not in request.FILES:
            messages.error(request, _('Nenhum arquivo foi enviado.'))
            return render(request, self.template_name)
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, _('O arquivo deve estar no formato CSV.'))
            return render(request, self.template_name)
        
        company_id = request.session.get('current_company_id')
        if not company_id:
            messages.error(request, _('Selecione uma empresa para continuar.'))
            return redirect('dashboard')
        
        # Processar o arquivo CSV
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            # Verificar cabeçalhos
            required_headers = ['date', 'description', 'debit_account', 'credit_account', 'amount']
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
                            company_id=company_id,
                            code=row['debit_account']
                        )
                        credit_account = Account.objects.get(
                            company_id=company_id,
                            code=row['credit_account']
                        )
                        
                        # Criar transação
                        Transaction.objects.create(
                            company_id=company_id,
                            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                            description=row['description'],
                            document_number=row.get('document_number', ''),
                            notes=row.get('notes', ''),
                            debit_account=debit_account,
                            credit_account=credit_account,
                            amount=Decimal(row['amount']),
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
        """
        Exibe o formulário para importar transações
        """
        return render(request, self.template_name)


class TransactionExportView(LoginRequiredMixin, View):
    """
    View para exportar transações para um arquivo CSV
    """
    def get(self, request, *args, **kwargs):
        """
        Exporta as transações filtradas para um arquivo CSV
        """
        # Obter transações filtradas
        queryset = Transaction.objects.all()
        
        # Filtrar pela empresa atual
        company_id = request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Aplicar filtros
        account_id = request.GET.get('account')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search')
        
        if account_id:
            queryset = queryset.filter(
                Q(debit_account_id=account_id) | Q(credit_account_id=account_id)
            )
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(document_number__icontains=search) |
                Q(notes__icontains=search)
            )
        
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
            'ID', 'Data', 'Descrição', 'Documento', 
            'Conta de Débito (Código)', 'Conta de Débito (Nome)',
            'Conta de Crédito (Código)', 'Conta de Crédito (Nome)',
            'Valor', 'Observações'
        ])
        
        # Escrever dados
        for transaction in queryset:
            writer.writerow([
                transaction.id,
                transaction.date.strftime('%Y-%m-%d'),
                transaction.description,
                transaction.document_number,
                transaction.debit_account.code,
                transaction.debit_account.name,
                transaction.credit_account.code,
                transaction.credit_account.name,
                transaction.amount,
                transaction.notes
            ])
        
        return response


class JournalView(LoginRequiredMixin, ListView):
    """
    View para exibir o livro diário
    """
    model = Transaction
    template_name = 'transactions/journal.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        """
        Filtra as transações pelo período fiscal selecionado
        """
        queryset = super().get_queryset()
        
        # Filtrar pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtrar por período fiscal
        fiscal_year_id = self.request.GET.get('fiscal_year')
        if fiscal_year_id:
            try:
                fiscal_year = FiscalYear.objects.get(id=fiscal_year_id, company_id=company_id)
                queryset = queryset.filter(date__gte=fiscal_year.start_date, date__lte=fiscal_year.end_date)
            except FiscalYear.DoesNotExist:
                pass
        
        return queryset.order_by('date', 'id')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona os anos fiscais ao contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Filtrar anos fiscais pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            context['fiscal_years'] = FiscalYear.objects.filter(company_id=company_id)
        else:
            context['fiscal_years'] = FiscalYear.objects.none()
        
        # Adicionar filtro atual ao contexto
        context['current_fiscal_year'] = self.request.GET.get('fiscal_year')
        
        return context
