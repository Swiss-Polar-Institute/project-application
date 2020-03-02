from django.urls import path

import evaluation.views

urlpatterns = [
    path('logged/proposal/<uuid:uuid>/evaluation',
         evaluation.views.ProposalEvaluationDetail.as_view(),
         name='logged-proposal-evaluation-detail'),
    path('logged/proposal/<uuid:uuid>/evaluation/update/',
         evaluation.views.ProposalEvaluationUpdate.as_view(),
         name='logged-proposal-evaluation-update'),
    path('logged/evaluation/list',
        evaluation.views.ProposalEvaluationList.as_view(),
        name='logged-evaluation-list')
]
