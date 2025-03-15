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

from transactions.models import TransactionTemplate, TransactionTemplateItem
from accounts.models import Account
from transactions.forms import TransactionTemplateItemForm
from django.db.models import Q


class TransactionTemplateListView(LoginRequiredMixin, ListView):
    """
    View para listar templates de transação
    """
    model = TransactionTemplate
    template_name = 'transactions/transaction_template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar templates pela empresa atual da sessão
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
            
        return queryset.order_by('-is_active', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entry_types'] = TransactionTemplate.ENTRY_TYPE_CHOICES
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
    fields = ['name', 'description', 'entry_type']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem uma empresa selecionada
        """
        if not request.session.get('current_company_id'):
            messages.error(request, _('Selecione uma empresa para continuar.'))
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Define a empresa do template como a empresa atual da sessão
        e o usuário criador como o usuário atual
        """
        form.instance.company_id = self.request.session.get('current_company_id')
        form.instance.created_by = self.request.user
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
    fields = ['name', 'description', 'entry_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para editar o template
        """
        template = self.get_object()
        company_id = request.session.get('current_company_id')
        if template.company_id != company_id:
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
        company_id = request.session.get('current_company_id')
        if template.company_id != company_id:
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
    company_id = request.session.get('current_company_id')
    if template.company_id != company_id:
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
        company_id = request.session.get('current_company_id')
        if item.template.company_id != company_id:
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
    fields = ['name', 'description', 'entry_type', 'is_active']
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para editar o template
        """
        template = self.get_object()
        company_id = request.session.get('current_company_id')
        if template.company_id != company_id:
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
