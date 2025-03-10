from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounts.models import Company
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.

class FiscalYear(models.Model):
    company = models.ForeignKey(
        Company,
        verbose_name=_('Empresa'),
        on_delete=models.CASCADE,
        related_name='fiscal_years'
    )
    year = models.PositiveIntegerField(_('Ano'))
    start_date = models.DateField(_('Data Inicial'))
    end_date = models.DateField(_('Data Final'))
    is_closed = models.BooleanField(_('Fechado'), default=False)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Fechado por'),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    closed_at = models.DateTimeField(_('Fechado em'), null=True, blank=True)
    notes = models.TextField(_('Observações'), blank=True)
    
    class Meta:
        verbose_name = _('Ano Fiscal')
        verbose_name_plural = _('Anos Fiscais')
        ordering = ['-year']
        unique_together = ['company', 'year']  # Ano fiscal deve ser único por empresa
        
    def __str__(self):
        return f'Ano Fiscal {self.year} - {self.company.name}'

class UserActivationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activation_token')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Token para {self.user.username}"
    
    def is_valid(self):
        return timezone.now() <= self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token válido por 7 dias
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

class AccessLog(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('Usuário'),
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    timestamp = models.DateTimeField(_('Data/Hora'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('Endereço IP'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), null=True, blank=True)
    account_count = models.IntegerField(_('Qtd. Contas'), default=0)
    company_count = models.IntegerField(_('Qtd. Empresas'), default=0)
    fiscal_year_count = models.IntegerField(_('Qtd. Anos Fiscais'), default=0)
    transaction_count = models.IntegerField(_('Qtd. Lançamentos'), default=0)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Log de Acesso')
        verbose_name_plural = _('Logs de Acesso')
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
