from django.contrib import admin
from .models import Transaction, TransactionTemplate, TransactionTemplateItem
from .forms import TransactionTemplateItemForm

# Register your models here.

class TransactionTemplateItemInline(admin.TabularInline):
    model = TransactionTemplateItem
    form = TransactionTemplateItemForm
    extra = 1

class TransactionTemplateAdmin(admin.ModelAdmin):
    inlines = [TransactionTemplateItemInline]
    list_display = ('name', 'company', 'entry_type', 'is_active')
    list_filter = ('company', 'entry_type', 'is_active')
    search_fields = ('name', 'description')

admin.site.register(Transaction)
admin.site.register(TransactionTemplate, TransactionTemplateAdmin)
admin.site.register(TransactionTemplateItem)
