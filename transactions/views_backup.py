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

from .models import Transaction, TransactionTemplate, TransactionTemplateItem
from accounts.models import Account
from .forms import TransactionForm, TransactionTemplateItemForm
from core.models import FiscalYear

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
        
        # Adicionar contas para o filtro
        company_id = self.request.session.get('current_company_id')
        if company_id:
            context['accounts'] = Account.objects.filter(company_id=company_id, is_active=True)
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se existe um ano fiscal ativo para a empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            # Verificar se existe pelo menos um ano fiscal para a empresa atual
            has_fiscal_year = FiscalYear.objects.filter(company_id=company_id).exists()
            if not has_fiscal_year:
                messages.warning(request, 'Você precisa cadastrar um ano fiscal antes de acessar as transações.')
                # Redirecionar para a criação de ano fiscal com parâmetro next
                return redirect(f"{reverse('fiscal_year_create')}?next={reverse('transaction_list')}")
        
        return super().dispatch(request, *args, **kwargs)

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    form_class = TransactionForm
    success_url = reverse_lazy('transaction_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se existe um ano fiscal ativo para a empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            # Verificar se existe pelo menos um ano fiscal para a empresa atual
            has_fiscal_year = FiscalYear.objects.filter(company_id=company_id).exists()
            if not has_fiscal_year:
                messages.warning(request, 'Você precisa cadastrar um ano fiscal antes de criar uma transação.')
                # Redirecionar para a criação de ano fiscal com parâmetro next
                return redirect(f"{reverse('fiscal_year_create')}?next={reverse('transaction_create')}")
        
        return super().dispatch(request, *args, **kwargs)
    
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
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se existe um ano fiscal ativo para a empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            # Verificar se existe pelo menos um ano fiscal para a empresa atual
            has_fiscal_year = FiscalYear.objects.filter(company_id=company_id).exists()
            if not has_fiscal_year:
                messages.warning(request, 'Você precisa cadastrar um ano fiscal antes de editar uma transação.')
                # Redirecionar para a criação de ano fiscal com parâmetro next
                current_url = request.path
                return redirect(f"{reverse('fiscal_year_create')}?next={current_url}")
        
        return super().dispatch(request, *args, **kwargs)
    
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

class TransactionTemplateListView(LoginRequiredMixin, ListView):
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar templates pela empresa atual
        company_id = self.request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtros
        entry_type = self.request.GET.get('entry_type')
        search = self.request.GET.get('search')
        
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)
            
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entry_types'] = TransactionTemplate.ENTRY_TYPE_CHOICES
        return context


class TransactionTemplateDetailView(LoginRequiredMixin, DetailView):
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all().order_by('order')
        return context


