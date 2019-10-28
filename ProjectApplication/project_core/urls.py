from django.urls import include, path

from .views import external
from .views import management

from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    path('', external.Homepage.as_view(), name='homepage'),
    path('calls/', external.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', external.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/', external.ProposalView.as_view(), name='proposal-update'),
    path('proposal/thank-you/<uuid:uuid>/', external.ProposalThankYouView.as_view(), name='proposal-thank-you'),
    path('proposal/too-late/', external.ProposalTooLate.as_view(), name='proposal-too-late'),

    path('management/proposals', management.ProposalsList.as_view(), name='management-proposals-list'),
    path('management/call/list', management.CallsList.as_view(), name='management-calls-list'),
    path('management/call/add/', management.CallView.as_view(), name='call-add'),
    path('management/call/<int:id>/update', management.CallView.as_view(), name='management-call-update'),
    path('management/call/<int:id>/', management.CallViewDetails.as_view(), name='management-call-detail'),
    path('management/call/updated/<int:id>/', management.CallUpdated.as_view(), name='management-call-updated'),
    path('management/calls/', management.CallsList.as_view(), name='management-calls'),
    path('management/', management.Homepage.as_view(), name='management-homepage'),

    path('management/templatequestion/add', management.TemplateQuestionCreateView.as_view(), name='template-question-add'),
    path('management/templatequestion/<int:pk>/', management.TemplateQuestionDetailView.as_view(), name='template-question-detail'),
    path('management/templatequestion/<int:pk>/update', management.TemplateQuestionUpdateView.as_view(), name='template-question-update'),
    path('management/templatequestions/', management.QuestionsList.as_view(), name='template-questions-list'),

    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.tmpl',
                                      extra_context={'contact': settings.LOGIN_CONTACT})),
    path('accounts/', include('django.contrib.auth.urls')),

    path('autocomplete/organisations/', external.OrganisationsAutocomplete.as_view(),
         name='autocomplete-organisations'),
    path('autocomplete/keywords/', external.KeywordsAutocomplete.as_view(create_field='name'),
         name='autocomplete-keywords')
]
