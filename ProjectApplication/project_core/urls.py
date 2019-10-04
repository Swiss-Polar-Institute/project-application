from django.urls import include, path

from .views.external import Homepage, CallsList, ProposalView
from .views.internal import CallView, ProposalsList, InternalHomepage, InternalCallsList


urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('calls/', CallsList.as_view(), name='calls-list'),
    path('proposal/add/', ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', ProposalView.as_view(), name='proposal-update'),

    path('internal/proposals', ProposalsList.as_view(), name='internal-proposals-list'),
    path('internal/call/add/', CallView.as_view(), name='call-add'),
    path('internal/call/<int:id>/', CallView.as_view(), name='call-update'),
    path('internal/calls/', InternalCallsList.as_view(), name='internal-calls-list'),
    path('internal/', InternalHomepage.as_view(), name='internal-homepage'),

    path('accounts/', include('django.contrib.auth.urls')),
]
