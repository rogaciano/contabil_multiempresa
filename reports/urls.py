from django.urls import path
from . import views

urlpatterns = [
    path('balance-sheet/', views.BalanceSheetView.as_view(), name='balance_sheet'),
    path('income-statement/', views.IncomeStatementView.as_view(), name='income_statement'),
    path('cash-flow/', views.CashFlowView.as_view(), name='cash_flow'),
    path('trial-balance/', views.TrialBalanceView.as_view(), name='trial_balance'),
    path('general-ledger/', views.GeneralLedgerView.as_view(), name='general_ledger'),
    path('export/<str:report_type>/', views.ReportExportView.as_view(), name='report_export'),
    path('export-pdf/', views.ReportPDFView.as_view(), name='report_export_pdf'),
    path('balance-status/', views.BalanceStatusView.as_view(), name='balance_status'),
]
