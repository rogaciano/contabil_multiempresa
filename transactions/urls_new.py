from django.urls import path
from . import views
from . import transaction_templates

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('import/', views.TransactionImportView.as_view(), name='transaction_import'),
    path('export/', views.TransactionExportView.as_view(), name='transaction_export'),
    path('journal/', views.JournalView.as_view(), name='journal'),
    
    # URLs para modelos de lançamentos - usando o novo módulo transaction_templates
    path('templates/', transaction_templates.TransactionTemplateListView.as_view(), name='transaction_template_list'),
    path('templates/create/', transaction_templates.TransactionTemplateCreateView.as_view(), name='transaction_template_create'),
    path('templates/<int:pk>/', transaction_templates.TransactionTemplateDetailView.as_view(), name='transaction_template_detail'),
    path('templates/<int:pk>/edit/', transaction_templates.TransactionTemplateUpdateView.as_view(), name='transaction_template_update'),
    path('templates/<int:pk>/delete/', transaction_templates.TransactionTemplateDeleteView.as_view(), name='transaction_template_delete'),
    path('templates/<int:pk>/full-edit/', transaction_templates.TransactionTemplateEditView.as_view(), name='transaction_template_edit'),
    path('templates/<int:template_id>/items/add/', transaction_templates.transaction_template_item_create, name='transaction_template_item_create'),
    path('templates/items/<int:pk>/edit/', transaction_templates.TransactionTemplateItemUpdateView.as_view(), name='transaction_template_item_update'),
    path('templates/items/<int:pk>/delete/', transaction_templates.TransactionTemplateItemDeleteView.as_view(), name='transaction_template_item_delete'),
    path('templates/<int:template_id>/use/', transaction_templates.TransactionFromTemplateView.as_view(), name='transaction_from_template'),
    
    # API para busca de contas via AJAX
    path('api/accounts/search/', transaction_templates.account_search, name='account_search'),
]
