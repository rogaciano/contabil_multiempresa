from django.urls import path
from . import views
from . import ai_views

urlpatterns = [
    path('', views.AccountListView.as_view(), name='account_list'),
    path('create/', views.AccountCreateView.as_view(), name='account_create'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_update'),
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('<int:pk>/create-child/', views.AccountCreateChildView.as_view(), name='account_create_child'),
    path('chart/', views.AccountChartView.as_view(), name='account_chart'),
    path('import/', views.AccountImportView.as_view(), name='account_import'),
    path('export/', views.AccountExportView.as_view(), name='account_export'),
    path('api/by-type/<str:type_code>/', views.AccountsByTypeView.as_view(), name='accounts_by_type'),
    path('template-download/', views.AccountTemplateDownloadView.as_view(), name='account_template_download'),
    
    # URLs para perfil do usuário e configurações
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='user_profile_edit'),
    path('settings/', views.UserSettingsView.as_view(), name='user_settings'),
    
    # URLs para geração de plano de contas com IA
    path('ai-generator/', ai_views.AIAccountPlanGeneratorView.as_view(), name='ai_account_plan_generator'),
    path('ai-result/', ai_views.AIAccountPlanResultView.as_view(), name='ai_account_plan_result'),
]
