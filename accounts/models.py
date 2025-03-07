from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import models

class AccountType(models.TextChoices):
    ASSET = 'A', _('Ativo')
    LIABILITY = 'L', _('Passivo')
    EQUITY = 'E', _('Patrimônio Líquido')
    REVENUE = 'R', _('Receita')
    EXPENSE = 'X', _('Despesa')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    companies = models.ManyToManyField('Company', related_name='users')
    last_company_id = models.IntegerField(null=True, blank=True, help_text=_('ID da última empresa utilizada pelo usuário'))
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Perfil de Usuário')
        verbose_name_plural = _('Perfis de Usuários')


class Company(models.Model):
    name = models.CharField(_('Nome'), max_length=100)
    tax_id = models.CharField(_('CNPJ'), max_length=14, unique=True)
    address = models.TextField(_('Endereço'), blank=True)
    phone = models.CharField(_('Telefone'), max_length=20, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Empresa')
        verbose_name_plural = _('Empresas')


class Account(models.Model):
    company = models.ForeignKey(Company, verbose_name=_('Empresa'), on_delete=models.CASCADE, related_name='accounts')
    code = models.CharField(_('Código'), max_length=20)
    name = models.CharField(_('Nome'), max_length=100)
    type = models.CharField(_('Tipo'), max_length=1, choices=AccountType.choices)
    parent = models.ForeignKey('self', verbose_name=_('Conta Pai'), null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    description = models.TextField(_('Descrição'), blank=True)
    is_active = models.BooleanField(_('Ativo'), default=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Conta')
        verbose_name_plural = _('Contas')
        ordering = ['code']
        unique_together = ['company', 'code']  # Código deve ser único por empresa

    def __str__(self):
        return f'{self.code} - {self.name}'

    def clean(self):
        # Validar que o código da conta segue o padrão correto
        if not self.code.replace('.', '').isdigit():
            raise ValidationError({
                'code': _('O código da conta deve conter apenas números e pontos.')
            })

        # Validar que a conta pai é do mesmo tipo
        if self.parent and self.parent.type != self.type:
            raise ValidationError({
                'parent': _('A conta pai deve ser do mesmo tipo que a conta filha.')
            })

        # Validar que a conta não é pai dela mesma
        if self.pk and self.parent and self.parent.pk == self.pk:
            raise ValidationError({
                'parent': _('Uma conta não pode ser pai dela mesma.')
            })
        
        # Validar que a conta pai pertence à mesma empresa
        if self.parent and self.parent.company != self.company:
            raise ValidationError({
                'parent': _('A conta pai deve pertencer à mesma empresa.')
            })

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('account_detail', kwargs={'pk': self.pk})

    def get_balance(self, start_date=None, end_date=None):
        """
        Calcula o saldo da conta com base nas transações.
        Se a conta for pai, soma os saldos das contas filhas.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Comentado para reduzir logs no terminal
        # logger.debug(f"Calculando saldo para conta {self.code} - {self.name} (ID: {self.id}, Empresa: {self.company.name})")
        
        # Se a conta não é folha, soma os saldos das contas filhas
        if not self.is_leaf:
            children_balance = sum(child.get_balance(start_date=start_date, end_date=end_date) for child in self.children.filter(is_active=True))
            # Comentado para reduzir logs no terminal
            # logger.debug(f"Conta {self.code} (não-folha) - Saldo das filhas: {children_balance}")
            return children_balance
        
        # Para contas folha, calcula o saldo com base nas transações
        from django.db.models import Sum, Q
        from transactions.models import Transaction
        
        transactions = Transaction.objects.filter(company=self.company)
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        # Filtrar transações por conta
        debits = transactions.filter(debit_account=self).aggregate(Sum('amount'))['amount__sum'] or 0
        credits = transactions.filter(credit_account=self).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calcular saldo conforme o tipo de conta
        if self.type in [AccountType.ASSET, AccountType.EXPENSE]:  # ASSET, EXPENSE
            balance = debits - credits
        else:  # LIABILITY, EQUITY, REVENUE
            balance = credits - debits
            
        # Comentado para reduzir logs no terminal
        # logger.debug(f"Conta {self.code} - Débitos: {debits}, Créditos: {credits}, Saldo: {balance}")
        return balance

    @property
    def is_leaf(self):
        """Retorna True se a conta não tem filhos."""
        if not self.pk:  # Se a conta ainda não foi salva, consideramos como folha
            return True
        return not self.children.exists()

    @property
    def level(self):
        """Retorna o nível da conta na hierarquia."""
        if not self.parent:
            return 1
        
        # Se o pai não tem pk, pode ser uma conta temporária
        if not self.parent.pk:
            return 2  # Assumimos que é uma conta de segundo nível
            
        return self.parent.level + 1

    @property
    def type_display(self):
        """Retorna o nome do tipo de conta."""
        return self.get_type_display()
