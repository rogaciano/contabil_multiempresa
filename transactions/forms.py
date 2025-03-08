from django import forms
from django_select2 import forms as s2forms
from .models import Transaction
from accounts.models import Account
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime

# Widget personalizado para campos de data
class CustomDateInput(forms.DateInput):
    def __init__(self, attrs=None, format=None):
        attrs = attrs or {}
        attrs['type'] = 'date'
        super().__init__(attrs, format)
    
    def format_value(self, value):
        """
        Formata o valor da data para o formato ISO (YYYY-MM-DD) exigido pelo input type="date"
        """
        if value is None:
            return ''
        
        # Se já for uma string no formato ISO, retorna como está
        if isinstance(value, str) and value.strip() and len(value.strip()) == 10:
            try:
                # Verifica se está no formato brasileiro (DD/MM/YYYY)
                if '/' in value:
                    parts = value.split('/')
                    if len(parts) == 3:
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
                # Verifica se já está no formato ISO (YYYY-MM-DD)
                elif '-' in value:
                    datetime.strptime(value, '%Y-%m-%d')
                    return value
            except ValueError:
                pass
        
        # Tenta converter para o formato ISO
        try:
            if hasattr(value, 'strftime'):
                return value.strftime('%Y-%m-%d')
        except (AttributeError, ValueError):
            pass
        
        # Se tudo falhar, usa o comportamento padrão
        return super().format_value(value)

# Definir widgets personalizados para o Select2
class AccountSelect2Widget(s2forms.ModelSelect2Widget):
    model = Account
    search_fields = ['name__icontains', 'code__icontains']
    minimum_input_length = 0  # Permitir busca com qualquer quantidade de caracteres
    
    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['class'] = kwargs['attrs'].get('class', '') + ' django-select2'
        super().__init__(*args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.company_id:
            # Filtrar apenas contas analíticas (que não têm filhos)
            queryset = queryset.filter(
                company_id=self.company_id,
                is_active=True
            )
            # Usar o método is_leaf para filtrar apenas contas analíticas (que não têm filhos)
            # Como is_leaf é uma propriedade e não um campo do banco de dados,
            # precisamos filtrar depois de obter os resultados
            leaf_accounts = [account for account in queryset if account.is_leaf]
            # Converter de volta para queryset
            queryset = Account.objects.filter(pk__in=[account.pk for account in leaf_accounts])
        return queryset
    
    def filter_queryset(self, request, term, queryset=None, **kwargs):
        """Filtrar o queryset pela empresa atual e pelo termo de busca"""
        if queryset is None:
            queryset = self.get_queryset()
        
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term) | Q(code__icontains=term)
            )
        
        return queryset

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Obter a empresa atual da sessão
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar as contas pela empresa atual
        if self.company_id:
            self.fields['debit_account'].queryset = Account.objects.filter(
                company_id=self.company_id, 
                is_active=True
            )
            self.fields['credit_account'].queryset = Account.objects.filter(
                company_id=self.company_id, 
                is_active=True
            )
            
            # Atualizar os widgets com o company_id
            self.fields['debit_account'].widget.company_id = self.company_id
            self.fields['credit_account'].widget.company_id = self.company_id
    
    debit_account = forms.ModelChoiceField(
        label=_('Conta de Débito'),
        queryset=Account.objects.filter(is_active=True),
        widget=AccountSelect2Widget(
            attrs={'data-placeholder': 'Clique com o Mouse ou Barra de Espaço para Pesquisar conta de débito...', 'style': 'width: 100%;'}
        )
    )
    
    credit_account = forms.ModelChoiceField(
        label=_('Conta de Crédito'),
        queryset=Account.objects.filter(is_active=True),
        widget=AccountSelect2Widget(
            attrs={'data-placeholder': 'Clique com o Mouse ou Barra de Espaço para Pesquisar conta de crédito...', 'style': 'width: 100%;'}
        )
    )
    
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'debit_account', 'credit_account', 'amount', 'document_number', 'notes']
        widgets = {
            'date': CustomDateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        
        if not date:
            return date
            
        if not self.company_id:
            raise forms.ValidationError(_('Selecione uma empresa antes de criar uma transação.'))
            
        # Verificar se a data está dentro do período de um ano fiscal ativo
        from core.models import FiscalYear
        fiscal_year = FiscalYear.objects.filter(
            company_id=self.company_id,
            start_date__lte=date,
            end_date__gte=date,
            is_closed=False
        ).first()
        
        if not fiscal_year:
            raise forms.ValidationError(_(
                'A data da transação deve estar dentro do período de um ano fiscal ativo. '
                'Verifique se existe um ano fiscal aberto que inclua esta data.'
            ))
            
        return date
    
    def clean_debit_account(self):
        account = self.cleaned_data.get('debit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações. Contas sintéticas (com subcontas) não são permitidas.'))
        return account
    
    def clean_credit_account(self):
        account = self.cleaned_data.get('credit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações. Contas sintéticas (com subcontas) não são permitidas.'))
        return account
