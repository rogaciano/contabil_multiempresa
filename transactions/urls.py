from django.urls import path
from . import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('import/', views.TransactionImportView.as_view(), name='transaction_import'),
    path('export/', views.TransactionExportView.as_view(), name='transaction_export'),
    path('journal/', views.JournalView.as_view(), name='journal'),
]
