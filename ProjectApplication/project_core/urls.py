from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from .views import common
from .views import external
from .views import management
from django.views.defaults import server_error

urlpatterns = [
    path('', external.homepage.Homepage.as_view(), name='homepage'),
    path('admin/jsi18n/', JavaScriptCatalog.as_view(), name='javascript-jsi18n'),
    path('calls/', external.call.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', external.proposal.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/update', external.proposal.ProposalView.as_view(),
         name='proposal-update'),
    path('proposal/<uuid:uuid>/', external.proposal.ProposalDetailView.as_view(),
         name='proposal-detail'),
    path('proposal/thank-you/<uuid:uuid>/', external.proposal.ProposalThankYouView.as_view(),
         name='proposal-thank-you'),
    path('proposal/cannot-modify/', external.proposal.ProposalCannotModify.as_view(),
         name='proposal-cannot-modify'),
    path('proposal/question_answer/file/<int:proposal_qa_file_id>/<str:md5>',
         common.proposal.ProposalQuestionAnswerFileView.as_view(),
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

    path('management/template_question/add', management.template_question.TemplateQuestionCreateView.as_view(),
         name='template-question-add'),
    path('management/template_question/<int:pk>/', management.template_question.TemplateQuestionDetailView.as_view(),
         name='template-question-detail'),
    path('management/template_question/<int:pk>/update',
         management.template_question.TemplateQuestionUpdateView.as_view(),
         name='template-question-update'),
    path('management/template_questions/', management.template_question.TemplateQuestionList.as_view(),
         name='template-questions-list'),

    path('management/funding_instrument/add', management.funding_instrument.FundingInstrumentCreateView.as_view(),
         name='funding-instrument-add'),
    path('management/funding_instrument/<int:pk>/', management.funding_instrument.FundingInstrumentDetailView.as_view(),
         name='funding-instrument-detail'),
    path('management/funding_instrument/<int:pk>/update',
         management.funding_instrument.FundingInstrumentUpdateView.as_view(),
         name='funding-instrument-update'),
    path('management/funding_instruments/', management.funding_instrument.FundingInstrumentList.as_view(),
         name='funding-instruments-list'),

    path('management/contact/add', management.contact.ContactsCreateView.as_view(), name='management-contact-add'),
    path('management/contact/<int:pk>/', management.contact.ContactDetailView.as_view(), name='contact-detail'),
    path('management/contact/<int:pk>/update', management.contact.ContactUpdateView.as_view(), name='contact-update'),
    path('management/contacts/', management.contact.ContactsListView.as_view(), name='management-contacts-list'),

    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.tmpl',
                                      extra_context={'contact': settings.LOGIN_CONTACT,
                                                     'demo_management_user': settings.DEMO_MANAGEMENT_USER,
                                                     'demo_management_password': settings.DEMO_MANAGEMENT_PASSWORD}),
         name='accounts-login'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('autocomplete/organisations/', common.autocomplete.OrganisationsAutocomplete.as_view(create_field='name'),
         name='autocomplete-organisation-names'),
    path('autocomplete/keywords/',
         common.autocomplete.KeywordsAutocomplete.as_view(create_field='name'),
         name='autocomplete-keywords'),

    path('raises500/', server_error),
]
