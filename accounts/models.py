from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class AccountType(models.TextChoices):
    ASSET = 'A', _('Ativo')
    LIABILITY = 'L', _('Passivo')
    EQUITY = 'E', _('Patrimônio Líquido')
    REVENUE = 'R', _('Receita')
    EXPENSE = 'X', _('Despesa')

class Account(models.Model):
    code = models.CharField(_('Código'), max_length=20, unique=True)
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('account_detail', kwargs={'pk': self.pk})

    def get_balance(self, start_date=None, end_date=None):
        """
        Calcula o saldo da conta com base nas transações.
        Retorna um valor positivo ou negativo dependendo do tipo de conta.
        """
        from django.db.models import Sum, Q
        from transactions.models import Transaction

        # Filtrar transações por data se especificado
        transactions = Transaction.objects.all()
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        # Calcular débitos e créditos
        debits = transactions.filter(debit_account=self).aggregate(total=Sum('amount'))['total'] or 0
        credits = transactions.filter(credit_account=self).aggregate(total=Sum('amount'))['total'] or 0

        # Calcular saldo com base no tipo de conta
        if self.type in [AccountType.ASSET, AccountType.EXPENSE]:
            return debits - credits
        else:  # LIABILITY, EQUITY, REVENUE
            return credits - debits

    @property
    def is_leaf(self):
        """Retorna True se a conta não tem filhos."""
        return not self.children.exists()

    @property
    def level(self):
        """Retorna o nível da conta na hierarquia."""
        if not self.parent:
            return 1
        return self.parent.level + 1

    @property
    def type_display(self):
        """Retorna o nome do tipo de conta."""
        return self.get_type_display()
