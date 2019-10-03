from django.urls import include, path

from .views.external import Homepage, CallsList, ProposalView, ProposalThankYouView
from .views.internal import CallView, ProposalsList, InternalHomepage


urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('calls/', CallsList.as_view(), name='calls-list'),
    path('proposal/add/', ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', ProposalView.as_view(), name='proposal-update'),
    path('proposal/thank-you/<uuid:uuid>/', ProposalThankYouView.as_view(), name='proposal-thank-you'),

    path('internal/proposals', ProposalsList.as_view(), name='internal-proposals-list'),
    path('internal/call/add/', CallView.as_view(), name='call-add'),
    path('internal/', InternalHomepage.as_view(), name='internal-homepage'),

    path('accounts/', include('django.contrib.auth.urls')),
]
