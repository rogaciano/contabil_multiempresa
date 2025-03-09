from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _

from .ai_forms import AIAccountPlanForm
from .services import AIService
from .models import Account

class AIAccountPlanGeneratorView(LoginRequiredMixin, FormView):
    """View para gerar plano de contas usando IA"""
    template_name = 'accounts/ai_account_plan_form.html'
    form_class = AIAccountPlanForm
    success_url = reverse_lazy('ai_account_plan_result')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Geração de Plano de Contas com IA')
        context['subtitle'] = _('Forneça informações sobre o negócio para gerar um plano de contas personalizado')
        return context
    
    def form_valid(self, form):
        # Obter a empresa atual do usuário
        current_company_id = self.request.session.get('current_company_id')
        if not current_company_id:
            messages.error(self.request, _('Selecione uma empresa antes de gerar um plano de contas.'))
            return redirect('company_list')
        
        # Preparar os dados para a API da AIService
        business_type = form.cleaned_data['business_type']
        business_subtype = form.cleaned_data['business_subtype']
        business_size = form.cleaned_data['business_size']
        tax_regime = form.cleaned_data['tax_regime']
        additional_details = form.cleaned_data['additional_details']
        
        # Construir descrição detalhada do negócio
        business_details = f"""
        Subtipo/Segmento: {business_subtype}
        Porte da Empresa: {dict(form.fields['business_size'].choices)[business_size]}
        Regime Tributário: {dict(form.fields['tax_regime'].choices)[tax_regime]}
        Detalhes Adicionais: {additional_details}
        """
        
        # Armazenar os dados na sessão para uso na view de resultado
        self.request.session['ai_account_plan_data'] = {
            'business_type': business_type,
            'business_details': business_details,
            'company_id': current_company_id
        }
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, _('Por favor, corrija os erros no formulário.'))
        return super().form_invalid(form)


class AIAccountPlanResultView(LoginRequiredMixin, TemplateView):
    """View para exibir e processar o resultado da geração do plano de contas"""
    template_name = 'accounts/ai_account_plan_result.html'
    
    def get(self, request, *args, **kwargs):
        # Verificar se existem dados na sessão
        if 'ai_account_plan_data' not in request.session:
            messages.error(request, _('Nenhum dado encontrado para geração do plano de contas.'))
            return redirect('ai_account_plan_generator')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter dados da sessão
        ai_data = self.request.session.get('ai_account_plan_data', {})
        business_type = ai_data.get('business_type')
        business_details = ai_data.get('business_details')
        company_id = ai_data.get('company_id')
        
        # Verificar se a empresa atual ainda é válida
        if not company_id or company_id != self.request.session.get('current_company_id'):
            messages.error(self.request, _('A empresa selecionada mudou. Por favor, tente novamente.'))
            context['error'] = True
            return context
        
        # Gerar o plano de contas usando a API da AIService
        accounts_data = AIService.generate_account_plan(
            business_type=business_type,
            business_details=business_details,
            company_id=company_id
        )
        
        # Verificar se houve erro na geração
        if "error" in accounts_data:
            messages.error(self.request, _('Erro ao gerar plano de contas: {}').format(accounts_data["error"]))
            context['error'] = True
            return context
        
        # Preparar o contexto com os dados das contas
        context['accounts'] = accounts_data.get('accounts', [])
        context['business_type'] = business_type
        context['business_details'] = business_details
        context['company_id'] = company_id
        context['title'] = _('Plano de Contas Gerado')
        context['subtitle'] = _('Revise o plano de contas gerado antes de importá-lo')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Processar a importação do plano de contas"""
        # Verificar se existem dados na sessão
        if 'ai_account_plan_data' not in request.session:
            messages.error(request, _('Nenhum dado encontrado para importação do plano de contas.'))
            return redirect('ai_account_plan_generator')
        
        # Obter dados da sessão
        ai_data = request.session.get('ai_account_plan_data', {})
        business_type = ai_data.get('business_type')
        business_details = ai_data.get('business_details')
        company_id = ai_data.get('company_id')
        
        # Verificar se a empresa atual ainda é válida
        if not company_id or company_id != request.session.get('current_company_id'):
            messages.error(request, _('A empresa selecionada mudou. Por favor, tente novamente.'))
            return redirect('ai_account_plan_generator')
        
        # Verificar se o usuário deseja limpar as contas existentes
        clear_existing = request.POST.get('clear_existing') == 'on'
        
        # Se o usuário optou por limpar as contas existentes, excluir todas as contas da empresa
        if clear_existing:
            try:
                # Excluir apenas contas que não têm transações associadas
                accounts_to_delete = Account.objects.filter(
                    company_id=company_id,
                    debit_transactions__isnull=True,
                    credit_transactions__isnull=True
                )
                deleted_count = accounts_to_delete.count()
                accounts_to_delete.delete()
                messages.success(request, _('Foram excluídas {} contas existentes.').format(deleted_count))
            except Exception as e:
                messages.error(request, _('Erro ao excluir contas existentes: {}').format(str(e)))
                return redirect('ai_account_plan_result')
        
        # Gerar o plano de contas novamente
        accounts_data = AIService.generate_account_plan(
            business_type=business_type,
            business_details=business_details,
            company_id=company_id
        )
        
        # Verificar se houve erro na geração
        if "error" in accounts_data:
            messages.error(request, _('Erro ao gerar plano de contas: {}').format(accounts_data["error"]))
            return redirect('ai_account_plan_generator')
        
        # Criar as contas no banco de dados
        try:
            accounts_created, errors = AIService.create_accounts_from_plan(accounts_data, company_id)
            
            # Exibir mensagens de sucesso ou erro
            if accounts_created > 0:
                messages.success(request, _('Foram criadas {} contas com sucesso!').format(accounts_created))
            else:
                messages.warning(request, _('Nenhuma conta nova foi criada.'))
            
            if errors:
                for error in errors:
                    messages.warning(request, error)
        except Exception as e:
            messages.error(request, _('Erro ao criar contas: {}').format(str(e)))
        
        # Limpar os dados da sessão
        if 'ai_account_plan_data' in request.session:
            del request.session['ai_account_plan_data']
        
        # Redirecionar para a lista de contas
        return redirect('account_list')
