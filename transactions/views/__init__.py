"""
Este módulo contém todas as views relacionadas a transações.
As views foram organizadas em módulos separados para melhor manutenção e organização.
"""

# Importar todas as views dos submódulos para manter compatibilidade com código existente
from .transaction_views import (
    TransactionListView, TransactionDetailView, TransactionCreateView,
    TransactionUpdateView, TransactionDeleteView, TransactionImportView,
    TransactionExportView, JournalView
)

from .template_views import (
    TransactionTemplateListView, TransactionTemplateDetailView,
    TransactionTemplateCreateView, TransactionTemplateUpdateView,
    TransactionTemplateDeleteView, TransactionTemplateEditView,
    TransactionTemplateItemUpdateView, TransactionTemplateItemDeleteView,
    transaction_template_item_create
)

from .template_use_views import (
    TransactionFromTemplateView
)

from .api_views import (
    account_search
)
