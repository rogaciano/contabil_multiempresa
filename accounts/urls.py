from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountListView.as_view(), name='account_list'),
    path('create/', views.AccountCreateView.as_view(), name='account_create'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_update'),
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('chart/', views.AccountChartView.as_view(), name='account_chart'),
    path('import/', views.AccountImportView.as_view(), name='account_import'),
    path('export/', views.AccountExportView.as_view(), name='account_export'),
    path('api/by-type/<str:type_code>/', views.AccountsByTypeView.as_view(), name='accounts_by_type'),
]
