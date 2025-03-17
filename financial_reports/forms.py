from django import forms
from django.utils.translation import gettext_lazy as _
from .models import DRETemplate, DRESection, DREAccount, DREReport
from accounts.models import Company
from django.utils import timezone
import datetime

class DRETemplateForm(forms.ModelForm):
    class Meta:
        model = DRETemplate
        fields = ['name', 'description', 'tax_regime', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tax_regime': forms.Select(attrs={'class': 'form-select'}),
        }


class DRESectionForm(forms.ModelForm):
    class Meta:
        model = DRESection
        fields = ['name', 'description', 'order', 'is_subtotal', 'formula', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'formula': forms.Textarea(attrs={'rows': 2}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        template = kwargs.pop('template', None)
        super().__init__(*args, **kwargs)
        
        if template:
            # Filtrar apenas seções do mesmo template
            self.fields['parent'].queryset = DRESection.objects.filter(template=template)
        elif self.instance and self.instance.pk:
            # Filtrar apenas seções do mesmo template, excluindo a própria seção
            self.fields['parent'].queryset = DRESection.objects.filter(
                template=self.instance.template
            ).exclude(pk=self.instance.pk)


class DREAccountForm(forms.ModelForm):
    class Meta:
        model = DREAccount
        fields = ['account_type', 'multiplier']
        widgets = {
            'account_type': forms.TextInput(attrs={'class': 'form-control'}),
            'multiplier': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DREReportForm(forms.ModelForm):
    class Meta:
        model = DREReport
        fields = ['title', 'start_date', 'end_date', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        
        # Definir valores iniciais para as datas
        if not self.instance.pk:
            # Para novos relatórios, usar o mês atual
            today = timezone.now().date()
            first_day = datetime.date(today.year, today.month, 1)
            last_day = (datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)) if today.month < 12 else datetime.date(today.year, 12, 31)
            
            self.fields['start_date'].initial = first_day
            self.fields['end_date'].initial = last_day
            self.fields['title'].initial = f"DRE - {first_day.strftime('%b/%Y')}"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('A data inicial não pode ser posterior à data final.'))
            
        return cleaned_data
