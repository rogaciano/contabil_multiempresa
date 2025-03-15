import json
from decimal import Decimal
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

@register.filter(name='to_json')
def to_json(value):
    """Converte um objeto Python para JSON"""
    return mark_safe(json.dumps(value, cls=DecimalEncoder))

@register.filter(name='template_items_json')
def template_items_json(items):
    """Converte uma lista de itens de template para JSON"""
    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'description': item.description or '',
            'debitAccount': f"{item.debit_account.code} - {item.debit_account.name}",
            'creditAccount': f"{item.credit_account.code} - {item.credit_account.name}",
            'value': float(item.value) if item.value is not None else None,
            'isPercentage': item.is_percentage,
            'order': item.order
        })
    return mark_safe(json.dumps(items_data, cls=DecimalEncoder))
