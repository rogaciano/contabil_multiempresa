from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Account, UserProfile, Company


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'type', 'parent', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)
        self.company_id = company_id  # Armazenar o company_id para uso posterior
        super().__init__(*args, **kwargs)
        
        if company_id:
            # Filtrar contas pai pela empresa atual
            self.fields['parent'].queryset = Account.objects.filter(company_id=company_id)
            
            # Se estamos editando uma conta existente, filtrar pelo tipo atual
            if self.instance and self.instance.pk and self.instance.type:
                self.fields['parent'].queryset = self.fields['parent'].queryset.filter(
                    type=self.instance.type
                ).exclude(pk=self.instance.pk)
            # Se temos dados de formulário com um tipo selecionado, filtrar por esse tipo
            elif self.data and 'type' in self.data:
                selected_type = self.data.get('type')
                if selected_type:
                    self.fields['parent'].queryset = self.fields['parent'].queryset.filter(
                        type=selected_type
                    )
        else:
            self.fields['parent'].queryset = Account.objects.none()
        
        # Adicionar evento JavaScript para atualizar as opções do campo parent quando o tipo mudar
        self.fields['type'].widget.attrs.update({
            'onchange': 'updateParentOptions(this.value)'
        })


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': _('Nome'),
            'last_name': _('Sobrenome'),
            'email': _('Email'),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = []  # Por enquanto, não temos campos adicionais para editar


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'tax_id', 'tax_regime', 'address', 'phone', 'email']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'tax_regime': forms.Select(attrs={'class': 'form-select'}),
        }
