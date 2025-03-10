from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FiscalYear
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FiscalYearForm(forms.ModelForm):
    class Meta:
        model = FiscalYear
        fields = ['year', 'start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Definir valores padrão para o ano fiscal
        if not self.instance.pk and not self.initial.get('year'):
            current_year = datetime.date.today().year
            # Não definimos o ano automaticamente, apenas as datas
            # self.initial['year'] = current_year
            self.initial['start_date'] = datetime.date(current_year, 1, 1)
            self.initial['end_date'] = datetime.date(current_year, 12, 31)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('A data de início deve ser anterior à data de término.'))
        
        # Verificar se já existe um ano fiscal com o mesmo período para esta empresa
        if self.company:
            overlapping = FiscalYear.objects.filter(
                company=self.company,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Excluir a instância atual se estiver editando
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise forms.ValidationError(_('Já existe um ano fiscal que se sobrepõe a este período.'))
        
        return cleaned_data

class FiscalYearCloseForm(forms.ModelForm):
    confirm_close = forms.BooleanField(
        label=_('Confirmo que desejo fechar este ano fiscal'),
        required=True,
        help_text=_('Esta ação não pode ser desfeita. Todos os saldos serão transferidos para o próximo ano fiscal.')
    )
    
    class Meta:
        model = FiscalYear
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Adicione notas sobre o fechamento deste ano fiscal')}),
        }
    
    def __init__(self, *args, **kwargs):
        self.fiscal_year = kwargs.pop('fiscal_year', None)
        super().__init__(*args, **kwargs)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        help_text=_('Informe um email válido para confirmação da conta.')
    )
    
    first_name = forms.CharField(
        required=True,
        label=_('Nome'),
        max_length=30
    )
    
    last_name = forms.CharField(
        required=True,
        label=_('Sobrenome'),
        max_length=30
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Este email já está em uso.'))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
