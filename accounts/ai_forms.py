from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Company

class AIAccountPlanForm(forms.Form):
    """Formulário para coletar informações para geração de plano de contas com IA"""
    
    BUSINESS_TYPE_CHOICES = [
        ('comercio', _('Comércio')),
        ('servicos', _('Serviços')),
        ('industria', _('Indústria')),
        ('outro', _('Outro')),
    ]
    
    business_type = forms.ChoiceField(
        label=_('Tipo de Negócio'),
        choices=BUSINESS_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )
    
    business_subtype = forms.CharField(
        label=_('Subtipo/Segmento'),
        max_length=100,
        required=True,
        help_text=_('Ex: Varejo de roupas, Consultoria de TI, Fabricação de móveis, etc.')
    )
    
    business_size = forms.ChoiceField(
        label=_('Porte da Empresa'),
        choices=[
            ('micro', _('Microempresa')),
            ('pequena', _('Empresa de Pequeno Porte')),
            ('media', _('Empresa de Médio Porte')),
            ('grande', _('Empresa de Grande Porte')),
        ],
        required=True,
    )
    
    # Campo oculto que será preenchido automaticamente com o regime tributário da empresa ativa
    tax_regime = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    additional_details = forms.CharField(
        label=_('Detalhes Adicionais'),
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text=_('Forneça informações adicionais relevantes sobre o negócio que possam ajudar na criação do plano de contas.')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Se o tipo de negócio for "outro", o subtipo é obrigatório
        if cleaned_data.get('business_type') == 'outro' and not cleaned_data.get('business_subtype'):
            self.add_error('business_subtype', _('Por favor, especifique o tipo de negócio.'))
            
        return cleaned_data
