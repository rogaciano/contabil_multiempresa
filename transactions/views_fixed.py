"""
Este arquivo serve como um ponto de entrada para todas as views do módulo de transações.
Todas as views foram reorganizadas em submódulos para melhor manutenção e organização.

Nota: Este arquivo mantém compatibilidade com o código existente, importando todas as views
dos submódulos e expondo-as no mesmo namespace.
"""

# Importar todas as views dos submódulos
from .views.transaction_views import (
    TransactionListView, TransactionDetailView, TransactionCreateView,
    TransactionUpdateView, TransactionDeleteView, TransactionImportView,
    TransactionExportView, JournalView
)

from .views.template_views import (
    TransactionTemplateListView, TransactionTemplateDetailView,
    TransactionTemplateCreateView, TransactionTemplateUpdateView,
    TransactionTemplateDeleteView, TransactionTemplateEditView,
    TransactionTemplateItemUpdateView, TransactionTemplateItemDeleteView,
    transaction_template_item_create
)

from .views.template_use_views import (
    TransactionFromTemplateView
)

from .views.api_views import (
    account_search
)

# Manter todas as views disponíveis no namespace transactions.views
__all__ = [
    'TransactionListView', 'TransactionDetailView', 'TransactionCreateView',
    'TransactionUpdateView', 'TransactionDeleteView', 'TransactionImportView',
    'TransactionExportView', 'JournalView',
    'TransactionTemplateListView', 'TransactionTemplateDetailView',
    'TransactionTemplateCreateView', 'TransactionTemplateUpdateView',
    'TransactionTemplateDeleteView', 'TransactionTemplateEditView',
    'TransactionTemplateItemUpdateView', 'TransactionTemplateItemDeleteView',
    'transaction_template_item_create',
    'TransactionFromTemplateView',
    'account_search'
]
