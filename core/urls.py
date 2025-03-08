from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/done/', views.RegistrationDoneView.as_view(), name='registration_done'),
    path('activate/<uuid:token>/', views.activate_account, name='activate_account'),
    
    # URLs para empresas
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/add/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
    path('set-current-company/', views.set_current_company, name='set_current_company'),
    
    # URLs para anos fiscais
    path('fiscal-year/', views.FiscalYearListView.as_view(), name='fiscal_year_list'),
    path('fiscal-year/create/', views.FiscalYearCreateView.as_view(), name='fiscal_year_create'),
    path('fiscal-year/<int:pk>/', views.FiscalYearDetailView.as_view(), name='fiscal_year_detail'),
    path('fiscal-year/<int:pk>/edit/', views.FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
    path('fiscal-year/<int:pk>/close/', views.FiscalYearCloseView.as_view(), name='fiscal_year_close'),
]
