from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.defaults import server_error
from django.views.i18n import JavaScriptCatalog

from .views import common
from .views import external
from .views import management

urlpatterns = [
    path('', external.homepage.Homepage.as_view(), name='homepage'),
    path('admin/jsi18n/', JavaScriptCatalog.as_view(), name='javascript-jsi18n'),
    path('calls/', external.call.CallsList.as_view(), name='calls-list'),
    path('proposal/add/', external.proposal.ProposalView.as_view(), name='proposal-add'),
    path('proposal/<uuid:uuid>/update', external.proposal.ProposalView.as_view(),
         name='proposal-update'),
    path('proposal/<uuid:uuid>/', external.proposal.ProposalDetailView.as_view(),
         name='proposal-detail'),
    # path('review/proposal/<uuid:uuid>/', external.proposal.ProposalDetailView.as_view(),
    #      name='review-proposal-detail'),
    path('proposal/thank-you/<uuid:uuid>/', external.proposal.ProposalThankYouView.as_view(),
         name='proposal-thank-you'),
    path('proposal/cannot-modify/', external.proposal.ProposalCannotModify.as_view(),
         name='proposal-cannot-modify'),
    path('proposal/question_answer/file/<int:proposal_qa_file_id>/<str:md5>',
         common.proposal.ProposalQuestionAnswerFileView.as_view(),
         name='proposal-question-answer-file'),

    path('logged/proposals', management.proposal.ProposalsList.as_view(), name='management-proposals-list'),
    path('logged/proposal/<uuid:uuid>/update', management.proposal.ProposalView.as_view(),
         name='management-proposal-update'),
    path('logged/proposal/<uuid:uuid>/', management.proposal.ProposalDetailView.as_view(),
         name='management-proposal-detail'),
    path('logged/proposals/export/excel/<int:call>/', management.proposal.ProposalsExportExcel.as_view(),
         name='management-export-proposals-for-call-excel'),
    path('logged/proposals/export/csv/summary/<int:call>/', management.proposal.ProposalsExportCsvSummary.as_view(),
         name='management-export-proposals-csv-summary-call'),
    path('logged/proposals/export/csv/summary/', management.proposal.ProposalsExportCsvSummary.as_view(),
         name='management-export-proposals-csv-summary-all'),

    path('logged/call/list', management.call.CallsList.as_view(), name='management-calls-list'),
    path('logged/call/add/', management.call.CallView.as_view(), name='call-add'),
    path('logged/call/<int:id>/update', management.call.CallView.as_view(),
         name='management-call-update'),
    path('logged/call/<int:id>/', management.call.CallDetailView.as_view(),
         name='management-call-detail'),
    path('logged/calls/', management.call.CallsList.as_view(), name='management-calls'),
    path('logged/', management.homepage.Homepage.as_view(), name='management-homepage'),

    path('logged/template_question/add', management.template_question.TemplateQuestionCreateView.as_view(),
         name='template-question-add'),
    path('logged/template_question/<int:pk>/', management.template_question.TemplateQuestionDetailView.as_view(),
         name='template-question-detail'),
    path('logged/template_question/<int:pk>/update',
         management.template_question.TemplateQuestionUpdateView.as_view(),
         name='template-question-update'),
    path('logged/template_questions/', management.template_question.TemplateQuestionList.as_view(),
         name='template-questions-list'),

    path('logged/funding_instrument/add', management.funding_instrument.FundingInstrumentCreateView.as_view(),
         name='funding-instrument-add'),
    path('logged/funding_instrument/<int:pk>/', management.funding_instrument.FundingInstrumentDetailView.as_view(),
         name='funding-instrument-detail'),
    path('logged/funding_instrument/<int:pk>/update',
         management.funding_instrument.FundingInstrumentUpdateView.as_view(),
         name='funding-instrument-update'),
    path('logged/funding_instruments/', management.funding_instrument.FundingInstrumentList.as_view(),
         name='funding-instruments-list'),

    path('logged/contact/add', management.contact.ContactsCreateView.as_view(), name='management-contact-add'),
    path('logged/contact/<int:pk>/', management.contact.ContactDetailView.as_view(), name='contact-detail'),
    path('logged/contact/<int:pk>/update', management.contact.ContactUpdateView.as_view(), name='contact-update'),
    path('logged/contacts/', management.contact.ContactsListView.as_view(), name='management-contacts-list'),

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
