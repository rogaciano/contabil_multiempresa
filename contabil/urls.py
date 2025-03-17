"""
URL configuration for contabil project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('reports/', include('reports.urls')),
    path('financial-reports/', include('financial_reports.urls')),
    path('select2/', include('django_select2.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
