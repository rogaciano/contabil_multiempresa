"""
Views relacionadas a APIs e endpoints AJAX para o módulo de transações.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from accounts.models import Account


@login_required
def account_search(request):
    """
    View para buscar contas via AJAX para o Select2
    
    Esta view é usada pelos componentes Select2 para buscar contas
    com base em um termo de pesquisa e filtrar pelo company_id.
    """
    # Obter parâmetros da requisição
    term = request.GET.get('term', '')
    company_id = request.GET.get('company_id')
    
    # Validar company_id
    if not company_id:
        company_id = request.user.company_id
    
    # Inicializar queryset
    queryset = Account.objects.filter(company_id=company_id, is_active=True)
    
    # Filtrar pelo termo de busca
    if term:
        queryset = queryset.filter(
            Q(code__icontains=term) | 
            Q(name__icontains=term)
        )
    
    # Limitar resultados
    queryset = queryset[:20]
    
    # Formatar resultados para o Select2
    results = []
    for account in queryset:
        results.append({
            'id': account.id,
            'text': f"{account.code} - {account.name}"
        })
    
    # Retornar resposta JSON
    return JsonResponse({
        'results': results,
        'pagination': {
            'more': False
        }
    })
