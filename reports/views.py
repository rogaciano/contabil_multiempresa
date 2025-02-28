from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Q
import csv
import locale
from datetime import datetime, timedelta
from io import BytesIO

from .models import Report
from accounts.models import Account, AccountType
from transactions.models import Transaction
from core.models import CompanyInfo

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import tempfile
import os
from xhtml2pdf import pisa

# Create your views here.

class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/balance_sheet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        end_date = self.request.GET.get('end_date', timezone.now().date())
        
        # Criar relatório
        report = Report.objects.create(
            type='BS',
            start_date=None,  # Balanço não precisa de data inicial
            end_date=end_date,
            generated_by=self.request.user
        )
        
        # Obter dados do balanço
        context.update(report.get_balance_sheet_data())
        context['report'] = report
        context['end_date'] = end_date
        
        # Calcular total de passivos + patrimônio líquido
        context['total_liabilities_equity'] = context['total_liabilities'] + context['total_equity']
        
        # Calcular diferença entre ativos e passivos + patrimônio líquido
        context['difference'] = abs(context['total_assets'] - context['total_liabilities_equity'])
        
        return context

class IncomeStatementView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/income_statement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if not start_date:
            # Se não especificado, usar primeiro dia do ano atual
            today = timezone.now()
            start_date = today.replace(month=1, day=1).date()
        
        if not end_date:
            end_date = timezone.now().date()
        
        # Criar relatório
        report = Report.objects.create(
            type='IS',
            start_date=start_date,
            end_date=end_date,
            generated_by=self.request.user
        )
        
        # Obter dados do DRE
        context.update(report.get_income_statement_data())
        context['report'] = report
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['now'] = timezone.now()
        
        return context

class CashFlowView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/cash_flow.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if not start_date:
            # Se não especificado, usar primeiro dia do mês atual
            today = timezone.now()
            start_date = today.replace(day=1).date()
        
        if not end_date:
            end_date = timezone.now().date()
        
        # Criar relatório
        report = Report.objects.create(
            type='CF',
            start_date=start_date,
            end_date=end_date,
            generated_by=self.request.user
        )
        
        # Obter dados do fluxo de caixa
        context.update(report.get_cash_flow_data())
        context['report'] = report
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['now'] = timezone.now()
        
        return context

class TrialBalanceView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/trial_balance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        end_date = self.request.GET.get('end_date', timezone.now().date())
        
        accounts = Account.objects.filter(is_active=True).order_by('code')
        trial_balance = []
        total_debit = total_credit = 0
        
        for account in accounts:
            balance = account.get_balance(end_date=end_date)
            if balance != 0:
                # Determinar se o saldo deve ir para débito ou crédito com base no tipo de conta
                if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                    # Para contas de Ativo e Despesa, saldo positivo é débito, negativo é crédito
                    debit = balance if balance > 0 else 0
                    credit = -balance if balance < 0 else 0
                else:
                    # Para contas de Passivo, Patrimônio Líquido e Receita, saldo positivo é crédito, negativo é débito
                    debit = -balance if balance < 0 else 0
                    credit = balance if balance > 0 else 0
                
                trial_balance.append({
                    'account': account,
                    'debit': debit,
                    'credit': credit
                })
                total_debit += debit
                total_credit += credit
        
        context.update({
            'trial_balance': trial_balance,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'end_date': end_date,
            'now': timezone.now()
        })
        
        return context

class GeneralLedgerView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/general_ledger.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account_id = self.request.GET.get('account')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Converter strings para objetos date
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if account_id:
            account = Account.objects.get(pk=account_id)
            transactions = Transaction.objects.filter(
                Q(debit_account=account) | Q(credit_account=account)
            )
            
            if start_date:
                transactions = transactions.filter(date__gte=start_date)
            if end_date:
                transactions = transactions.filter(date__lte=end_date)
                
            transactions = transactions.order_by('date', 'created_at')
            
            # Calcular saldo inicial
            if start_date:
                # Calcular o saldo até o dia anterior à data inicial
                day_before_start = start_date - timedelta(days=1)
                initial_balance = account.get_balance(end_date=day_before_start)
            else:
                initial_balance = 0
            
            # Preparar movimentos com saldo
            movements = []
            running_balance = initial_balance
            
            for transaction in transactions:
                if transaction.debit_account == account:
                    amount = transaction.amount
                else:
                    amount = -transaction.amount
                
                running_balance += amount
                movements.append({
                    'transaction': transaction,
                    'amount': amount,
                    'balance': running_balance
                })
            
            context.update({
                'account': account,
                'initial_balance': initial_balance,
                'movements': movements,
                'final_balance': running_balance
            })
        
        context['accounts'] = Account.objects.filter(is_active=True)
        context['start_date'] = start_date_str
        context['end_date'] = end_date_str
        context['now'] = timezone.now()
        
        return context

