from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import csv
from datetime import datetime

from .models import Transaction
from accounts.models import Account
from .forms import TransactionForm

class TransactionListView(LoginRequiredMixin, ListView):
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
                Q(document_number__icontains=search)
            )
        
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtrar contas pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            context['accounts'] = Account.objects.filter(company_id=company_id, is_active=True)
        else:
            context['accounts'] = Account.objects.filter(is_active=True)
            
        return context

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passar o ID da empresa atual para o formulário
        kwargs['company_id'] = self.request.session.get('current_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Definir o usuário que criou a transação
        form.instance.created_by = self.request.user
        
        # Definir a empresa da transação
        company_id = self.request.session.get('current_company_id')
        if company_id:
            form.instance.company_id = company_id
        else:
            messages.error(self.request, 'Selecione uma empresa antes de criar uma transação.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Transação criada com sucesso!')
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passar o ID da empresa da transação para o formulário
        transaction = self.get_object()
        kwargs['company_id'] = transaction.company_id
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Transação atualizada com sucesso!')
        return super().form_valid(form)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transação excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class TransactionImportView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/transaction_import.html'
    
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Por favor, selecione um arquivo CSV para importar.')
            return super().get(request, *args, **kwargs)
        
        # Obter a empresa atual
        company_id = request.session.get('current_company_id')
        if not company_id:
            messages.error(request, 'Selecione uma empresa antes de importar transações.')
            return super().get(request, *args, **kwargs)
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                # Buscar contas apenas da empresa atual
                try:
                    debit_account = Account.objects.get(code=row['debit_account'], company_id=company_id)
                    credit_account = Account.objects.get(code=row['credit_account'], company_id=company_id)
                    
                    Transaction.objects.create(
                        company_id=company_id,
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        description=row['description'],
                        debit_account=debit_account,
                        credit_account=credit_account,
                        amount=row['amount'],
                        document_number=row.get('document_number', ''),
                        notes=row.get('notes', ''),
                        created_by=request.user
                    )
                except Account.DoesNotExist:
                    messages.error(request, f'Conta não encontrada para a empresa atual: {row["debit_account"]} ou {row["credit_account"]}')
                    continue
            
            messages.success(request, 'Transações importadas com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao importar transações: {str(e)}')
        
        return super().get(request, *args, **kwargs)

class TransactionExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transacoes.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Data', 'Descrição', 'Conta Débito', 'Conta Crédito',
            'Valor', 'Documento', 'Observações'
        ])
        
        # Aplicar os mesmos filtros da lista de transações
        transactions = Transaction.objects.all()
        
        # Filtrar pela empresa atual
        company_id = request.session.get('current_company_id')
        if company_id:
            transactions = transactions.filter(
                Q(debit_account__company_id=company_id) | 
                Q(credit_account__company_id=company_id)
            )
        
        # Filtros
        account_id = request.GET.get('account')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search')
        
        if account_id:
            transactions = transactions.filter(
                Q(debit_account_id=account_id) | Q(credit_account_id=account_id)
            )
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
            
        if search:
            transactions = transactions.filter(
                Q(description__icontains=search) |
                Q(document_number__icontains=search)
            )
        
        transactions = transactions.order_by('-date', '-created_at')
        
        for transaction in transactions:
            writer.writerow([
                transaction.date.strftime('%d/%m/%Y'),
                transaction.description,
                f"{transaction.debit_account.code} - {transaction.debit_account.name}",
                f"{transaction.credit_account.code} - {transaction.credit_account.name}",
                f"{transaction.amount:.2f}".replace('.', ','),
                transaction.document_number,
                transaction.notes
            ])
        
        return response

class JournalView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/journal.html'
    context_object_name = 'transactions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(
                Q(debit_account__company_id=company_id) | 
                Q(credit_account__company_id=company_id)
            )
        
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset.order_by('date', 'created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtrar contas pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            context['accounts'] = Account.objects.filter(company_id=company_id, is_active=True)
        else:
            context['accounts'] = Account.objects.filter(is_active=True)
            
        return context
