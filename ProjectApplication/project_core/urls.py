from django.urls import include, path

from .views import external
from .views import management

urlpatterns = [
    path('', external.Homepage.as_view(), name='homepage'),
    path('calls/', external.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', external.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', external.ProposalView.as_view(), name='proposal-update'),
    path('proposal/thank-you/<uuid:uuid>/', external.ProposalThankYouView.as_view(), name='proposal-thank-you'),

    path('management/proposals', management.ProposalsList.as_view(), name='management-proposals-list'),
    path('management/call/add/', management.CallView.as_view(), name='call-add'),
    path('management/call/<int:id>/', management.CallView.as_view(), name='call-update'),
    path('management/call/updated/<int:id>/', management.CallUpdated.as_view(), name='management-call-updated'),
    path('management/calls/', management.CallsList.as_view(), name='management-calls-list'),
    path('management/', management.Homepage.as_view(), name='management-homepage'),

    path('management/templatequestion/add', management.TemplateQuestionCreateView.as_view(), name='question-add'),
    path('management/templatequestion/<int:pk>/', management.TemplateQuestionDetailView.as_view(), name='question-detail'),
    path('management/templatequestion/<int:pk>/update', management.TemplateQuestionUpdateView.as_view(), name='question-update'),
    path('management/templatequestions/', management.QuestionsList.as_view(), name='questions-list'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('autocomplete/organisations/', external.OrganisationsAutocomplete.as_view(),
         name='autocomplete-organisations'),
    path('autocomplete/keywords/', external.KeywordsAutocomplete.as_view(create_field='name'),
         name='autocomplete-keywords')
]
