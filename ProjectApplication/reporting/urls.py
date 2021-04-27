from django.urls import path

import reporting.views

urlpatterns = [
    path('logged/reporting/',
         reporting.views.Reporting.as_view(),
         name='logged-reporting'),
    path('logged/reporting/csv/financial/projects_balance',
         reporting.views.ProjectsBalanceCsv.as_view(),
         name='logged-reporting-finance-projects_balance-csv')
]
