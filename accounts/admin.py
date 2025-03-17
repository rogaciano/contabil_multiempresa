from django.contrib import admin
from .models import Company, UserProfile, Account

# Register your models here.

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'get_tax_regime_display', 'phone', 'email')
    list_filter = ('tax_regime',)
    search_fields = ('name', 'tax_id', 'email')
    
    def get_tax_regime_display(self, obj):
        return obj.get_tax_regime_display()
    
    get_tax_regime_display.short_description = 'Regime Tributário'

admin.site.register(Company, CompanyAdmin)
admin.site.register(UserProfile)
admin.site.register(Account)
