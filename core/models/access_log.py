from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    account_count = models.IntegerField(default=0)
    company_count = models.IntegerField(default=0)
    fiscal_year_count = models.IntegerField(default=0)
    transaction_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
