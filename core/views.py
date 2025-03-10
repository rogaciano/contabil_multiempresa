from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import login
from django.utils.translation import gettext as _
import logging
import datetime
from django.db import transaction

logger = logging.getLogger(__name__)

from accounts.models import Account, UserProfile, Company
from transactions.models import Transaction
from .models import FiscalYear, UserActivationToken
from .forms import FiscalYearForm, FiscalYearCloseForm, UserRegistrationForm

import uuid

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Código de depuração
        logger.debug("============ INÍCIO DEBUG DASHBOARD ============")
        logger.debug(f"Usuário: {request.user.username} (ID: {request.user.id})")
        logger.debug(f"Empresa atual no request: {getattr(request, 'current_company', None)}")
        logger.debug(f"Empresa atual na sessão: {request.session.get('current_company_id', None)}")
        
        # Verificar se o usuário tem alguma empresa cadastrada mas nenhuma selecionada
        if request.user.is_authenticated:
            try:
                user_profile = request.user.profile
                logger.debug(f"Perfil do usuário: {user_profile.id}")
                logger.debug(f"Última empresa do perfil: {user_profile.last_company_id}")
                
                # Verificar empresas do usuário
                companies = user_profile.companies.all()
                logger.debug(f"Empresas do usuário: {[f'{c.id}:{c.name}' for c in companies]}")
                
                # Se não tem empresa atual, tenta selecionar uma
                if not getattr(request, 'current_company', None):
                    logger.debug("Usuário não tem empresa atual no request")
                    
                    if companies.exists():
                        logger.debug("Usuário tem empresas cadastradas")
                        # O usuário tem empresas, mas nenhuma está selecionada
                        # Selecionar automaticamente a primeira empresa
                        first_company = companies.first()
                        logger.debug(f"Primeira empresa: {first_company.id}:{first_company.name}")
                        
                        # Forçar a seleção da empresa na sessão
                        request.session['current_company_id'] = first_company.id
                        # Forçar o salvamento da sessão
                        request.session.modified = True
                        logger.debug(f"Empresa {first_company.id} definida na sessão")
                        
                        # Atualizar a última empresa utilizada no perfil do usuário
                        user_profile.last_company_id = first_company.id
                        user_profile.save(update_fields=['last_company_id'])
                        logger.debug(f"Última empresa atualizada no perfil: {first_company.id}")
                        
                        # Redirecionar para o dashboard para recarregar com a empresa selecionada
                        messages.info(request, _(f'Empresa {first_company.name} selecionada automaticamente.'))
                        logger.debug("Redirecionando para o dashboard")
                        logger.debug("============ FIM DEBUG DASHBOARD ============")
                        return redirect('dashboard')
                    else:
                        logger.debug("Usuário não tem empresas cadastradas")
            except Exception as e:
                logger.error(f"Erro ao selecionar empresa automaticamente: {str(e)}")
                logger.debug(f"Exceção: {str(e)}")
        
        logger.debug("Continuando com o processamento normal")
        logger.debug("============ FIM DEBUG DASHBOARD ============")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Usar a empresa atual do usuário (definida pelo middleware)
        company = getattr(self.request, 'current_company', None)
        
        # Depuração adicional
        logger.debug("============ INÍCIO DEBUG GET_CONTEXT_DATA ============")
        logger.debug(f"Empresa atual no request: {company}")
        logger.debug(f"Empresa atual na sessão: {self.request.session.get('current_company_id', None)}")
        
        if not company:
            logger.debug("Nenhuma empresa atual encontrada")
            # Verificar se o usuário tem alguma empresa cadastrada
            try:
                user_profile = self.request.user.profile
                companies = user_profile.companies.all()
                logger.debug(f"Empresas do usuário: {[f'{c.id}:{c.name}' for c in companies]}")
                
                if companies.exists():
                    # O usuário tem empresas, mas nenhuma está selecionada
                    logger.debug("Usuário tem empresas, mas nenhuma está selecionada")
                    context['has_companies'] = True
                    context['companies'] = companies
                    messages.info(self.request, _('Selecione uma empresa para continuar.'))
                else:
                    # O usuário não tem nenhuma empresa cadastrada
                    logger.debug("Usuário não tem empresas cadastradas")
                    context['has_companies'] = False
                    messages.info(self.request, _('Para começar a usar o sistema, cadastre sua primeira empresa.'))
            except UserProfile.DoesNotExist:
                logger.debug("Perfil do usuário não existe")
                # Criar perfil de usuário se não existir
                UserProfile.objects.create(user=self.request.user)
                context['has_companies'] = False
                messages.info(self.request, _('Para começar a usar o sistema, cadastre sua primeira empresa.'))
            
            logger.debug("============ FIM DEBUG GET_CONTEXT_DATA ============")
            return context
        
        logger.debug(f"Empresa atual encontrada: {company.id}:{company.name}")
        logger.debug("============ FIM DEBUG GET_CONTEXT_DATA ============")
        
        # Adicionar a empresa atual ao contexto com o nome correto para o template
        context['current_company'] = company
        
        # Obter o ano fiscal atual
        fiscal_year = FiscalYear.objects.filter(
            company=company,
            start_date__lte=datetime.date.today(),
            end_date__gte=datetime.date.today()
        ).first()
        
        if not fiscal_year:
            fiscal_year = FiscalYear.objects.filter(company=company).order_by('-end_date').first()
        
        if fiscal_year:
            # Estatísticas gerais - usar filter explícito para garantir que a consulta está correta
            total_accounts = Account.objects.filter(company=company.id).count()
            total_transactions = Transaction.objects.filter(company=company.id).count()
            
            # Adicionar logs de depuração para verificar as contagens
            logger.debug(f"Total de contas para a empresa {company.id}: {total_accounts}")
            logger.debug(f"Total de transações para a empresa {company.id}: {total_transactions}")
            
            # Verificar se há contas e transações
            accounts_exist = Account.objects.filter(company=company.id).exists()
            transactions_exist = Transaction.objects.filter(company=company.id).exists()
            logger.debug(f"Existem contas? {accounts_exist}")
            logger.debug(f"Existem transações? {transactions_exist}")
            
            # Listar algumas contas e transações para depuração
            sample_accounts = Account.objects.filter(company=company.id)[:5]
            sample_transactions = Transaction.objects.filter(company=company.id)[:5]
            logger.debug(f"Amostra de contas: {[f'{a.id}:{a.name}' for a in sample_accounts]}")
            logger.debug(f"Amostra de transações: {[f'{t.id}:{t.description}' for t in sample_transactions]}")
            
            # Transações recentes
            recent_transactions = Transaction.objects.filter(
                company=company.id,
                date__range=(fiscal_year.start_date, fiscal_year.end_date)
            ).order_by('-date', '-id')[:10]
            
            # Calcular estatísticas para o ano fiscal atual
            # Total de transações no ano fiscal
            fiscal_year_transactions_count = Transaction.objects.filter(
                company=company.id,
                date__range=(fiscal_year.start_date, fiscal_year.end_date)
            ).count()
            
            # Identificar contas de receita e despesa
            revenue_accounts = Account.objects.filter(
                company=company.id, 
                type='R'  # Receitas
            ).values_list('id', flat=True)
            
            expense_accounts = Account.objects.filter(
                company=company.id, 
                type='X'  # Despesas
            ).values_list('id', flat=True)
            
            # Calcular total de receitas (créditos em contas de receita)
            total_revenue = Transaction.objects.filter(
                company=company.id,
                date__range=(fiscal_year.start_date, fiscal_year.end_date),
                credit_account_id__in=revenue_accounts
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calcular total de despesas (débitos em contas de despesa)
            total_expenses = Transaction.objects.filter(
                company=company.id,
                date__range=(fiscal_year.start_date, fiscal_year.end_date),
                debit_account_id__in=expense_accounts
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Adicionar ao contexto
            context.update({
                'current_company': company,  # Garantir que o nome da variável seja consistente
                'fiscal_year': fiscal_year,
                'total_accounts': total_accounts,
                'total_transactions': total_transactions,
                'recent_transactions': recent_transactions,
                'fiscal_year_transactions_count': fiscal_year_transactions_count,
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'total_companies': Company.objects.count(),  # Total de empresas no sistema
                'total_fiscal_years': FiscalYear.objects.filter(company=company).count(),  # Total de anos fiscais da empresa atual
            })
            
            # Calcular índices financeiros para o dashboard
            # Obter contas para cálculo dos índices
            contas_ativo_circulante = Account.objects.filter(
                company=company.id, 
                type='A',  # Ativo
                code__startswith='1.1'  # Códigos que começam com 1.1 são ativos circulantes
            )
            
            contas_ativo = Account.objects.filter(
                company=company.id, 
                type='A'  # Ativo
            )
            
            contas_passivo_circulante = Account.objects.filter(
                company=company.id, 
                type='L',  # Passivo
                code__startswith='2.1'  # Códigos que começam com 2.1 são passivos circulantes
            )
            
            contas_passivo = Account.objects.filter(
                company=company.id, 
                type='L'  # Passivo
            )
            
            contas_patrimonio_liquido = Account.objects.filter(
                company=company.id, 
                type='E'  # Patrimônio Líquido
            )
            
            contas_estoque = Account.objects.filter(
                company=company.id, 
                type='A',  # Ativo
                code__startswith='1.1',  # Ativo Circulante
                name__icontains='estoque'  # Contas de estoque
            )
            
            # Calcular saldos
            ativo_circulante = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_ativo_circulante)
            ativo_total = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_ativo)
            passivo_circulante = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_passivo_circulante)
            passivo_total = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_passivo)
            patrimonio_liquido = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_patrimonio_liquido)
            estoques = sum(conta.get_balance(start_date=fiscal_year.start_date, end_date=fiscal_year.end_date) for conta in contas_estoque)
            
            # Cálculo dos índices financeiros
            # Índices de Liquidez
            liquidez_corrente = round(ativo_circulante / passivo_circulante, 2) if passivo_circulante > 0 else None
            liquidez_seca = round((ativo_circulante - estoques) / passivo_circulante, 2) if passivo_circulante > 0 else None
            
            # Índices de Endividamento
            grau_endividamento = round(passivo_total / patrimonio_liquido * 100, 2) if patrimonio_liquido > 0 else None
            composicao_endividamento = round(passivo_circulante / passivo_total * 100, 2) if passivo_total > 0 else None
            
            # Índices de Rentabilidade
            margem_liquida = round((total_revenue - total_expenses) / total_revenue * 100, 2) if total_revenue > 0 else None
            retorno_pl = round((total_revenue - total_expenses) / patrimonio_liquido * 100, 2) if patrimonio_liquido > 0 else None
            
            # Adicionar índices ao contexto
            context.update({
                'indices_financeiros': {
                    'liquidez_corrente': liquidez_corrente,
                    'liquidez_seca': liquidez_seca,
                    'grau_endividamento': grau_endividamento,
                    'composicao_endividamento': composicao_endividamento,
                    'margem_liquida': margem_liquida,
                    'retorno_pl': retorno_pl
                }
            })
        else:
            messages.info(self.request, _('Por favor, crie um ano fiscal para começar.'))
        
        return context

