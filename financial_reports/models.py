from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import Company, Account
from django.utils import timezone
import uuid

class DRETemplate(models.Model):
    """
    Modelo para armazenar templates de DRE (Demonstração do Resultado do Exercício)
    baseados no regime tributário da empresa.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descrição'), blank=True)
    tax_regime = models.CharField(
        _('Regime Tributário'),
        max_length=2,
        choices=Company.TaxRegime.choices,
        help_text=_('Regime tributário para o qual este template de DRE é aplicável')
    )
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_at = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Data de Atualização'), auto_now=True)

    class Meta:
        verbose_name = _('Template de DRE')
        verbose_name_plural = _('Templates de DRE')
        ordering = ['tax_regime', 'name']
        unique_together = ['tax_regime', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_tax_regime_display()})"


class DRESection(models.Model):
    """
    Seção do DRE, como "Receita Bruta", "Deduções", "Custos", etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        DRETemplate, 
        on_delete=models.CASCADE, 
        related_name='sections',
        verbose_name=_('Template')
    )
    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descrição'), blank=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    is_subtotal = models.BooleanField(_('É subtotal'), default=False, 
                                      help_text=_('Indica se esta seção representa um subtotal'))
    formula = models.TextField(_('Fórmula'), blank=True, 
                              help_text=_('Fórmula para calcular o valor desta seção (se for subtotal)'))
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_('Seção pai')
    )

    class Meta:
        verbose_name = _('Seção do DRE')
        verbose_name_plural = _('Seções do DRE')
        ordering = ['template', 'order']

    def __str__(self):
        return f"{self.template.name} - {self.name}"


