from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

import project_core.views.common.autocomplete
import project_core.views.common.proposal
import project_core.views.external.call
import project_core.views.external.proposal
from .views import management

urlpatterns = [
    path('', project_core.views.external.homepage.Homepage.as_view(), name='homepage'),
    path('admin/jsi18n/', JavaScriptCatalog.as_view(), name='javascript-jsi18n'),
    path('calls/', project_core.views.external.call.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', project_core.views.external.proposal.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/update', project_core.views.external.proposal.ProposalView.as_view(),
         name='proposal-update'),
    path('proposal/<uuid:uuid>/', project_core.views.external.proposal.ProposalDetailView.as_view(),
         name='proposal-detail'),
    path('proposal/thank-you/<uuid:uuid>/', project_core.views.external.proposal.ProposalThankYouView.as_view(),
         name='proposal-thank-you'),
    path('proposal/too-late/', project_core.views.external.proposal.ProposalTooLate.as_view(),
         name='proposal-too-late'),
    path('proposal/questionanswer/file/<str:md5>',
         project_core.views.common.proposal.ProposalQuestionAnswerFileView.as_view(),
         name='proposal-question-answer-file'),

    path('management/proposals', management.proposal.ProposalsList.as_view(), name='management-proposals-list'),
    path('management/proposal/<uuid:uuid>/update', management.proposal.ProposalView.as_view(),
         name='management-proposal-update'),
    path('management/proposal/<uuid:uuid>/', management.proposal.ProposalDetailView.as_view(),
         name='management-proposal-detail'),
    path('management/proposals/export/excel/<int:call>/', management.proposal.ProposalsExportExcel.as_view(),
         name='management-export-proposals-for-call-excel'),

    path('management/call/list', management.call.CallsList.as_view(), name='management-calls-list'),
    path('management/call/add/', management.call.CallView.as_view(), name='call-add'),
    path('management/call/<int:id>/update', management.call.CallView.as_view(),
         name='management-call-update'),
    path('management/call/<int:id>/', management.call.CallDetailView.as_view(),
         name='management-call-detail'),
    path('management/calls/', management.call.CallsList.as_view(), name='management-calls'),
    path('management/', management.homepage.Homepage.as_view(), name='management-homepage'),

    path('management/templatequestion/add', management.templatequestion.TemplateQuestionCreateView.as_view(),
         name='template-question-add'),
    path('management/templatequestion/<int:pk>/', management.templatequestion.TemplateQuestionDetailView.as_view(),
         name='template-question-detail'),
    path('management/templatequestion/<int:pk>/update',
         management.templatequestion.TemplateQuestionUpdateView.as_view(),
         name='template-question-update'),
    path('management/templatequestions/', management.templatequestion.TemplateQuestionList.as_view(),
         name='template-questions-list'),

    path('management/contact/add', management.contact.ContactsCreateView.as_view(), name='management-contact-add'),
    path('management/contact/<int:pk>/', management.contact.ContactDetailView.as_view(), name='contact-detail'),
    path('management/contact/<int:pk>/update', management.contact.ContactUpdateView.as_view(), name='contact-update'),
    path('management/contacts/', management.contact.ContactsListView.as_view(), name='management-contacts-list'),

    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.tmpl',
                                      extra_context={'contact': settings.LOGIN_CONTACT,
                                                     'demo_management_user': settings.DEMO_MANAGEMENT_USER,
                                                     'demo_management_password': settings.DEMO_MANAGEMENT_PASSWORD})),
    path('accounts/', include('django.contrib.auth.urls')),

    path('autocomplete/organisations/', project_core.views.common.autocomplete.OrganisationsAutocomplete.as_view(),
         name='autocomplete-organisations'),
    path('autocomplete/keywords/',
         project_core.views.common.autocomplete.KeywordsAutocomplete.as_view(create_field='name'),
         name='autocomplete-keywords')
]
