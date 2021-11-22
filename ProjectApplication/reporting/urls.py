from django.urls import path
import reporting.views

urlpatterns = [
    path('logged/reporting/',
         reporting.views.Reporting.as_view(),
         name='logged-reporting'),
    path('logged/reporting/excel/financial/projects_balance',
         reporting.views.ProjectsBalanceExcel.as_view(),
         name='logged-reporting-finance-projects_balance-excel')
]