class TransactionTemplateCreateView(LoginRequiredMixin, CreateView):
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_form.html'
    fields = ['name', 'description', 'entry_type']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário tem uma empresa selecionada
        if not request.session.get('current_company_id'):
            messages.error(request, 'Selecione uma empresa antes de criar um modelo de lançamento.')
            return redirect('company_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('current_company_id')
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Modelo de lançamento criado com sucesso! Agora adicione os itens do modelo.')
        return reverse('transaction_template_edit', kwargs={'pk': self.object.pk})


class TransactionTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_form.html'
    fields = ['name', 'description', 'entry_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o modelo pertence à empresa atual
        template = self.get_object()
        if template.company_id != request.session.get('current_company_id'):
            messages.error(request, 'Você não tem permissão para editar este modelo de lançamento.')
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Modelo de lançamento atualizado com sucesso!')
        return reverse('transaction_template_detail', kwargs={'pk': self.object.pk})


class TransactionTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_confirm_delete.html'
    success_url = reverse_lazy('transaction_template_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o modelo pertence à empresa atual
        template = self.get_object()
        if template.company_id != request.session.get('current_company_id'):
            messages.error(request, 'Você não tem permissão para excluir este modelo de lançamento.')
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Modelo de lançamento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


def transaction_template_item_create(request, template_id):
    """
    Cria um novo item para um template de transação
    """
    template = get_object_or_404(TransactionTemplate, pk=template_id)
    
    # Verificar se o usuário tem permissão para editar o template
    if not request.user.has_perm('transactions.change_transactiontemplate') and template.created_by != request.user:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('transaction_template_detail', pk=template_id)
    
    # Verificar se o template pertence à empresa atual
    if template.company_id != request.session.get('current_company_id'):
        messages.error(request, _('Este template não pertence à empresa atual.'))
        return redirect('transaction_template_list')
    
    print(f"DEBUG: Template company_id: {template.company_id}")
    
    if request.method == 'POST':
        form = TransactionTemplateItemForm(request.POST, company_id=template.company_id)
        
        # Criar uma instância do item e definir o template antes da validação
        item = form.instance
        item.template = template
        
        if form.is_valid():
            # Definir a ordem do item como a última ordem + 1
            last_item = TransactionTemplateItem.objects.filter(template=template).order_by('-order').first()
            item.order = (last_item.order + 1) if last_item else 1
            
            # Validar se a conta de débito e crédito são contas analíticas
            if not item.debit_account.is_leaf:
                form.add_error('debit_account', _('A conta de débito deve ser uma conta analítica.'))
                return render(request, 'transactions/transaction_template_item_form.html', {
                    'form': form,
                    'template': template,
                    'company_id': template.company_id,
                })
            
            if not item.credit_account.is_leaf:
                form.add_error('credit_account', _('A conta de crédito deve ser uma conta analítica.'))
                return render(request, 'transactions/transaction_template_item_form.html', {
                    'form': form,
                    'template': template,
                    'company_id': template.company_id,
                })
            
            # Validar se o valor é válido
            if not item.is_percentage and not item.value:
                form.add_error('value', _('O valor é obrigatório para itens com valor fixo.'))
                return render(request, 'transactions/transaction_template_item_form.html', {
                    'form': form,
                    'template': template,
                    'company_id': template.company_id,
                })
            
            if item.is_percentage and (not item.value or item.value <= 0 or item.value > 100):
                form.add_error('value', _('O percentual deve ser maior que 0 e menor ou igual a 100.'))
                return render(request, 'transactions/transaction_template_item_form.html', {
                    'form': form,
                    'template': template,
                    'company_id': template.company_id,
                })
            
            form.save()
            messages.success(request, _('Item adicionado com sucesso!'))
            return redirect('transaction_template_edit', pk=template_id)
    else:
        form = TransactionTemplateItemForm(company_id=template.company_id)
    
    # Adicionar company_id ao contexto para uso no template
    context = {
        'form': form,
        'template': template,
        'company_id': template.company_id,
    }
    
    print(f"DEBUG: Renderizando formulário com company_id={template.company_id}")
    
    return render(request, 'transactions/transaction_template_item_form.html', context)


class TransactionTemplateItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para atualizar um item de template de transação
    """
    model = TransactionTemplateItem
    form_class = TransactionTemplateItemForm
    template_name = 'transactions/transaction_template_item_form.html'
    
    def get_success_url(self):
        return reverse_lazy('transaction_template_detail', kwargs={'pk': self.object.template.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passar o company_id para o formulário
        kwargs['company_id'] = self.object.template.company_id
        print(f"DEBUG: TransactionTemplateItemUpdateView.get_form_kwargs - company_id={kwargs['company_id']}")
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar o template e o company_id ao contexto
        context['template'] = self.object.template
        context['company_id'] = self.object.template.company_id
        print(f"DEBUG: TransactionTemplateItemUpdateView.get_context_data - company_id={context['company_id']}")
        return context
    
    def form_valid(self, form):
        # Verificar se o usuário tem permissão para editar o template
        if not self.request.user.has_perm('transactions.change_transactiontemplate') and self.object.template.created_by != self.request.user:
            messages.error(self.request, _('Você não tem permissão para editar este template.'))
            return redirect('transaction_template_detail', pk=self.object.template.pk)
        
        # Verificar se o template pertence à empresa atual
        if self.object.template.company_id != self.request.session.get('current_company_id'):
            messages.error(self.request, _('Este template não pertence à empresa atual.'))
            return redirect('transaction_template_list')
        
        # Validar se a conta de débito e crédito são contas analíticas
        item = form.save(commit=False)
        if not item.debit_account.is_leaf:
            form.add_error('debit_account', _('A conta de débito deve ser uma conta analítica.'))
            return self.form_invalid(form)
        
        if not item.credit_account.is_leaf:
            form.add_error('credit_account', _('A conta de crédito deve ser uma conta analítica.'))
            return self.form_invalid(form)
        
        # Validar se o valor é válido
        if not item.is_percentage and not item.value:
            form.add_error('value', _('O valor é obrigatório para itens com valor fixo.'))
            return self.form_invalid(form)
        
        if item.is_percentage and (not item.value or item.value <= 0 or item.value > 100):
            form.add_error('value', _('O percentual deve ser maior que 0 e menor ou igual a 100.'))
            return self.form_invalid(form)
        
        messages.success(self.request, _('Item atualizado com sucesso.'))
        return super().form_valid(form)


class TransactionTemplateItemDeleteView(LoginRequiredMixin, DeleteView):
    model = TransactionTemplateItem
    template_name = 'transactions/transaction_template_item_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o item pertence à empresa atual
        item = self.get_object()
        if item.template.company_id != request.session.get('current_company_id'):
            messages.error(request, 'Você não tem permissão para excluir este item.')
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        messages.success(self.request, 'Item excluído com sucesso!')
        return reverse('transaction_template_edit', kwargs={'pk': self.object.template.pk})

class TransactionTemplateEditView(LoginRequiredMixin, UpdateView):
    """
    View para edição completa do template, incluindo seus itens.
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_edit.html'
    fields = ['name', 'description', 'entry_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o template pertence à empresa atual
        template = self.get_object()
        if template.company_id != request.session.get('current_company_id'):
            messages.error(request, 'Você não tem permissão para editar este modelo.')
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all().order_by('order')
        # Adicionar informações da empresa para filtrar contas
        context['company_id'] = self.object.company_id
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Modelo atualizado com sucesso!')
        return reverse('transaction_template_edit', kwargs={'pk': self.object.pk})

class TransactionFromTemplateView(LoginRequiredMixin, View):
    """
    View para criar transações a partir de um modelo.
    """
    template_name = 'transactions/transaction_from_template.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Obter o template e verificar se pertence à empresa atual
        self.template = get_object_or_404(TransactionTemplate, pk=self.kwargs['template_id'])
        if self.template.company_id != request.session.get('current_company_id'):
            messages.error(request, 'Você não tem permissão para usar este modelo.')
            return redirect('transaction_template_list')
        
        # Verificar se o template tem itens
        if not self.template.items.filter(is_active=True).exists():
            messages.error(request, 'Este modelo não possui itens ativos.')
            return redirect('transaction_template_edit', pk=self.template.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Preparar os dados dos itens para serialização JSON
        items_data = []
        for item in self.template.items.filter(is_active=True).order_by('order'):
            items_data.append({
                'id': item.id,
                'description': item.description or '',
                'debitAccount': f"{item.debit_account.code} - {item.debit_account.name}",
                'creditAccount': f"{item.credit_account.code} - {item.credit_account.name}",
                'value': float(item.value) if item.value is not None else None,
                'isPercentage': item.is_percentage,
                'order': item.order
            })
            
        context = {
            'template': self.template,
            'items': self.template.items.filter(is_active=True).order_by('order'),
            'items_data': items_data
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Obter os dados do formulário
        try:
            base_amount = Decimal(request.POST.get('base_amount', '0').replace(',', '.'))
            date_str = request.POST.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            description = request.POST.get('description', '')
            document_number = request.POST.get('document_number', '')
            notes = request.POST.get('notes', '')
            
            # Validar os dados
            if not base_amount or base_amount <= 0:
                messages.error(request, 'O valor base deve ser maior que zero.')
                return self.get(request, *args, **kwargs)
                
            if not date:
                messages.error(request, 'A data é obrigatória.')
                return self.get(request, *args, **kwargs)
                
            if not description:
                messages.error(request, 'A descrição é obrigatória.')
                return self.get(request, *args, **kwargs)
            
            # Gerar as transações com base no template
            with db_transaction.atomic():
                transactions = self.template.generate_transactions(
                    base_amount=base_amount,
                    date=date,
                    description=description,
                    document_number=document_number,
                    notes=notes,
                    user=self.request.user
                )
                
                # Salvar todas as transações
                for transaction in transactions:
                    transaction.save()
            
            # Mensagem de sucesso
            messages.success(
                self.request, 
                f'Foram criados {len(transactions)} lançamentos com sucesso a partir do modelo "{self.template.name}"!'
            )
            
            # Redirecionar para a lista de transações
            return redirect('transaction_list')
            
        except (ValueError, TypeError, InvalidOperation) as e:
            messages.error(request, f'Erro ao processar os dados do formulário: {str(e)}')
            return self.get(request, *args, **kwargs)

def account_search(request):
    """
    View para buscar contas via AJAX para o Select2
    """
    term = request.GET.get('term', '')
    company_id = request.GET.get('company_id')
    
    print(f"DEBUG: Buscando contas com term={term}, company_id={company_id}")
    
    # Iniciar com todas as contas ativas
    queryset = Account.objects.filter(is_active=True)
    
    # Filtrar por empresa se company_id estiver presente
    if company_id:
        queryset = queryset.filter(company_id=company_id)
        print(f"DEBUG: Filtrado por company_id={company_id}, encontradas {queryset.count()} contas")
    
    # Filtrar pelo termo de busca
    if term:
        queryset = queryset.filter(
            Q(name__icontains=term) | Q(code__icontains=term)
        )
        print(f"DEBUG: Filtrado por term={term}, encontradas {queryset.count()} contas")
    
    # Filtrar apenas contas analíticas (que não têm filhos)
    # Como is_leaf é uma propriedade e não um campo do banco de dados,
    # precisamos filtrar depois de obter os resultados
    leaf_accounts = [account for account in queryset if account.is_leaf]
    print(f"DEBUG: Filtrado para contas analíticas, encontradas {len(leaf_accounts)} contas")
    
    # Formatar os resultados para o Select2
    results = []
    for account in leaf_accounts[:20]:  # Limitar a 20 resultados
        results.append({
            'id': account.id,
            'text': f"{account.code} - {account.name}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'more': len(leaf_accounts) > 20  # Indicar se há mais resultados
        }
    })
