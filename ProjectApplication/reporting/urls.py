from django.urls import path

import reporting.views

urlpatterns = [
    path('logged/reporting/',
         reporting.views.Reporting.as_view(),
         name='logged-reporting'),
]
