from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.models import Account

class Transaction(models.Model):
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
            
        if self.amount <= 0:
            raise ValidationError({
                'amount': _('O valor da transação deve ser maior que zero.')
            })
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('transaction_detail', kwargs={'pk': self.pk})
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
