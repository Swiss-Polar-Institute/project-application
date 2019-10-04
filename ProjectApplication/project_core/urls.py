from django.urls import include, path

from .views import external
from .views import internal


urlpatterns = [
    path('', external.Homepage.as_view(), name='homepage'),
    path('calls/', external.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', external.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', external.ProposalView.as_view(), name='proposal-update'),
    path('proposal/thank-you/<uuid:uuid>/', external.ProposalThankYouView.as_view(), name='proposal-thank-you'),

    path('internal/proposals', internal.ProposalsList.as_view(), name='internal-proposals-list'),
    path('internal/call/add/', internal.CallView.as_view(), name='call-add'),
    path('internal/call/<int:id>/', internal.CallView.as_view(), name='call-update'),
    path('internal/call/updated/<int:id>/', internal.CallUpdated.as_view(), name='internal-call-updated'),
    path('internal/calls/', internal.CallsList.as_view(), name='internal-calls-list'),
    path('internal/', internal.Homepage.as_view(), name='internal-homepage'),

    path('accounts/', include('django.contrib.auth.urls')),
]
