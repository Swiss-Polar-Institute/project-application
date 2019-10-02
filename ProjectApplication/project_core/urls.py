from django.urls import path

from .views import Homepage, CallsList, ProposalView, ProposalsList, ProposalThankYouView

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('calls/', CallsList.as_view(), name='calls-list'),
    path('proposals', ProposalsList.as_view(), name='proposals-list'),
    path('proposal/add/', ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', ProposalView.as_view(), name='proposal-update'),
    path('proposal/thank-you/<uuid:uuid>/', ProposalThankYouView.as_view(), name='proposal-thank-you'),
]
