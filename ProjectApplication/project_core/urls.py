from django.urls import path

from .views import Homepage, ProposalForm, Calls, Proposal

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('calls/', Calls.as_view(), name='calls_list'),
    path('proposal/new/', Proposal.as_view(), name='proposal_new'),

]
