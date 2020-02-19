from django.urls import path

import project_core.views.logged

urlpatterns = [
    path('logged/proposal/<uuid:uuid>/evaluation',
         project_core.views.logged.proposal.ProposalEvaluationDetail.as_view(),
         name='logged-proposal-evaluation-detail'),
    path('logged/proposal/<uuid:uuid>/evaluation/update/',
         project_core.views.logged.proposal.ProposalEvaluationUpdate.as_view(),
         name='logged-proposal-evaluation-update'),
]
