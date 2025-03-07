from datetime import date
from .models import FiscalYear

def active_fiscal_year(request):
    """
    Adiciona informações do ano fiscal ativo ao contexto de todos os templates.
    """
    context = {
        'active_fiscal_year': None
    }
    
    # Verificar se o usuário está autenticado e tem uma empresa atual
    if hasattr(request, 'current_company') and request.current_company:
        # Buscar o ano fiscal ativo para a data atual
        today = date.today()
        fiscal_year = FiscalYear.objects.filter(
            company=request.current_company,
            start_date__lte=today,
            end_date__gte=today,
            is_closed=False
        ).first()
        
        context['active_fiscal_year'] = fiscal_year
    
    return context
