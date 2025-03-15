from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.models import Account, Company
from decimal import Decimal

class Transaction(models.Model):
    company = models.ForeignKey(
        Company,
        verbose_name=_('Empresa'),
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    date = models.DateField(_('Data'))
    description = models.CharField(_('Descrição'), max_length=200)
    debit_account = models.ForeignKey(
        Account,
        verbose_name=_('Conta de Débito'),
        on_delete=models.PROTECT,
        related_name='debit_transactions'
    )
    credit_account = models.ForeignKey(
        Account,
        verbose_name=_('Conta de Crédito'),
        on_delete=models.PROTECT,
        related_name='credit_transactions'
    )
    amount = models.DecimalField(_('Valor'), max_digits=15, decimal_places=2)
    document_number = models.CharField(_('Número do Documento'), max_length=50, blank=True)
    notes = models.TextField(_('Observações'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Criado por'),
        on_delete=models.PROTECT,
        related_name='transactions_created'
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Transação')
        verbose_name_plural = _('Transações')
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f'{self.date} - {self.description} ({self.amount})'
    
    def clean(self):
        if self.debit_account == self.credit_account:
            raise ValidationError({
                'credit_account': _('A conta de crédito deve ser diferente da conta de débito.')
            })
        
        # Verificar se as contas pertencem à mesma empresa
        if self.debit_account and self.credit_account and self.debit_account.company != self.credit_account.company:
            raise ValidationError(_('As contas de débito e crédito devem pertencer à mesma empresa.'))
            
        if self.amount <= 0:
            raise ValidationError({
                'amount': _('O valor da transação deve ser maior que zero.')
            })
            
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('transaction_detail', kwargs={'pk': self.pk})
        
    def save(self, *args, **kwargs):
        # Se a empresa não estiver definida, usar a empresa da conta de débito
        if not self.company_id and self.debit_account_id:
            self.company = self.debit_account.company
        
        self.full_clean()
        super().save(*args, **kwargs)


class TransactionTemplate(models.Model):
    """
    Modelo para templates de transações que podem ser usados para criar várias
    transações relacionadas de uma vez (como vendas, compras, etc).
    """
    ENTRY_TYPE_CHOICES = [
        ('sale', _('Venda')),
        ('purchase', _('Compra')),
        ('payment', _('Pagamento')),
        ('receipt', _('Recebimento')),
        ('transfer', _('Transferência')),
        ('other', _('Outro')),
    ]
    
    company = models.ForeignKey(
        Company,
        verbose_name=_('Empresa'),
        on_delete=models.CASCADE,
        related_name='transaction_templates'
    )
    name = models.CharField(_('Nome'), max_length=100)
    description = models.TextField(_('Descrição'), blank=True)
    entry_type = models.CharField(
        _('Tipo de Lançamento'),
        max_length=20,
        choices=ENTRY_TYPE_CHOICES,
        default='other'
    )
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Criado por'),
        on_delete=models.PROTECT,
        related_name='templates_created'
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Modelo de Transação')
        verbose_name_plural = _('Modelos de Transação')
        ordering = ['name']
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('transaction_template_detail', kwargs={'pk': self.pk})


class TransactionTemplateItem(models.Model):
    """
    Item do template de transação, que define um dos lançamentos a serem
    criados quando o template for utilizado.
    """
    template = models.ForeignKey(
        TransactionTemplate,
        verbose_name=_('Modelo'),
        on_delete=models.CASCADE,
        related_name='items'
    )
    description = models.CharField(_('Descrição'), max_length=200)
    debit_account = models.ForeignKey(
        Account,
        verbose_name=_('Conta de Débito'),
        on_delete=models.PROTECT,
        related_name='template_debit_items'
    )
    credit_account = models.ForeignKey(
        Account,
        verbose_name=_('Conta de Crédito'),
        on_delete=models.PROTECT,
        related_name='template_credit_items'
    )
    value = models.DecimalField(
        _('Valor'),
        max_digits=15,
        decimal_places=2,
        help_text=_('Valor fixo ou percentual (se for percentual)')
    )
    is_percentage = models.BooleanField(
        _('É percentual?'),
        default=False,
        help_text=_('Se marcado, o valor será tratado como percentual do valor total')
    )
    order = models.PositiveSmallIntegerField(_('Ordem'), default=0)
    is_active = models.BooleanField(_('Ativo'), default=True)
    
    class Meta:
        verbose_name = _('Item do Modelo de Transação')
        verbose_name_plural = _('Itens do Modelo de Transação')
        ordering = ['order', 'id']
        
    def __str__(self):
        return f'{self.template.name} - {self.description}'
        
    def clean(self):
        # Verificar se as contas pertencem à mesma empresa do template
        if self.debit_account and self.template and self.debit_account.company != self.template.company:
            raise ValidationError({
                'debit_account': _('A conta de débito deve pertencer à mesma empresa do modelo.')
            })
            
        if self.credit_account and self.template and self.credit_account.company != self.template.company:
            raise ValidationError({
                'credit_account': _('A conta de crédito deve pertencer à mesma empresa do modelo.')
            })
            
        if self.debit_account == self.credit_account:
            raise ValidationError({
                'credit_account': _('A conta de crédito deve ser diferente da conta de débito.')
            })
            
        if self.value <= 0:
            raise ValidationError({
                'value': _('O valor deve ser maior que zero.')
            })
            
        if self.is_percentage and self.value > 100:
            raise ValidationError({
                'value': _('O valor percentual não pode ser maior que 100%.')
            })
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def calculate_amount(self, total_amount):
        """
        Calcula o valor real do item com base no valor total informado.
        Se o item for percentual, calcula o valor correspondente à porcentagem.
        Caso contrário, retorna o valor fixo.
        """
        if self.is_percentage:
            return (Decimal(total_amount) * self.value) / Decimal('100.0')
        return self.value
