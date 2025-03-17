from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.db.models import Sum, Q
from django.utils import timezone

from accounts.models import Company, Account
from .models import DRETemplate, DRESection, DREAccount, DREReport, DREReportItem
from .forms import DRETemplateForm, DRESectionForm, DREAccountForm, DREReportForm

import logging
logger = logging.getLogger(__name__)

# Mixin para verificar se o usuário é administrador
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, _('Você não tem permissão para acessar esta página.'))
        return redirect('home')


class DRETemplateListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = DRETemplate
    template_name = 'financial_reports/dre_template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por regime tributário, se especificado
        tax_regime = self.request.GET.get('tax_regime')
        if tax_regime:
            queryset = queryset.filter(tax_regime=tax_regime)
            
        # Filtrar por status de ativo, se especificado
        is_active = self.request.GET.get('is_active')
        if is_active:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tax_regimes'] = Company.TaxRegime.choices
        return context


class DRETemplateDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = DRETemplate
    template_name = 'financial_reports/dre_template_detail.html'
    context_object_name = 'template'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.get_object()
        
        # Obter seções do template, ordenadas por ordem
        context['sections'] = template.sections.all().order_by('order')
        
        return context


class DRETemplateCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = DRETemplate
    form_class = DRETemplateForm
    template_name = 'financial_reports/dre_template_form.html'
    success_url = reverse_lazy('dre_template_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Template de DRE criado com sucesso!'))
        return super().form_valid(form)


class DRETemplateUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = DRETemplate
    form_class = DRETemplateForm
    template_name = 'financial_reports/dre_template_form.html'
    
    def get_success_url(self):
        return reverse('dre_template_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Template de DRE atualizado com sucesso!'))
        return super().form_valid(form)


class DRETemplateDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = DRETemplate
    template_name = 'financial_reports/dre_template_confirm_delete.html'
    success_url = reverse_lazy('dre_template_list')
    
    def delete(self, request, *args, **kwargs):
        template = self.get_object()
        
        # Verificar se existem relatórios usando este template
        if template.reports.exists():
            messages.error(request, _('Não é possível excluir este template pois existem relatórios associados a ele.'))
            return HttpResponseRedirect(self.get_success_url())
            
        messages.success(request, _('Template de DRE excluído com sucesso!'))
        return super().delete(request, *args, **kwargs)


class DRESectionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = DRESection
    form_class = DRESectionForm
    template_name = 'financial_reports/dre_section_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(DRETemplate, pk=template_id)
        kwargs['template'] = template
        return kwargs
    
    def form_valid(self, form):
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(DRETemplate, pk=template_id)
        
        form.instance.template = template
        messages.success(self.request, _('Seção de DRE criada com sucesso!'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template_id = self.kwargs.get('template_id')
        context['template'] = get_object_or_404(DRETemplate, pk=template_id)
        return context
    
    def get_success_url(self):
        template_id = self.kwargs.get('template_id')
        return reverse('dre_template_detail', kwargs={'pk': template_id})


class DRESectionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = DRESection
    form_class = DRESectionForm
    template_name = 'financial_reports/dre_section_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['template'] = self.object.template
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.object.template
        return context
    
    def get_success_url(self):
        return reverse('dre_template_detail', kwargs={'pk': self.object.template.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Seção de DRE atualizada com sucesso!'))
        return super().form_valid(form)


class DRESectionDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = DRESection
    template_name = 'financial_reports/dre_section_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('dre_template_detail', kwargs={'pk': self.object.template.pk})
    
    def delete(self, request, *args, **kwargs):
        section = self.get_object()
        template_id = section.template.pk
        
        # Verificar se existem subseções
        if section.children.exists():
            messages.error(request, _('Não é possível excluir esta seção pois existem subseções associadas a ela.'))
            return HttpResponseRedirect(self.get_success_url())
            
        messages.success(request, _('Seção de DRE excluída com sucesso!'))
        return super().delete(request, *args, **kwargs)


class DREReportListView(LoginRequiredMixin, ListView):
    model = DREReport
    template_name = 'financial_reports/dre_report_list.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obter a empresa atual do usuário
        current_company_id = self.request.session.get('current_company_id')
        if not current_company_id:
            # Se não houver empresa selecionada, retornar queryset vazio
            messages.warning(self.request, _('Selecione uma empresa para visualizar os relatórios.'))
            return DREReport.objects.none()
            
        # Filtrar relatórios pela empresa atual
        queryset = queryset.filter(company_id=current_company_id)
        
        # Filtrar por período, se especificado
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(Q(start_date__year=year) | Q(end_date__year=year))
            
        return queryset.order_by('-end_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter a empresa atual
        current_company_id = self.request.session.get('current_company_id')
        if current_company_id:
            try:
                company = Company.objects.get(id=current_company_id)
                context['company'] = company
                
                # Obter anos disponíveis para filtro
                years = DREReport.objects.filter(company_id=current_company_id).dates('end_date', 'year')
                context['years'] = [date.year for date in years]
            except Company.DoesNotExist:
                pass
                
        return context


class DREReportCreateView(LoginRequiredMixin, CreateView):
    model = DREReport
    form_class = DREReportForm
    template_name = 'financial_reports/dre_report_form.html'
    success_url = reverse_lazy('dre_report_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['company_id'] = self.request.session.get('current_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter a empresa atual
        current_company_id = self.request.session.get('current_company_id')
        if not current_company_id:
            messages.warning(self.request, _('Selecione uma empresa para criar um relatório.'))
            return context
            
        try:
            company = Company.objects.get(id=current_company_id)
            context['company'] = company
            
            # Obter template adequado para o regime tributário da empresa
            templates = DRETemplate.objects.filter(
                tax_regime=company.tax_regime,
                is_active=True
            )
            context['available_templates'] = templates
            
            if not templates.exists():
                messages.warning(self.request, _(
                    f'Não há templates de DRE disponíveis para o regime tributário {company.get_tax_regime_display()}. '
                    f'Entre em contato com o administrador do sistema.'
                ))
        except Company.DoesNotExist:
            messages.error(self.request, _('Empresa não encontrada.'))
            
        return context
    
    def form_valid(self, form):
        # Obter a empresa atual
        current_company_id = self.request.session.get('current_company_id')
        if not current_company_id:
            messages.error(self.request, _('Selecione uma empresa para criar um relatório.'))
            return self.form_invalid(form)
            
        try:
            company = Company.objects.get(id=current_company_id)
            form.instance.company = company
            form.instance.created_by = self.request.user
            
            # Obter template adequado para o regime tributário da empresa
            template = DRETemplate.objects.filter(
                tax_regime=company.tax_regime,
                is_active=True
            ).first()
            
            if not template:
                messages.error(self.request, _(
                    f'Não há templates de DRE disponíveis para o regime tributário {company.get_tax_regime_display()}. '
                    f'Entre em contato com o administrador do sistema.'
                ))
                return self.form_invalid(form)
                
            form.instance.template = template
            
            response = super().form_valid(form)
            
            # Gerar itens do relatório
            self.object.generate()
            
            messages.success(self.request, _('Relatório de DRE criado com sucesso!'))
            return response
        except Company.DoesNotExist:
            messages.error(self.request, _('Empresa não encontrada.'))
            return self.form_invalid(form)


class DREReportDetailView(LoginRequiredMixin, DetailView):
    model = DREReport
    template_name = 'financial_reports/dre_report_detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obter a empresa atual do usuário
        current_company_id = self.request.session.get('current_company_id')
        if current_company_id:
            # Filtrar relatórios pela empresa atual
            queryset = queryset.filter(company_id=current_company_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.get_object()
        
        # Obter itens do relatório, ordenados por ordem
        context['items'] = report.items.all().order_by('order')
        
        return context


class DREReportDeleteView(LoginRequiredMixin, DeleteView):
    model = DREReport
    template_name = 'financial_reports/dre_report_confirm_delete.html'
    success_url = reverse_lazy('dre_report_list')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obter a empresa atual do usuário
        current_company_id = self.request.session.get('current_company_id')
        if current_company_id:
            # Filtrar relatórios pela empresa atual
            queryset = queryset.filter(company_id=current_company_id)
            
        return queryset
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Relatório de DRE excluído com sucesso!'))
        return super().delete(request, *args, **kwargs)
