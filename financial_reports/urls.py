from django.urls import path
from . import views

urlpatterns = [
    # URLs para Templates de DRE
    path('templates/', views.DRETemplateListView.as_view(), name='dre_template_list'),
    path('templates/create/', views.DRETemplateCreateView.as_view(), name='dre_template_create'),
    path('templates/<uuid:pk>/', views.DRETemplateDetailView.as_view(), name='dre_template_detail'),
    path('templates/<uuid:pk>/edit/', views.DRETemplateUpdateView.as_view(), name='dre_template_edit'),
    path('templates/<uuid:pk>/delete/', views.DRETemplateDeleteView.as_view(), name='dre_template_delete'),
    
    # URLs para Seções de DRE
    path('templates/<uuid:template_id>/sections/create/', views.DRESectionCreateView.as_view(), name='dre_section_create'),
    path('sections/<uuid:pk>/edit/', views.DRESectionUpdateView.as_view(), name='dre_section_edit'),
    path('sections/<uuid:pk>/delete/', views.DRESectionDeleteView.as_view(), name='dre_section_delete'),
    
    # URLs para Relatórios de DRE
    path('reports/', views.DREReportListView.as_view(), name='dre_report_list'),
    path('reports/create/', views.DREReportCreateView.as_view(), name='dre_report_create'),
    path('reports/<uuid:pk>/', views.DREReportDetailView.as_view(), name='dre_report_detail'),
    path('reports/<uuid:pk>/delete/', views.DREReportDeleteView.as_view(), name='dre_report_delete'),
]
