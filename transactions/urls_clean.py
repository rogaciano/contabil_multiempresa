"""
Configuração de URLs para o aplicativo de transações.
Este arquivo utiliza as views refatoradas dos módulos views_clean.py e transaction_templates.py.
"""
from django.urls import path
from .views_clean import (
    TransactionListView, TransactionDetailView, TransactionCreateView,
    TransactionUpdateView, TransactionDeleteView, TransactionImportView,
    TransactionExportView, JournalView
)
from .transaction_templates import (
    TransactionTemplateListView, TransactionTemplateDetailView,
    TransactionTemplateCreateView, TransactionTemplateUpdateView,
    TransactionTemplateDeleteView, TransactionTemplateItemUpdateView,
    TransactionTemplateItemDeleteView, TransactionTemplateEditView,
    TransactionFromTemplateView, transaction_template_item_create,
    account_search
)

urlpatterns = [
    # URLs para transações básicas - usando o módulo views_clean
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('create/', TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    path('import/', TransactionImportView.as_view(), name='transaction_import'),
    path('export/', TransactionExportView.as_view(), name='transaction_export'),
    path('journal/', JournalView.as_view(), name='journal'),
    
    # URLs para modelos de lançamentos - usando o módulo transaction_templates
    path('templates/', TransactionTemplateListView.as_view(), name='transaction_template_list'),
    path('templates/create/', TransactionTemplateCreateView.as_view(), name='transaction_template_create'),
    path('templates/<int:pk>/', TransactionTemplateDetailView.as_view(), name='transaction_template_detail'),
    path('templates/<int:pk>/edit/', TransactionTemplateUpdateView.as_view(), name='transaction_template_update'),
    path('templates/<int:pk>/delete/', TransactionTemplateDeleteView.as_view(), name='transaction_template_delete'),
    path('templates/<int:pk>/full-edit/', TransactionTemplateEditView.as_view(), name='transaction_template_edit'),
    path('templates/<int:template_id>/items/add/', transaction_template_item_create, name='transaction_template_item_create'),
    path('templates/items/<int:pk>/edit/', TransactionTemplateItemUpdateView.as_view(), name='transaction_template_item_update'),
    path('templates/items/<int:pk>/delete/', TransactionTemplateItemDeleteView.as_view(), name='transaction_template_item_delete'),
    path('templates/<int:template_id>/use/', TransactionFromTemplateView.as_view(), name='transaction_from_template'),
    
    # API para busca de contas via AJAX
    path('api/accounts/search/', account_search, name='account_search'),
]
