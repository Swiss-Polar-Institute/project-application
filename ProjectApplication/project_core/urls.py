from django.urls import path

from .views import Homepage

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('/proposal/new', ProposalForm.as_view(), name='new_proposal'),
]