class BalanceStatusView(LoginRequiredMixin, View):
    """View para fornecer o status do balanço (totais de ativos e passivos+patrimônio líquido)."""
    
    def get(self, request, *args, **kwargs):
        import json
        from django.http import JsonResponse
        
        # Criar relatório temporário para obter os dados do balanço
        report = Report.objects.create(
            type='BS',
            end_date=timezone.now().date(),
            generated_by=request.user
        )
        
        # Obter dados do balanço
        balance_data = report.get_balance_sheet_data()
        
        # Excluir o relatório temporário (não precisamos salvá-lo)
        report.delete()
        
        # Preparar resposta
        response_data = {
            'total_assets': balance_data['total_assets'],
            'total_liabilities_equity': balance_data['total_liabilities'] + balance_data['total_equity'],
            'is_balanced': abs(balance_data['total_assets'] - (balance_data['total_liabilities'] + balance_data['total_equity'])) < 0.01,
            'difference': abs(balance_data['total_assets'] - (balance_data['total_liabilities'] + balance_data['total_equity']))
        }
        
        return JsonResponse(response_data)

class ReportExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_type = kwargs.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{end_date}.csv"'
        
        writer = csv.writer(response)
        
        if report_type == 'BS':
            self._export_balance_sheet(writer, end_date)
        elif report_type == 'IS':
            self._export_income_statement(writer, start_date, end_date)
        elif report_type == 'CF':
            self._export_cash_flow(writer, start_date, end_date)
        elif report_type == 'TB':
            self._export_trial_balance(writer, end_date)
        
        return response
    
    def _export_balance_sheet(self, writer, end_date):
        try:
            # Configurar o locale para o padrão brasileiro
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except:
            try:
                # Fallback para Windows
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            except:
                pass
                
        writer.writerow(['Balanço Patrimonial', end_date])
        writer.writerow([])
        
        # Ativos
        writer.writerow(['Ativos'])
        assets = Account.objects.filter(type=AccountType.ASSET, is_active=True)
        total_assets = 0
        for account in assets:
            balance = account.get_balance(end_date=end_date)
            formatted_balance = locale.format_string('%.2f', balance, grouping=True)
            writer.writerow([account.code, account.name, formatted_balance])
            total_assets += balance
        writer.writerow(['Total Ativos', '', locale.format_string('%.2f', total_assets, grouping=True)])
        writer.writerow([])
        
        # Passivos
        writer.writerow(['Passivos'])
        liabilities = Account.objects.filter(type=AccountType.LIABILITY, is_active=True)
        total_liabilities = 0
        for account in liabilities:
            balance = account.get_balance(end_date=end_date)
            formatted_balance = locale.format_string('%.2f', balance, grouping=True)
            writer.writerow([account.code, account.name, formatted_balance])
            total_liabilities += balance
        writer.writerow(['Total Passivos', '', locale.format_string('%.2f', total_liabilities, grouping=True)])
        writer.writerow([])
        
        # Patrimônio Líquido
        writer.writerow(['Patrimônio Líquido'])
        equity = Account.objects.filter(type=AccountType.EQUITY, is_active=True)
        total_equity = 0
        for account in equity:
            balance = account.get_balance(end_date=end_date)
            formatted_balance = locale.format_string('%.2f', balance, grouping=True)
            writer.writerow([account.code, account.name, formatted_balance])
            total_equity += balance
        writer.writerow(['Total Patrimônio Líquido', '', locale.format_string('%.2f', total_equity, grouping=True)])
        
        # Total Passivo + PL
        total_liabilities_equity = total_liabilities + total_equity
        writer.writerow(['Total Passivo + Patrimônio Líquido', '', locale.format_string('%.2f', total_liabilities_equity, grouping=True)])
        
        # Verificar se o balanço está equilibrado
        difference = total_assets - total_liabilities_equity
        if abs(difference) > 0.01:  # Tolerância para erros de arredondamento
            writer.writerow([])
            writer.writerow(['ATENÇÃO: Balanço não equilibrado. Diferença:', '', locale.format_string('%.2f', difference, grouping=True)])
    
    def _export_income_statement(self, writer, start_date, end_date):
        writer.writerow(['Demonstração do Resultado', f'{start_date} a {end_date}'])
        writer.writerow([])
        
        # Receitas
        writer.writerow(['Receitas'])
        revenues = Account.objects.filter(type=AccountType.REVENUE, is_active=True)
        total_revenue = 0
        for account in revenues:
            balance = account.get_balance(start_date=start_date, end_date=end_date)
            writer.writerow([account.code, account.name, balance])
            total_revenue += balance
        writer.writerow(['Total Receitas', '', total_revenue])
        writer.writerow([])
        
        # Despesas
        writer.writerow(['Despesas'])
        expenses = Account.objects.filter(type=AccountType.EXPENSE, is_active=True)
        total_expenses = 0
        for account in expenses:
            balance = account.get_balance(start_date=start_date, end_date=end_date)
            writer.writerow([account.code, account.name, balance])
            total_expenses += balance
        writer.writerow(['Total Despesas', '', total_expenses])
        writer.writerow([])
        
        # Resultado
        writer.writerow(['Resultado do Período', '', total_revenue - total_expenses])
    
    def _export_cash_flow(self, writer, start_date, end_date):
        writer.writerow(['Fluxo de Caixa', f'{start_date} a {end_date}'])
        writer.writerow([])
        
        cash_accounts = Account.objects.filter(
            type=AccountType.ASSET,
            is_active=True,
            code__startswith='1.1.1'
        )
        
        # Saldo inicial
        initial_balance = sum(
            account.get_balance(end_date=start_date)
            for account in cash_accounts
        )
        writer.writerow(['Saldo Inicial', '', initial_balance])
        writer.writerow([])
        
        # Movimentações
        writer.writerow(['Data', 'Descrição', 'Entrada', 'Saída'])
        transactions = Transaction.objects.filter(
            Q(debit_account__in=cash_accounts) | Q(credit_account__in=cash_accounts),
            date__range=[start_date, end_date]
        ).order_by('date')
        
        for transaction in transactions:
            if transaction.debit_account in cash_accounts:
                writer.writerow([
                    transaction.date,
                    transaction.description,
                    transaction.amount,
                    ''
                ])
            else:
                writer.writerow([
                    transaction.date,
                    transaction.description,
                    '',
                    transaction.amount
                ])
        
        # Saldo final
        final_balance = sum(
            account.get_balance(end_date=end_date)
            for account in cash_accounts
        )
        writer.writerow([])
        writer.writerow(['Saldo Final', '', final_balance])
    
    def _export_trial_balance(self, writer, end_date):
        writer.writerow(['Balancete', end_date])
        writer.writerow([])
        writer.writerow(['Código', 'Conta', 'Débito', 'Crédito'])
        
        accounts = Account.objects.filter(is_active=True).order_by('code')
        total_debit = total_credit = 0
        
        for account in accounts:
            balance = account.get_balance(end_date=end_date)
            if balance != 0:
                # Determinar se o saldo deve ir para débito ou crédito com base no tipo de conta
                if account.type in [AccountType.ASSET, AccountType.EXPENSE]:
                    # Para contas de Ativo e Despesa, saldo positivo é débito, negativo é crédito
                    debit = balance if balance > 0 else 0
                    credit = -balance if balance < 0 else 0
                else:
                    # Para contas de Passivo, Patrimônio Líquido e Receita, saldo positivo é crédito, negativo é débito
                    debit = -balance if balance < 0 else 0
                    credit = balance if balance > 0 else 0
                
                writer.writerow([account.code, account.name, debit, credit])
                total_debit += debit
                total_credit += credit
        
        writer.writerow([])
        writer.writerow(['Total', '', total_debit, total_credit])

