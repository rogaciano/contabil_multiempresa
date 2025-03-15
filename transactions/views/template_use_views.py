"""
Views relacionadas ao uso de templates de transação.
Estas views permitem ao usuário criar múltiplos lançamentos relacionados de uma só vez,
como vendas e compras, a partir dos templates pré-definidos.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction as db_transaction
from decimal import Decimal
from datetime import date

from transactions.models import TransactionTemplate, Transaction


class TransactionFromTemplateView(LoginRequiredMixin, View):
    """
    View para criar transações a partir de um modelo.
    Esta view permite ao usuário informar apenas os valores variáveis
    e gera automaticamente todos os lançamentos relacionados.
    """
    template_name = 'transactions/transaction_from_template.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica se o usuário tem permissão para usar o template
        """
        template_id = kwargs.get('template_id')
        self.template = get_object_or_404(TransactionTemplate, pk=template_id)
        
        company_id = request.session.get('current_company_id')
        if self.template.company_id != company_id:
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
                        company_id=request.session.get('current_company_id'),
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
