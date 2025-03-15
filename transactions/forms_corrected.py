from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from accounts.models import Account
from .models import Transaction, TransactionTemplate, TransactionTemplateItem


class TransactionForm(forms.ModelForm):
    """
    Formulário para criação e edição de transações
    """
    class Meta:
        model = Transaction
        fields = ['description', 'date', 'reference', 'debit_account', 'credit_account', 'value']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'debit_account': forms.Select(attrs={'class': 'form-control'}),
            'credit_account': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        if self.company_id:
            # Filtrar contas pelo company_id
            self.fields['debit_account'].queryset = Account.objects.filter(
                company_id=self.company_id,
                is_active=True
            )
            self.fields['credit_account'].queryset = Account.objects.filter(
                company_id=self.company_id,
                is_active=True
            )
    
    def clean_debit_account(self):
        account = self.cleaned_data.get('debit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações.'))
        return account
    
    def clean_credit_account(self):
        account = self.cleaned_data.get('credit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações.'))
        return account


class TransactionTemplateForm(forms.ModelForm):
    """
    Formulário para criação e edição de modelos de transação
    """
    class Meta:
        model = TransactionTemplate
        fields = ['name', 'description', 'template_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
        }


class AccountSelect2Widget(ModelSelect2Widget):
    """
    Widget Select2 para seleção de contas
    """
    search_fields = ['code__icontains', 'name__icontains']
    
    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        print(f"DEBUG: Inicializando AccountSelect2Widget com company_id={self.company_id}")
        super().__init__(*args, **kwargs)
    
    def filter_queryset(self, request, term, queryset=None, **kwargs):
        """
        Filtra o queryset pelo termo de busca e pelo company_id
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        # Filtrar pelo company_id se estiver disponível
        company_id = request.GET.get('company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtrar pelo termo de busca
        if term:
            for search_field in self.search_fields:
                filter_kwargs = {f'{search_field}': term}
                queryset = queryset.filter(**filter_kwargs)
        
        return queryset


class TransactionTemplateItemForm(forms.ModelForm):
    """
    Formulário para criação e edição de itens de modelo de transação
    """
    debit_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=AccountSelect2Widget(
            attrs={'data-placeholder': 'Clique com o Mouse ou Barra de Espaço para Pesquisar conta de débito...', 'style': 'width: 100%;'}
        )
    )
    
    credit_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=AccountSelect2Widget(
            attrs={'data-placeholder': 'Clique com o Mouse ou Barra de Espaço para Pesquisar conta de crédito...', 'style': 'width: 100%;'}
        )
    )
    
    class Meta:
        model = TransactionTemplateItem
        fields = ['description', 'debit_account', 'credit_account', 'value', 'is_percentage', 'order', 'is_active']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_percentage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean_debit_account(self):
        account = self.cleaned_data.get('debit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações.'))
        return account
    
    def clean_credit_account(self):
        account = self.cleaned_data.get('credit_account')
        if account and not account.is_leaf:
            raise forms.ValidationError(_('Apenas contas analíticas (de último nível) podem ser usadas em transações.'))
        return account
    
    def __init__(self, *args, **kwargs):
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        if self.company_id:
            # Filtrar contas pelo company_id
            self.fields['debit_account'].queryset = Account.objects.filter(
                company_id=self.company_id,
                is_active=True,
                is_leaf=True  # Garantir que apenas contas analíticas sejam exibidas
            )
            self.fields['debit_account'].widget.company_id = self.company_id
            
            self.fields['credit_account'].queryset = Account.objects.filter(
                company_id=self.company_id,
                is_active=True,
                is_leaf=True  # Garantir que apenas contas analíticas sejam exibidas
            )
            self.fields['credit_account'].widget.company_id = self.company_id