class ReportPDFView(LoginRequiredMixin, View):
    """
    View para exportar relatórios em PDF.
    """
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type', 'BS')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Converter as datas para objetos date
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().replace(day=1).date()
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()
        
        # Obter o relatório mais recente ou criar um novo
        report = Report.objects.filter(
            type=report_type,
            start_date=start_date,
            end_date=end_date
        ).order_by('-generated_at').first()
        
        if not report:
            # Criar um novo relatório se não existir
            report = Report.objects.create(
                type=report_type,
                start_date=start_date,
                end_date=end_date,
                generated_by=request.user,
                notes=f'Relatório gerado em {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}'
            )
        
        # Obter os dados do relatório
        # Timestamp para o nome do arquivo
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        
        if report_type == 'BS':
            template_name = 'reports/pdf/balance_sheet_pdf.html'
            context = report.get_balance_sheet_data()
            filename = f'balanco_patrimonial_{start_date.strftime("%Y%m%d")}_a_{end_date.strftime("%Y%m%d")}_gerado_{timestamp}.pdf'
            title = 'Balanço Patrimonial'
        elif report_type == 'IS':
            template_name = 'reports/pdf/income_statement_pdf.html'
            context = report.get_income_statement_data()
            filename = f'demonstracao_resultado_{start_date.strftime("%Y%m%d")}_a_{end_date.strftime("%Y%m%d")}_gerado_{timestamp}.pdf'
            title = 'Demonstração do Resultado'
        elif report_type == 'CF':
            template_name = 'reports/pdf/cash_flow_pdf.html'
            context = report.get_cash_flow_data()
            filename = f'fluxo_caixa_{start_date.strftime("%Y%m%d")}_a_{end_date.strftime("%Y%m%d")}_gerado_{timestamp}.pdf'
            title = 'Fluxo de Caixa'
        elif report_type == 'TB':
            template_name = 'reports/pdf/trial_balance_pdf.html'
            context = report.get_trial_balance_data()
            filename = f'balancete_{start_date.strftime("%Y%m%d")}_a_{end_date.strftime("%Y%m%d")}_gerado_{timestamp}.pdf'
            title = 'Balancete'
        elif report_type == 'GL':
            template_name = 'reports/pdf/general_ledger_pdf.html'
            # Obter o ID da conta da URL
            account_id = request.GET.get('account')
            if not account_id:
                return HttpResponse('ID da conta não especificado', status=400)
                
            # Adicionar o ID da conta às notas do relatório
            report.notes = f'account_id:{account_id}\n{report.notes}'
            report.save()
            
            context = report.get_general_ledger_data()
            if 'error' in context:
                return HttpResponse(context['error'], status=400)
                
            account_code = context['account'].code
            filename = f'razao_{account_code}_{start_date.strftime("%Y%m%d")}_a_{end_date.strftime("%Y%m%d")}_gerado_{timestamp}.pdf'
            title = f'Razão Geral - {context["account"].code} - {context["account"].name}'
        else:
            return HttpResponse('Tipo de relatório inválido', status=400)
        
        # Adicionar informações comuns ao contexto
        context.update({
            'report': report,
            'start_date': start_date,
            'end_date': end_date,
            'now': timezone.now(),
            'title': title,
            'company': CompanyInfo.objects.first()
        })
        
        # Renderizar o HTML
        html_string = render_to_string(template_name, context)
        
        # Criar o PDF usando xhtml2pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Função para lidar com links para recursos estáticos
        def link_callback(uri, rel):
            """
            Converte links HTML para caminhos absolutos do sistema de arquivos
            """
            # Usar o STATIC_ROOT para recursos estáticos
            if uri.startswith(settings.STATIC_URL):
                path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
                if os.path.isfile(path):
                    return path
                # Tentar encontrar o arquivo em STATICFILES_DIRS
                for static_dir in settings.STATICFILES_DIRS:
                    path = os.path.join(static_dir, uri.replace(settings.STATIC_URL, ""))
                    if os.path.isfile(path):
                        return path
            # Usar o MEDIA_ROOT para uploads
            if uri.startswith(settings.MEDIA_URL):
                path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
                if os.path.isfile(path):
                    return path
            # Retornar o URI como está para outros casos
            return uri

        # Converter HTML para PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(html_string.encode("UTF-8")),
            result,
            encoding='UTF-8',
            link_callback=link_callback
        )
        
        if not pdf.err:
            response.write(result.getvalue())
            return response
        else:
            return HttpResponse(f'Erro ao gerar PDF: {pdf.err}', status=500)
