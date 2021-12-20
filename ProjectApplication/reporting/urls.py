from django.urls import path
import reporting.views

urlpatterns = [
    path('logged/reporting/',
         reporting.views.Reporting.as_view(),
         name='logged-reporting'),
    path('logged/reporting/excel/downloads/projects_balance',
         reporting.views.ProjectsBalanceExcel.as_view(),
         name='logged-reporting-finance-projects_balance-excel'),
    path('logged/reporting/excel/downloads/projects_information',
         reporting.views.ProjectsAllInformationExcel.as_view(),
         name='logged-reporting-projects_information-excel')
]
