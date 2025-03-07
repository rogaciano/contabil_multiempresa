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
    if request.user.is_authenticated and hasattr(request, 'current_company') and request.current_company:
        try:
            # Buscar o ano fiscal ativo para a data atual
            today = date.today()
            fiscal_year = FiscalYear.objects.filter(
                company=request.current_company,
                start_date__lte=today,
                end_date__gte=today,
                is_closed=False
            ).first()
            
            # Se não encontrar um ano fiscal ativo para a data atual,
            # buscar o ano fiscal mais recente não fechado
            if not fiscal_year:
                fiscal_year = FiscalYear.objects.filter(
                    company=request.current_company,
                    is_closed=False
                ).order_by('-year').first()
            
            context['active_fiscal_year'] = fiscal_year
        except Exception:
            # Em caso de erro, não quebrar a aplicação
            pass
    
    return context