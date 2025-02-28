from django import forms
from django_select2.forms import ModelSelect2Widget
from .models import Transaction
from accounts.models import Account

class TransactionForm(forms.ModelForm):
    debit_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=ModelSelect2Widget(
            model=Account,
            search_fields=['name__icontains', 'code__icontains'],
            attrs={'data-placeholder': 'Pesquisar conta de débito...', 'style': 'width: 100%;'}
        )
    )
    
    credit_account = forms.ModelChoiceField(
        queryset=Account.objects.filter(is_active=True),
        widget=ModelSelect2Widget(
            model=Account,
            search_fields=['name__icontains', 'code__icontains'],
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
