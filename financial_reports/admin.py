from django.contrib import admin
from .models import DRETemplate, DRESection, DREAccount, DREReport, DREReportItem

class DRESectionInline(admin.TabularInline):
    model = DRESection
    extra = 0
    fields = ('name', 'order', 'is_subtotal', 'parent', 'formula')
    ordering = ('order',)

class DREAccountInline(admin.TabularInline):
    model = DREAccount
    extra = 0
    fields = ('section', 'account_type', 'multiplier')

class DREReportItemInline(admin.TabularInline):
    model = DREReportItem
    extra = 0
    fields = ('name', 'value', 'order', 'is_subtotal', 'section_id')
    readonly_fields = ('name', 'value', 'order', 'is_subtotal', 'section_id')
    ordering = ('order',)
    can_delete = False
    max_num = 0  # Não permite adicionar novos itens

@admin.register(DRETemplate)
class DRETemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_regime', 'is_active')
    list_filter = ('tax_regime', 'is_active')
    search_fields = ('name', 'description')
    inlines = [DRESectionInline]

@admin.register(DRESection)
class DRESectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'order', 'is_subtotal', 'parent')
    list_filter = ('template', 'is_subtotal')
    search_fields = ('name', 'description')
    inlines = [DREAccountInline]

@admin.register(DREReport)
class DREReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'template', 'start_date', 'end_date', 'created_at', 'created_by')
    list_filter = ('company', 'template', 'start_date', 'end_date')
    search_fields = ('title', 'notes')
    readonly_fields = ('company', 'template', 'created_at', 'created_by')
    date_hierarchy = 'created_at'
    inlines = [DREReportItemInline]

# Não registramos DREReportItem e DREAccount diretamente, pois são gerenciados através de seus modelos relacionados
