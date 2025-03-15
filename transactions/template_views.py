"""
Views relacionadas aos templates de transação (facilitadores de lançamentos contábeis).
Estas views permitem criar e gerenciar templates que contêm múltiplos lançamentos
relacionados para operações comuns como vendas e compras.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from decimal import Decimal
from datetime import date

from transactions.models import TransactionTemplate, TransactionTemplateItem, Transaction
from accounts.models import Account
from transactions.forms import TransactionTemplateItemForm


class TransactionTemplateListView(LoginRequiredMixin, ListView):
    """
    View para listar templates de transação
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        """
        Filtra os templates pela empresa atual do usuário
        """
        queryset = TransactionTemplate.objects.filter(
            company=self.request.user.company
        )
        
        # Filtrar por tipo
        template_type = self.request.GET.get('type', '')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        # Filtrar por status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-is_active', 'name')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados adicionais ao contexto
        """
        context = super().get_context_data(**kwargs)
        
        # Adicionar filtros atuais ao contexto
        context['current_filters'] = {
            'type': self.request.GET.get('type', ''),
            'status': self.request.GET.get('status', ''),
        }
        
        # Adicionar tipos de template ao contexto
        context['template_types'] = TransactionTemplate.TEMPLATE_TYPES
        
        return context


class TransactionTemplateDetailView(LoginRequiredMixin, DetailView):
    """
    View para exibir detalhes de um template de transação
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_detail.html'
    
    def get_context_data(self, **kwargs):
        """
        Adiciona os itens do template ao contexto
        """
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all().order_by('order', 'id')
        return context


class TransactionTemplateCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar um novo template de transação
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_form.html'
    fields = ['name', 'description', 'template_type']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem uma empresa selecionada
        """
        if not request.user.company:
            messages.error(request, _('Selecione uma empresa para continuar.'))
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Define a empresa do template como a empresa atual do usuário
        """
        form.instance.company = self.request.user.company
        messages.success(self.request, _('Template de transação criado com sucesso!'))
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Redireciona para a página de edição do template após a criação
        """
        return reverse('transaction_template_edit', kwargs={'pk': self.object.pk})


class TransactionTemplateUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para atualizar um template de transação existente
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_form.html'
    fields = ['name', 'description', 'template_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para editar o template
        """
        template = self.get_object()
        if template.company != request.user.company:
            messages.error(request, _('Você não tem permissão para editar este template.'))
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Redireciona para a página de detalhes do template após a atualização
        """
        return reverse('transaction_template_detail', kwargs={'pk': self.object.pk})


class TransactionTemplateDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir um template de transação
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_confirm_delete.html'
    success_url = reverse_lazy('transaction_template_list')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para excluir o template
        """
        template = self.get_object()
        if template.company != request.user.company:
            messages.error(request, _('Você não tem permissão para excluir este template.'))
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """
        Exclui o template e exibe mensagem de sucesso
        """
        messages.success(request, _('Template de transação excluído com sucesso!'))
        return super().delete(request, *args, **kwargs)


def transaction_template_item_create(request, template_id):
    """
    Cria um novo item para um template de transação
    """
    template = get_object_or_404(TransactionTemplate, pk=template_id)
    
    # Verificar se o usuário tem permissão para editar o template
    if template.company != request.user.company:
        messages.error(request, _('Você não tem permissão para editar este template.'))
        return redirect('transaction_template_list')
    
    if request.method == 'POST':
        form = TransactionTemplateItemForm(request.POST, company_id=template.company_id)
        
        # Definir o template antes da validação para evitar o erro "TransactionTemplateItem has no template"
        form.instance.template = template
        
        if form.is_valid():
            item = form.save()
            messages.success(request, _('Item adicionado com sucesso!'))
            return redirect('transaction_template_edit', pk=template.pk)
    else:
        form = TransactionTemplateItemForm(company_id=template.company_id)
    
    # Adicionar company_id ao contexto para uso no template
    context = {
        'form': form,
        'template': template,
        'company_id': template.company_id,
    }
    
    return render(request, 'transactions/transaction_template_item_form.html', context)


class TransactionTemplateItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para atualizar um item de template de transação
    """
    model = TransactionTemplateItem
    form_class = TransactionTemplateItemForm
    template_name = 'transactions/transaction_template_item_form.html'
    
    def get_success_url(self):
        return reverse_lazy('transaction_template_edit', kwargs={'pk': self.object.template.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passar o company_id para o formulário
        kwargs['company_id'] = self.object.template.company_id
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar o template e o company_id ao contexto
        context['template'] = self.object.template
        context['company_id'] = self.object.template.company_id
        return context
    
    def form_valid(self, form):
        """
        Salva o item e exibe mensagem de sucesso
        """
        messages.success(self.request, _('Item atualizado com sucesso!'))
        return super().form_valid(form)


class TransactionTemplateItemDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir um item de template de transação
    """
    model = TransactionTemplateItem
    template_name = 'transactions/transaction_template_item_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para excluir o item
        """
        item = self.get_object()
        if item.template.company != request.user.company:
            messages.error(request, _('Você não tem permissão para excluir este item.'))
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """
        Redireciona para a página de edição do template após a exclusão
        """
        return reverse('transaction_template_edit', kwargs={'pk': self.object.template.pk})


class TransactionTemplateEditView(LoginRequiredMixin, UpdateView):
    """
    View para edição completa do template, incluindo seus itens.
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_edit.html'
    fields = ['name', 'description', 'template_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para editar o template
        """
        template = self.get_object()
        if template.company != request.user.company:
            messages.error(request, _('Você não tem permissão para editar este template.'))
            return redirect('transaction_template_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Adiciona os itens do template ao contexto
        """
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all().order_by('order', 'id')
        return context
    
    def get_success_url(self):
        """
        Redireciona para a mesma página após a atualização
        """
        return reverse('transaction_template_edit', kwargs={'pk': self.object.pk})


class TransactionFromTemplateView(LoginRequiredMixin, ListView):
    """
    View para criar transações a partir de um modelo.
    Esta view permite ao usuário informar apenas os valores variáveis
    e gera automaticamente todos os lançamentos relacionados.
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_from_template.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para usar o template
        """
        template_id = kwargs.get('template_id')
        self.template = get_object_or_404(TransactionTemplate, pk=template_id)
        
        if self.template.company != request.user.company:
            messages.error(request, _('Você não tem permissão para usar este template.'))
            return redirect('transaction_template_list')
        
        if not self.template.is_active:
            messages.error(request, _('Este template está inativo e não pode ser usado.'))
            return redirect('transaction_template_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """
        Exibe o formulário para usar o template
        """
        # Obter os itens do template
        items = self.template.items.filter(is_active=True).order_by('order', 'id')
        
        # Verificar se o template tem pelo menos um item
        if not items.exists():
            messages.error(request, _('Este template não possui itens configurados.'))
            return redirect('transaction_template_list')
        
        # Preparar contexto
        context = {
            'template': self.template,
            'items': items,
            'today': date.today().strftime('%Y-%m-%d'),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        """
        Processa o formulário e cria as transações
        """
        # Obter dados do formulário
        transaction_date = request.POST.get('date')
        description = request.POST.get('description')
        reference = request.POST.get('reference', '')
        base_value = request.POST.get('base_value')
        
        # Validar dados
        errors = []
        
        if not transaction_date:
            errors.append(_('A data é obrigatória.'))
        
        if not description:
            errors.append(_('A descrição é obrigatória.'))
        
        if not base_value:
            errors.append(_('O valor base é obrigatório.'))
        else:
            try:
                base_value = Decimal(base_value.replace(',', '.'))
                if base_value <= 0:
                    errors.append(_('O valor base deve ser maior que zero.'))
            except:
                errors.append(_('O valor base deve ser um número válido.'))
        
        # Se houver erros, exibir mensagens e retornar ao formulário
        if errors:
            for error in errors:
                messages.error(request, error)
            
            # Obter os itens do template
            items = self.template.items.filter(is_active=True).order_by('order', 'id')
            
            # Preparar contexto
            context = {
                'template': self.template,
                'items': items,
                'today': transaction_date or date.today().strftime('%Y-%m-%d'),
                'description': description,
                'reference': reference,
                'base_value': base_value,
            }
            
            return render(request, self.template_name, context)
        
        # Converter data
        try:
            transaction_date = date.fromisoformat(transaction_date)
        except ValueError:
            messages.error(request, _('Data inválida.'))
            return redirect('transaction_from_template', template_id=self.template.pk)
        
        # Criar transações
        try:
            with db_transaction.atomic():
                # Obter os itens do template
                items = self.template.items.filter(is_active=True).order_by('order', 'id')
                
                # Criar uma transação para cada item
                for item in items:
                    # Calcular o valor da transação
                    if item.is_percentage and item.value is not None:
                        # Calcular valor baseado na porcentagem
                        transaction_value = base_value * (item.value / Decimal('100'))
                    elif not item.is_percentage and item.value is not None:
                        # Usar valor fixo
                        transaction_value = item.value
                    else:
                        # Usar valor base
                        transaction_value = base_value
                    
                    # Criar a transação
                    Transaction.objects.create(
                        company=request.user.company,
                        date=transaction_date,
                        description=f"{description} - {item.description}" if item.description else description,
                        reference=reference,
                        debit_account=item.debit_account,
                        credit_account=item.credit_account,
                        value=transaction_value,
                        created_by=request.user
                    )
                
                messages.success(request, _('Lançamentos criados com sucesso!'))
                return redirect('transaction_list')
                
        except Exception as e:
            messages.error(request, _('Erro ao criar lançamentos: {}').format(str(e)))
            return redirect('transaction_from_template', template_id=self.template.pk)


# Função auxiliar para busca de contas via AJAX para o Select2
def account_search(request):
    """
    View para buscar contas via AJAX para o Select2
    
    Esta view é usada pelos componentes Select2 para buscar contas
    com base em um termo de pesquisa e filtrar pelo company_id.
    """
    # Obter parâmetros da requisição
    term = request.GET.get('term', '')
    company_id = request.GET.get('company_id')
    
    # Validar company_id
    if not company_id:
        company_id = request.user.company_id
    
    # Inicializar queryset
    queryset = Account.objects.filter(company_id=company_id, is_active=True)
    
    # Filtrar pelo termo de busca
    if term:
        queryset = queryset.filter(
            Q(code__icontains=term) | 
            Q(name__icontains=term)
        )
    
    # Limitar resultados
    queryset = queryset[:20]
    
    # Formatar resultados para o Select2
    results = []
    for account in queryset:
        results.append({
            'id': account.id,
            'text': f"{account.code} - {account.name}"
        })
    
    # Retornar resposta JSON
    return JsonResponse({
        'results': results,
        'pagination': {
            'more': False
        }
    })