class DREAccount(models.Model):
    """
    Associação entre contas contábeis e seções do DRE.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(
        DRESection, 
        on_delete=models.CASCADE, 
        related_name='accounts',
        verbose_name=_('Seção')
    )
    account_type = models.CharField(
        _('Tipo de Conta'), 
        max_length=20,
        help_text=_('Tipo ou código da conta contábil a ser incluída nesta seção')
    )
    multiplier = models.IntegerField(
        _('Multiplicador'), 
        default=1,
        help_text=_('1 para adicionar o valor da conta, -1 para subtrair')
    )
    
    class Meta:
        verbose_name = _('Conta do DRE')
        verbose_name_plural = _('Contas do DRE')
        ordering = ['section', 'account_type']

    def __str__(self):
        return f"{self.section.name} - {self.account_type} ({self.multiplier})"


class DREReport(models.Model):
    """
    Relatório de DRE gerado para uma empresa em um período específico.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='dre_reports',
        verbose_name=_('Empresa')
    )
    template = models.ForeignKey(
        DRETemplate, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reports',
        verbose_name=_('Template')
    )
    start_date = models.DateField(_('Data Inicial'))
    end_date = models.DateField(_('Data Final'))
    title = models.CharField(_('Título'), max_length=200)
    notes = models.TextField(_('Observações'), blank=True)
    created_at = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='dre_reports',
        verbose_name=_('Criado por')
    )

    class Meta:
        verbose_name = _('Relatório DRE')
        verbose_name_plural = _('Relatórios DRE')
        ordering = ['-end_date', 'company']

    def __str__(self):
        return f"{self.company.name} - {self.title} ({self.start_date} a {self.end_date})"
    
    def generate(self):
        """
        Gera os itens do relatório DRE com base no template e nos dados contábeis da empresa.
        """
        from django.db.models import Sum, Q
        from decimal import Decimal
        from transactions.models import Transaction
        import re
        
        # Limpar itens existentes
        self.items.all().delete()
        
        # Dicionário para armazenar valores calculados por seção
        section_values = {}
        
        # Processar cada seção do template
        for section in self.template.sections.all().order_by('order'):
            # Criar item para a seção
            item = DREReportItem.objects.create(
                report=self,
                name=section.name,
                description=section.description,
                order=section.order,
                is_subtotal=section.is_subtotal,
                section_id=section.id
            )
            
            # Se não for subtotal, calcular valor com base nas contas associadas
            if not section.is_subtotal:
                value = Decimal('0.00')
                
                # Obter contas associadas à seção
                for dre_account in section.accounts.all():
                    # Obter contas contábeis que correspondem ao tipo/código
                    accounts = Account.objects.filter(
                        company=self.company,
                        code__startswith=dre_account.account_type
                    )
                    
                    if accounts.exists():
                        account_ids = accounts.values_list('id', flat=True)
                        
                        # Calcular saldo das contas no período
                        debit_sum = Transaction.objects.filter(
                            Q(debit_account_id__in=account_ids) &
                            Q(date__gte=self.start_date) &
                            Q(date__lte=self.end_date) &
                            Q(company=self.company)
                        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                        
                        credit_sum = Transaction.objects.filter(
                            Q(credit_account_id__in=account_ids) &
                            Q(date__gte=self.start_date) &
                            Q(date__lte=self.end_date) &
                            Q(company=self.company)
                        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                        
                        # Calcular saldo final com base na natureza da conta
                        account_value = Decimal('0.00')
                        
                        # Contas de receita (3) e passivo (2) são de natureza credora
                        if dre_account.account_type.startswith('3') or dre_account.account_type.startswith('2'):
                            account_value = credit_sum - debit_sum
                        # Contas de despesa (4) e ativo (1) são de natureza devedora
                        elif dre_account.account_type.startswith('4') or dre_account.account_type.startswith('1'):
                            account_value = debit_sum - credit_sum
                        
                        # Aplicar o multiplicador
                        value += account_value * dre_account.multiplier
                
                item.value = value
                item.save()
                
                # Armazenar valor para uso em subtotais
                section_values[str(section.id)] = value
            
            # Se for subtotal, calcular com base na fórmula
            else:
                if section.formula:
                    try:
                        # Substituir IDs de seção pelos valores calculados
                        formula = section.formula
                        
                        # Encontrar todos os IDs de seção na fórmula
                        section_ids = re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', formula)
                        
                        # Substituir cada ID pelo valor correspondente
                        for section_id in section_ids:
                            if section_id in section_values:
                                formula = formula.replace(section_id, str(section_values[section_id]))
                            else:
                                formula = formula.replace(section_id, '0')
                        
                        # Avaliar a fórmula
                        value = eval(formula)
                        
                        # Converter para Decimal se necessário
                        if not isinstance(value, Decimal):
                            value = Decimal(str(value))
                        
                        item.value = value
                        item.save()
                        
                        # Armazenar valor para uso em outros subtotais
                        section_values[str(section.id)] = value
                        
                    except Exception as e:
                        # Em caso de erro, definir valor como zero
                        item.value = Decimal('0.00')
                        item.save()
                        section_values[str(section.id)] = Decimal('0.00')
                        print(f"Erro ao calcular subtotal para seção {section.name}: {str(e)}")
                else:
                    # Se não houver fórmula, definir valor como zero
                    item.value = Decimal('0.00')
                    item.save()
                    section_values[str(section.id)] = Decimal('0.00')


class DREReportItem(models.Model):
    """
    Item individual de um relatório DRE.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        DREReport, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('Relatório')
    )
    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descrição'), blank=True)
    order = models.PositiveIntegerField(_('Ordem'), default=0)
    is_subtotal = models.BooleanField(_('É subtotal'), default=False)
    value = models.DecimalField(_('Valor'), max_digits=15, decimal_places=2, default=0)
    section_id = models.UUIDField(_('ID da Seção Original'), null=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_('Item pai')
    )

    class Meta:
        verbose_name = _('Item do Relatório DRE')
        verbose_name_plural = _('Itens do Relatório DRE')
        ordering = ['report', 'order']

    def __str__(self):
        return f"{self.report.title} - {self.name}: {self.value}"