# Views para gerenciamento de empresas
class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'core/company_list.html'
    context_object_name = 'companies'
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return user_profile.companies.all()
        except UserProfile.DoesNotExist:
            return Company.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_company'] = getattr(self.request, 'current_company', None)
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'core/company_detail.html'
    context_object_name = 'company'
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return user_profile.companies.all()
        except UserProfile.DoesNotExist:
            return Company.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        # Obter anos fiscais da empresa
        fiscal_years = FiscalYear.objects.filter(company=company).order_by('-start_date')
        
        # Obter estatísticas da empresa
        total_accounts = Account.objects.filter(company=company).count()
        total_transactions = Transaction.objects.filter(company=company).count()
        
        context.update({
            'fiscal_years': fiscal_years,
            'total_accounts': total_accounts,
            'total_transactions': total_transactions,
            'is_current': company.id == getattr(getattr(self.request, 'current_company', None), 'id', None)
        })
        
        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'core/company_form.html'
    fields = ['name', 'tax_id', 'address', 'phone', 'email']
    success_url = reverse_lazy('company_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Adicionar a empresa ao perfil do usuário
        try:
            user_profile = self.request.user.profile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=self.request.user)
        
        user_profile.companies.add(self.object)
        
        # Definir como empresa atual
        self.request.session['current_company_id'] = self.object.id
        
        messages.success(self.request, _('Empresa criada com sucesso!'))
        return response


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = 'core/company_form.html'
    fields = ['name', 'tax_id', 'address', 'phone', 'email']
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return user_profile.companies.all()
        except UserProfile.DoesNotExist:
            return Company.objects.none()
    
    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Empresa atualizada com sucesso!'))
        return response


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'core/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return user_profile.companies.all()
        except UserProfile.DoesNotExist:
            return Company.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        # Contar os registros relacionados para mostrar ao usuário
        context['transactions_count'] = Transaction.objects.filter(company=company).count()
        context['accounts_count'] = Account.objects.filter(company=company).count()
        
        return context
    
    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        company_name = company.name
        
        # Se a empresa a ser excluída for a atual na sessão, limpar a sessão
        if request.session.get('current_company_id') == company.id:
            request.session['current_company_id'] = None
            request.session.modified = True
        
        # Verificar se o usuário tem outras empresas e atualizar o perfil
        user_profile = request.user.profile
        if user_profile.last_company_id == company.id:
            # Encontrar outra empresa para definir como última
            other_company = user_profile.companies.exclude(id=company.id).first()
            if other_company:
                user_profile.last_company_id = other_company.id
            else:
                user_profile.last_company_id = None
            user_profile.save(update_fields=['last_company_id'])
        
        # Excluir a empresa (as relações serão excluídas em cascata devido ao on_delete=models.CASCADE)
        response = super().delete(request, *args, **kwargs)
        
        messages.success(request, _(f'Empresa "{company_name}" e todos os seus dados foram excluídos com sucesso!'))
        return response

