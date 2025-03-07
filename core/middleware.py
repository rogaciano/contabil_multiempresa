from django.contrib.auth.models import AnonymousUser
from accounts.models import Company
import logging

logger = logging.getLogger(__name__)

class CurrentCompanyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Código executado para cada requisição antes da view
        if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            # Verifica se o usuário tem um perfil
            try:
                profile = request.user.profile
                
                # Se o usuário está autenticado e não tem empresa atual na sessão
                if 'current_company_id' not in request.session:
                    logger.debug(f"Usuário {request.user.email} não tem empresa na sessão")
                    
                    # Verificar se o usuário tem empresas
                    companies = profile.companies.all()
                    if companies.exists():
                        # Selecionar a primeira empresa
                        first_company = companies.first()
                        request.session['current_company_id'] = first_company.id
                        request.current_company = first_company
                        
                        # Atualizar a última empresa utilizada
                        profile.last_company_id = first_company.id
                        profile.save(update_fields=['last_company_id'])
                        
                        logger.debug(f"Selecionada primeira empresa: {first_company.name}")
                    else:
                        request.current_company = None
                        logger.debug("Usuário não tem empresas cadastradas")
                else:
                    # Se já tem empresa na sessão, carrega ela
                    try:
                        company_id = request.session['current_company_id']
                        company = Company.objects.get(id=company_id)
                        
                        # Verificar se o usuário tem acesso a esta empresa
                        if profile.companies.filter(id=company_id).exists():
                            request.current_company = company
                            
                            # Atualizar a última empresa utilizada
                            if profile.last_company_id != company_id:
                                profile.last_company_id = company_id
                                profile.save(update_fields=['last_company_id'])
                                
                            logger.debug(f"Carregada empresa da sessão: {company.name}")
                        else:
                            # Se o usuário não tem acesso a esta empresa, remove da sessão
                            del request.session['current_company_id']
                            
                            # Tenta selecionar outra empresa
                            other_company = profile.companies.first()
                            if other_company:
                                request.session['current_company_id'] = other_company.id
                                request.current_company = other_company
                                
                                # Atualizar a última empresa utilizada
                                profile.last_company_id = other_company.id
                                profile.save(update_fields=['last_company_id'])
                                
                                logger.debug(f"Selecionada outra empresa: {other_company.name}")
                            else:
                                request.current_company = None
                                logger.debug("Usuário não tem empresas")
                    except Company.DoesNotExist:
                        # Se a empresa não existir, remove da sessão
                        if 'current_company_id' in request.session:
                            del request.session['current_company_id']
                        
                        # Tenta selecionar outra empresa
                        other_company = profile.companies.first()
                        if other_company:
                            request.session['current_company_id'] = other_company.id
                            request.current_company = other_company
                            
                            # Atualizar a última empresa utilizada
                            profile.last_company_id = other_company.id
                            profile.save(update_fields=['last_company_id'])
                            
                            logger.debug(f"Selecionada outra empresa após erro: {other_company.name}")
                        else:
                            request.current_company = None
                            logger.debug("Usuário não tem empresas após erro")
            except Exception as e:
                request.current_company = None
                logger.error(f"Erro ao carregar empresa: {str(e)}")
        else:
            request.current_company = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.debug(f"Usuário autenticado mas sem perfil: {request.user.username}")
            else:
                logger.debug("Usuário não autenticado")

        response = self.get_response(request)
        
        # Código executado para cada requisição após a view
        return response
