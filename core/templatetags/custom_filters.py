from django import template
from django.template.defaultfilters import floatformat
import locale

register = template.Library()

@register.filter
def currency(value):
    """
    Formata um valor monetário com separador de milhares e duas casas decimais.
    """
    try:
        value = float(value)
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """
    Subtrai o argumento do valor.
    """
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def absolute(value):
    """
    Retorna o valor absoluto.
    """
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value
