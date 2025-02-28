from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('company/', views.CompanyInfoView.as_view(), name='company_info'),
    path('company/edit/', views.CompanyInfoUpdateView.as_view(), name='company_info_edit'),
    path('fiscal-year/', views.FiscalYearListView.as_view(), name='fiscal_year_list'),
    path('fiscal-year/create/', views.FiscalYearCreateView.as_view(), name='fiscal_year_create'),
    path('fiscal-year/<int:pk>/', views.FiscalYearDetailView.as_view(), name='fiscal_year_detail'),
    path('fiscal-year/<int:pk>/edit/', views.FiscalYearUpdateView.as_view(), name='fiscal_year_edit'),
    path('fiscal-year/<int:pk>/close/', views.FiscalYearCloseView.as_view(), name='fiscal_year_close'),
]
