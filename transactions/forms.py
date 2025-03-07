from django import forms
from django_select2 import forms as s2forms
from .models import Transaction
from accounts.models import Account
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Definir widgets personalizados para o Select2
class AccountSelect2Widget(s2forms.ModelSelect2Widget):
    model = Account
    search_fields = ['name__icontains', 'code__icontains']
    
    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['class'] = kwargs['attrs'].get('class', '') + ' django-select2'
        super().__init__(*args, **kwargs)
    
    def get_queryset(self):
        return Account.objects.filter(is_active=True)
    
    def filter_queryset(self, request, term, queryset=None, **kwargs):
        """Filtrar o queryset pela empresa atual e pelo termo de busca"""
        queryset = self.get_queryset()
        
        # Filtrar pela empresa atual
        company_id = self.company_id or request.session.get('current_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id, is_active=True)
        
        # Filtrar pelo termo de busca
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
            attrs={'data-placeholder': 'Pesquisar conta de débito...', 'style': 'width: 100%;'}
        )
    )
    
    credit_account = forms.ModelChoiceField(
        label=_('Conta de Crédito'),
        queryset=Account.objects.filter(is_active=True),
        widget=AccountSelect2Widget(
            attrs={'data-placeholder': 'Pesquisar conta de crédito...', 'style': 'width: 100%;'}
        )
    )
    
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'debit_account', 'credit_account', 'amount', 'document_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
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
