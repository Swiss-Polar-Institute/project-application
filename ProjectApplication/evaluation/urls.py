from django.urls import path

import evaluation.views
import project_core.views.logged

urlpatterns = [
    path('logged/proposal/<uuid:uuid>/evaluation',
         evaluation.views.ProposalEvaluationDetail.as_view(),
         name='logged-proposal-evaluation-detail'),
    path('logged/proposal/<uuid:uuid>/evaluation/update/',
         evaluation.views.ProposalEvaluationUpdate.as_view(),
         name='logged-proposal-evaluation-update'),
]
