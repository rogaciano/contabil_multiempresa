from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

class CompanyInfo(models.Model):
    name = models.CharField(_('Nome da Empresa'), max_length=100)
    cnpj = models.CharField(_('CNPJ'), max_length=18, unique=True)
    address = models.TextField(_('Endereço'))
    phone = models.CharField(_('Telefone'), max_length=20)
    email = models.EmailField(_('E-mail'))
    website = models.URLField(_('Website'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='company_logos/', blank=True)
    
    class Meta:
        verbose_name = _('Informações da Empresa')
        verbose_name_plural = _('Informações da Empresa')
        
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError(_('Já existe um registro de informações da empresa.'))
        return super().save(*args, **kwargs)

class FiscalYear(models.Model):
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
        
    def __str__(self):
        return f'Ano Fiscal {self.year}'