# Views para gerenciamento de anos fiscais
class FiscalYearListView(LoginRequiredMixin, ListView):
    model = FiscalYear
    template_name = 'core/fiscal_year_list.html'
    context_object_name = 'fiscal_years'
    
    def get_queryset(self):
        company = getattr(self.request, 'current_company', None)
        if company:
            return FiscalYear.objects.filter(company=company).order_by('-start_date')
        return FiscalYear.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = getattr(self.request, 'current_company', None)
        context['company'] = company
        
        # Adicionar estatísticas financeiras para cada ano fiscal
        fiscal_years_with_stats = []
        for fiscal_year in context['fiscal_years']:
            # Identificar contas de receita e despesa
            revenue_accounts = Account.objects.filter(
                company=company, 
                type='R'  # Receitas
            ).values_list('id', flat=True)
            
            expense_accounts = Account.objects.filter(
                company=company, 
                type='X'  # Despesas
            ).values_list('id', flat=True)
            
            # Calcular total de receitas (créditos em contas de receita)
            total_revenue = Transaction.objects.filter(
                company=company,
                date__range=(fiscal_year.start_date, fiscal_year.end_date),
                credit_account_id__in=revenue_accounts
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calcular total de despesas (débitos em contas de despesa)
            total_expenses = Transaction.objects.filter(
                company=company,
                date__range=(fiscal_year.start_date, fiscal_year.end_date),
                debit_account_id__in=expense_accounts
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calcular o resultado (receitas - despesas)
            result = total_revenue - total_expenses
            
            fiscal_years_with_stats.append({
                'fiscal_year': fiscal_year,
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'result': result
            })
        
        context['fiscal_years_with_stats'] = fiscal_years_with_stats
        return context


class FiscalYearCreateView(LoginRequiredMixin, CreateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'core/fiscal_year_form.html'
    
    def get_success_url(self):
        # Verificar se existe um parâmetro 'next' na URL
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('fiscal_year_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = getattr(self.request, 'current_company', None)
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        current_year = datetime.date.today().year
        # Não preenchemos o ano automaticamente, apenas as datas
        # initial['year'] = current_year
        initial['start_date'] = datetime.date(current_year, 1, 1)
        initial['end_date'] = datetime.date(current_year, 12, 31)
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar o parâmetro 'next' ao contexto para uso no template
        context['next_url'] = self.request.GET.get('next', '')
        # Adicionar informação de redirecionamento automático
        context['from_transaction'] = 'next' in self.request.GET
        return context
    
    def form_valid(self, form):
        form.instance.company = getattr(self.request, 'current_company', None)
        if not form.instance.company:
            messages.error(self.request, _('Você precisa selecionar uma empresa primeiro.'))
            return self.form_invalid(form)
        
        messages.success(self.request, _('Ano fiscal criado com sucesso!'))
        return super().form_valid(form)


class FiscalYearUpdateView(LoginRequiredMixin, UpdateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'core/fiscal_year_form.html'
    success_url = reverse_lazy('fiscal_year_list')
    
    def get_queryset(self):
        company = getattr(self.request, 'current_company', None)
        if company:
            return FiscalYear.objects.filter(company=company)
        return FiscalYear.objects.none()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = getattr(self.request, 'current_company', None)
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _('Ano fiscal atualizado com sucesso!'))
        return super().form_valid(form)


class FiscalYearDetailView(LoginRequiredMixin, DetailView):
    model = FiscalYear
    template_name = 'core/fiscal_year_detail.html'
    context_object_name = 'fiscal_year'
    
    def get_queryset(self):
        company = getattr(self.request, 'current_company', None)
        if company:
            return FiscalYear.objects.filter(company=company)
        return FiscalYear.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fiscal_year = self.get_object()
        
        # Obter transações do ano fiscal
        transactions = Transaction.objects.filter(
            company=fiscal_year.company,
            date__range=(fiscal_year.start_date, fiscal_year.end_date)
        )
        
        # Contar total de transações
        transactions_count = transactions.count()
        context['transactions_count'] = transactions_count
        
        # Identificar contas de receita e despesa
        revenue_accounts = Account.objects.filter(
            company=fiscal_year.company, 
            type='R'  # Receitas
        ).values_list('id', flat=True)
        
        expense_accounts = Account.objects.filter(
            company=fiscal_year.company, 
            type='X'  # Despesas
        ).values_list('id', flat=True)
        
        # Calcular total de receitas (créditos em contas de receita)
        total_revenue = Transaction.objects.filter(
            company=fiscal_year.company,
            date__range=(fiscal_year.start_date, fiscal_year.end_date),
            credit_account_id__in=revenue_accounts
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calcular total de despesas (débitos em contas de despesa)
        total_expenses = Transaction.objects.filter(
            company=fiscal_year.company,
            date__range=(fiscal_year.start_date, fiscal_year.end_date),
            debit_account_id__in=expense_accounts
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calcular o resultado (receitas - despesas)
        result = total_revenue - total_expenses
        
        context['total_revenue'] = total_revenue
        context['total_expenses'] = total_expenses
        context['result'] = result
        context['transactions'] = transactions.order_by('-date', '-id')[:10]
        
        return context


class FiscalYearCloseView(LoginRequiredMixin, FormView):
    template_name = 'core/fiscal_year_close.html'
    form_class = FiscalYearCloseForm
    success_url = reverse_lazy('fiscal_year_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.fiscal_year = get_object_or_404(
            FiscalYear, 
            pk=self.kwargs['pk'],
            company=getattr(self.request, 'current_company', None)
        )
        kwargs['fiscal_year'] = self.fiscal_year
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fiscal_year'] = self.fiscal_year
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Marcar o ano fiscal como fechado
            self.fiscal_year.is_closed = True
            self.fiscal_year.closed_date = datetime.date.today()
            self.fiscal_year.save()
            
            messages.success(self.request, _('Ano fiscal fechado com sucesso!'))
            return HttpResponseRedirect(self.get_success_url())

class UserRegistrationView(FormView):
    template_name = 'core/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('registration_done')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Desativar o usuário até que ele confirme o email
        user.save()
        
        # Criar token de ativação
        token = UserActivationToken.objects.create(user=user)
        
        # Enviar email de ativação
        try:
            activation_url = self.request.build_absolute_uri(
                reverse('activate_account', kwargs={'token': token.token})
            )
            
            context = {
                'user': user,
                'activation_url': activation_url,
                'valid_days': settings.ACCOUNT_ACTIVATION_DAYS,
            }
            
            html_message = render_to_string('core/email/activation_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Ative sua conta no Sistema Contábil Estudos',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de ativação enviado para {user.email}")
            
        except Exception as e:
            # Registrar o erro, mas não impedir o registro
            logger.error(f"Erro ao enviar email de ativação: {str(e)}")
            # Ativar o usuário mesmo sem o email
            user.is_active = True
            user.save()
            if token:
                token.delete()
            
            messages.warning(self.request, _('Sua conta foi criada, mas não foi possível enviar o email de ativação. Entre em contato com o suporte.'))
        
        return super().form_valid(form)

class AboutView(TemplateView):
    template_name = 'core/about.html'

class RegistrationDoneView(TemplateView):
    template_name = 'core/registration_done.html'

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    
    def form_invalid(self, form):
        """
        Verifica se o erro é devido a uma conta inativa e adiciona uma mensagem específica.
        """
        username = form.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                if not user.is_active:
                    messages.error(
                        self.request, 
                        _('Esta conta ainda não foi ativada. Por favor, verifique seu email para o link de ativação ou entre em contato com o suporte.')
                    )
            except User.DoesNotExist:
                # Não fazemos nada aqui, deixamos o formulário mostrar o erro padrão
                pass
        return super().form_invalid(form)

def activate_account(request, token):
    try:
        activation_token = UserActivationToken.objects.get(token=token)
        
        # Verificar se o token é válido
        if not activation_token.is_valid():
            messages.error(request, _('O link de ativação expirou. Por favor, registre-se novamente.'))
            return redirect('register')
        
        # Ativar o usuário
        user = activation_token.user
        user.is_active = True
        user.save()
        
        # Excluir o token de ativação
        activation_token.delete()
        
        messages.success(request, _('Sua conta foi ativada com sucesso! Agora você pode fazer login.'))
        
        # Autenticar o usuário automaticamente especificando o backend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Redirecionar para a criação de empresa
        messages.info(request, _('Para começar a usar o sistema, cadastre sua primeira empresa.'))
        return redirect('company_create')
    except UserActivationToken.DoesNotExist:
        messages.error(request, _('Link de ativação inválido.'))
        return redirect('register')

@login_required
def set_current_company(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if company_id:
            # Verificar se o usuário tem acesso a esta empresa
            try:
                company = Company.objects.get(id=company_id, users=request.user.profile)
                request.session['current_company_id'] = int(company_id)
                
                # Atualizar a última empresa utilizada no perfil do usuário
                profile = request.user.profile
                profile.last_company_id = int(company_id)
                profile.save(update_fields=['last_company_id'])
                
                messages.success(request, f'Empresa alterada para {company.name}')
                
                # Redirecionar para o dashboard para garantir que a empresa seja carregada
                return redirect('dashboard')
            except Company.DoesNotExist:
                messages.error(request, 'Você não tem acesso a esta empresa')
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

class DocumentationView(TemplateView):
    template_name = 'docs/base_docs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doc_title'] = self.get_doc_title()
        context['doc_page'] = self.get_doc_page()
        context['last_updated'] = self.get_last_updated()
        return context
    
    def get_doc_title(self):
        return "Documentação do Sistema"
    
    def get_doc_page(self):
        return "overview"
    
    def get_last_updated(self):
        return datetime.date.today()


class OverviewView(DocumentationView):
    template_name = 'docs/overview.html'
    
    def get_doc_title(self):
        return "Visão Geral do Sistema"
    
    def get_doc_page(self):
        return "overview"


class VisualGuideView(DocumentationView):
    template_name = 'docs/visual_guide.html'
    
    def get_doc_title(self):
        return "Guia Visual do Sistema"
    
    def get_doc_page(self):
        return "visual_guide"


class ExamplesView(DocumentationView):
    template_name = 'docs/examples.html'
    
    def get_doc_title(self):
        return "Exemplos Práticos"
    
    def get_doc_page(self):
        return "examples"


class MaintenanceView(DocumentationView):
    template_name = 'docs/maintenance.html'
    
    def get_doc_title(self):
        return "Guia de Manutenção"
    
    def get_doc_page(self):
        return "maintenance"
