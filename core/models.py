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
