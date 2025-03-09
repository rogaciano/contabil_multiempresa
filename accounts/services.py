import os
import json
import logging
import requests
from django.conf import settings
from dotenv import load_dotenv
from .models import Account, AccountType, Company

# Configurar logger
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class AnthropicService:
    """Serviço para interagir com a API da Anthropic (Claude)"""
    
    API_URL = "https://api.anthropic.com/v1/messages"
    
    @staticmethod
    def get_api_key():
        """Obtém a chave de API da Anthropic das variáveis de ambiente"""
        return os.getenv('ANTROPIC_API_KEY')
    
    @classmethod
    def generate_account_plan(cls, business_type, business_details, company_id):
        """
        Gera um plano de contas usando a API da Anthropic com base no tipo de negócio
        
        Args:
            business_type (str): Tipo de negócio (serviços, indústria, comércio)
            business_details (str): Detalhes adicionais sobre o negócio
            company_id (int): ID da empresa para a qual o plano será gerado
            
        Returns:
            dict: Plano de contas gerado ou mensagem de erro
        """
        api_key = cls.get_api_key()
        if not api_key:
            return {"error": "Chave de API da Anthropic não configurada"}
        
        # Construir o prompt para a API
        prompt = f"""
        Você é um especialista em contabilidade. Preciso que crie um plano de contas contábil completo para uma empresa com as seguintes características:
        
        Tipo de negócio: {business_type}
        Detalhes adicionais: {business_details}
        
        O plano de contas deve seguir a estrutura:
        1. Ativo (A)
        2. Passivo (L)
        3. Patrimônio Líquido (E)
        4. Receita (R)
        5. Despesa (X)
        
        Para cada conta, forneça:
        - Código (formato numérico com pontos, ex: 1.1.01)
        - Nome da conta
        - Tipo (um dos códigos acima: A, L, E, R, X)
        - Conta pai (código da conta pai, se houver)
        
        Forneça o resultado em formato JSON seguindo exatamente esta estrutura:
        {{
            "accounts": [
                {{
                    "code": "1",
                    "name": "Ativo",
                    "type": "A",
                    "parent": null
                }},
                {{
                    "code": "1.1",
                    "name": "Ativo Circulante",
                    "type": "A",
                    "parent": "1"
                }},
                ...
            ]
        }}
        
        Crie um plano de contas completo e adequado para o tipo de negócio especificado, com pelo menos 50 contas.
        Responda APENAS com o JSON, sem texto adicional antes ou depois.
        """
        
        # Preparar a requisição para a API da Anthropic
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(cls.API_URL, headers=headers, json=data)
            response.raise_for_status()
            
            # Processar a resposta
            result = response.json()
            
            # Verificar se a resposta contém a estrutura esperada
            if 'content' not in result or not result['content']:
                return {"error": "Resposta da API não contém conteúdo"}
                
            # Extrair o texto da resposta
            assistant_message = ""
            for content_block in result.get('content', []):
                if content_block.get('type') == 'text':
                    assistant_message += content_block.get('text', '')
            
            # Tentar encontrar o JSON na resposta
            # Primeiro, tentar encontrar o JSON completo
            import re
            json_pattern = r'({[\s\S]*})'
            json_matches = re.findall(json_pattern, assistant_message)
            
            if json_matches:
                # Tentar cada correspondência encontrada
                for json_str in json_matches:
                    try:
                        accounts_data = json.loads(json_str)
                        # Verificar se o JSON tem a estrutura esperada
                        if 'accounts' in accounts_data and isinstance(accounts_data['accounts'], list):
                            return accounts_data
                    except json.JSONDecodeError:
                        continue
            
            # Se não conseguir extrair o JSON completo, tentar extrair apenas a parte relevante
            json_start = assistant_message.find('{')
            json_end = assistant_message.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = assistant_message[json_start:json_end]
                try:
                    accounts_data = json.loads(json_str)
                    # Verificar se o JSON tem a estrutura esperada
                    if 'accounts' in accounts_data and isinstance(accounts_data['accounts'], list):
                        return accounts_data
                    else:
                        # Tentar ajustar o JSON se estiver faltando a chave "accounts"
                        if isinstance(accounts_data, list):
                            return {"accounts": accounts_data}
                        else:
                            return {"error": "O JSON não contém a estrutura esperada"}
                except json.JSONDecodeError as e:
                    return {"error": f"Erro ao processar o JSON: {str(e)}"}
            
            return {"error": "Não foi possível extrair o plano de contas da resposta"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Erro na comunicação com a API da Anthropic: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Erro ao processar a resposta da API: {str(e)}"}
        except Exception as e:
            return {"error": f"Erro inesperado: {str(e)}"}
    
    @staticmethod
    def create_accounts_from_plan(accounts_data, company_id):
        """
        Cria contas no banco de dados a partir do plano de contas gerado
        """
        logger.info(f"Iniciando criação de contas para a empresa {company_id}")
        logger.debug(f"Dados recebidos: {accounts_data}")
        
        if not accounts_data or 'accounts' not in accounts_data:
            logger.error("Dados de contas inválidos")
            return 0, ["Dados de contas inválidos"]
        
        accounts_created = 0
        errors = []
        
        try:
            company = Company.objects.get(id=company_id)
            logger.info(f"Empresa encontrada: {company.name}")
            
            # Mapear códigos de contas para objetos Account para referência de contas pai
            account_map = {}
            
            # Primeira passagem: criar todas as contas sem definir os pais
            for account_data in accounts_data['accounts']:
                try:
                    logger.debug(f"Processando conta: {account_data}")
                    
                    # Verificar se a conta já existe
                    existing_account = Account.objects.filter(
                        code=account_data['code'],
                        company=company
                    ).first()
                    
                    if existing_account:
                        # Atualizar conta existente
                        logger.debug(f"Atualizando conta existente: {existing_account.code}")
                        existing_account.name = account_data['name']
                        existing_account.type = account_data['type']
                        existing_account.save()
                        account_map[account_data['code']] = existing_account
                    else:
                        # Criar nova conta
                        logger.debug(f"Criando nova conta: {account_data['code']}")
                        new_account = Account(
                            code=account_data['code'],
                            name=account_data['name'],
                            type=account_data['type'],
                            company=company
                        )
                        new_account.save()
                        account_map[account_data['code']] = new_account
                        accounts_created += 1
                except Exception as e:
                    error_msg = f"Erro ao criar conta {account_data['code']}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Segunda passagem: definir os pais
            logger.info(f"Definindo relações de contas pai-filho")
            for account_data in accounts_data['accounts']:
                if 'parent' in account_data and account_data['parent']:
                    try:
                        child_account = account_map.get(account_data['code'])
                        parent_account = account_map.get(account_data['parent'])
                        
                        if child_account and parent_account:
                            logger.debug(f"Definindo pai para {child_account.code}: {parent_account.code}")
                            child_account.parent = parent_account
                            child_account.save()
                        else:
                            if not child_account:
                                logger.warning(f"Conta filha não encontrada: {account_data['code']}")
                            if not parent_account:
                                logger.warning(f"Conta pai não encontrada: {account_data['parent']}")
                    except Exception as e:
                        error_msg = f"Erro ao definir pai para conta {account_data['code']}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
            
            logger.info(f"Criação de contas concluída. Criadas: {accounts_created}, Erros: {len(errors)}")
            return accounts_created, errors
        except Company.DoesNotExist:
            logger.error(f"Empresa não encontrada: {company_id}")
            return 0, ["Empresa não encontrada"]
        except Exception as e:
            error_msg = f"Erro ao criar contas: {str(e)}"
            logger.error(error_msg)
            return 0, [error_msg]

class GeminiService:
    """Serviço para interagir com a API do Google Gemini"""
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
    
    @staticmethod
    def get_api_key():
        """Obtém a chave de API do Gemini das variáveis de ambiente"""
        return os.getenv('GEMINI_API_KEY')
    
    @classmethod
    def generate_account_plan(cls, business_type, business_details, company_id):
        """
        Gera um plano de contas usando a API do Gemini com base no tipo de negócio
        
        Args:
            business_type (str): Tipo de negócio (serviços, indústria, comércio)
            business_details (str): Detalhes adicionais sobre o negócio
            company_id (int): ID da empresa para a qual o plano será gerado
            
        Returns:
            dict: Plano de contas gerado ou mensagem de erro
        """
        api_key = cls.get_api_key()
        if not api_key:
            return {"error": "Chave de API do Gemini não configurada"}
        
        # Construir o prompt para a API
        prompt = f"""
        Você é um especialista em contabilidade. Preciso que crie um plano de contas contábil completo para uma empresa com as seguintes características:
        
        Tipo de negócio: {business_type}
        Detalhes adicionais: {business_details}
        
        O plano de contas deve seguir a estrutura:
        1. Ativo (A)
        2. Passivo (L)
        3. Patrimônio Líquido (E)
        4. Receita (R)
        5. Despesa (X)
        
        Para cada conta, forneça:
        - Código (formato numérico com pontos, ex: 1.1.01)
        - Nome da conta
        - Tipo (um dos códigos acima: A, L, E, R, X)
        - Conta pai (código da conta pai, se houver)
        
        Forneça o resultado em formato JSON seguindo exatamente esta estrutura:
        {{
            "accounts": [
                {{
                    "code": "1",
                    "name": "Ativo",
                    "type": "A",
                    "parent": null
                }},
                {{
                    "code": "1.1",
                    "name": "Ativo Circulante",
                    "type": "A",
                    "parent": "1"
                }},
                ...
            ]
        }}
        
        Crie um plano de contas completo e adequado para o tipo de negócio especificado, com pelo menos 50 contas.
        Responda APENAS com o JSON, sem texto adicional antes ou depois.
        """
        
        # Preparar a requisição para a API do Gemini
        url = f"{cls.API_URL}?key={api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4000
            }
        }
        
        try:
            logger.info(f"Iniciando chamada à API do Gemini com prompt de tamanho: {len(prompt)}")
            logger.info(f"URL da API: {url}")
            
            # Adicionar um timeout mais curto para teste
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            logger.info(f"Resposta recebida da API do Gemini com status: {response.status_code}")
            response.raise_for_status()
            
            # Processar a resposta
            logger.info("Processando resposta JSON")
            result = response.json()
            logger.info(f"Resposta processada com sucesso, tamanho do JSON: {len(str(result))}")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout ao chamar a API do Gemini: {str(e)}")
            return {"error": f"Timeout ao chamar a API do Gemini: {str(e)}"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão com a API do Gemini: {str(e)}")
            return {"error": f"Erro de conexão com a API do Gemini: {str(e)}"}
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao chamar a API do Gemini: {str(e)}")
            return {"error": f"Erro HTTP ao chamar a API do Gemini: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na comunicação com a API do Gemini: {str(e)}")
            return {"error": f"Erro na comunicação com a API do Gemini: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao processar a resposta da API: {str(e)}")
            return {"error": f"Erro ao processar a resposta da API: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return {"error": f"Erro inesperado: {str(e)}"}
        
        # Verificar se a resposta contém a estrutura esperada
        if 'candidates' not in result or not result['candidates']:
            return {"error": "Resposta da API não contém conteúdo"}
                
        # Extrair o texto da resposta
        assistant_message = ""
        for candidate in result.get('candidates', []):
            content = candidate.get('content', {})
            for part in content.get('parts', []):
                if 'text' in part:
                    assistant_message += part['text']
        
        # Tentar encontrar o JSON na resposta
        # Primeiro, tentar encontrar o JSON completo
        import re
        json_pattern = r'({[\s\S]*})'
        json_matches = re.findall(json_pattern, assistant_message)
        
        if json_matches:
            # Tentar cada correspondência encontrada
            for json_str in json_matches:
                try:
                    accounts_data = json.loads(json_str)
                    # Verificar se o JSON tem a estrutura esperada
                    if 'accounts' in accounts_data and isinstance(accounts_data['accounts'], list):
                        return accounts_data
                except json.JSONDecodeError:
                    continue
        
        # Se não conseguir extrair o JSON completo, tentar extrair apenas a parte relevante
        json_start = assistant_message.find('{')
        json_end = assistant_message.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = assistant_message[json_start:json_end]
            try:
                accounts_data = json.loads(json_str)
                # Verificar se o JSON tem a estrutura esperada
                if 'accounts' in accounts_data and isinstance(accounts_data['accounts'], list):
                    return accounts_data
                else:
                    # Tentar ajustar o JSON se estiver faltando a chave "accounts"
                    if isinstance(accounts_data, list):
                        return {"accounts": accounts_data}
                    else:
                        return {"error": "O JSON não contém a estrutura esperada"}
            except json.JSONDecodeError as e:
                return {"error": f"Erro ao processar o JSON: {str(e)}"}
        
        return {"error": "Não foi possível extrair o plano de contas da resposta"}
    
    @staticmethod
    def create_accounts_from_plan(accounts_data, company_id):
        """
        Cria contas no banco de dados a partir do plano de contas gerado
        """
        # Reutiliza o mesmo método do AnthropicService
        return AnthropicService.create_accounts_from_plan(accounts_data, company_id)

# Classe para selecionar qual serviço de IA usar
class AIService:
    """Serviço para selecionar qual API de IA usar (Anthropic ou Gemini)"""
    
    @staticmethod
    def get_service():
        """
        Determina qual serviço de IA usar com base na configuração
        Prioriza Gemini se a chave estiver configurada, senão usa Anthropic
        """
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            return GeminiService
        
        anthropic_key = os.getenv('ANTROPIC_API_KEY')
        if anthropic_key:
            return AnthropicService
            
        # Se nenhuma chave estiver configurada, retorna Anthropic como padrão
        return AnthropicService
    
    @classmethod
    def generate_account_plan(cls, business_type, business_details, company_id):
        """
        Gera um plano de contas usando o serviço de IA selecionado
        """
        service = cls.get_service()
        logger.info(f"Usando serviço de IA: {service.__name__}")
        return service.generate_account_plan(business_type, business_details, company_id)
    
    @classmethod
    def create_accounts_from_plan(cls, accounts_data, company_id):
        """
        Cria contas no banco de dados a partir do plano de contas gerado
        """
        service = cls.get_service()
        return service.create_accounts_from_plan(accounts_data, company_id)
