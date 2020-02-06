from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.defaults import server_error
from django.views.i18n import JavaScriptCatalog
from .views import common
from .views import external
from .views import logged

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

    path('logged/proposals', logged.proposal.ProposalsList.as_view(), name='logged-proposals-list'),
    path('logged/proposal/<uuid:uuid>/update', logged.proposal.ProposalView.as_view(),
         name='logged-proposal-update'),
    path('logged/proposal/<uuid:uuid>/', logged.proposal.ProposalDetailView.as_view(),
         name='logged-proposal-detail'),
    path('logged/proposal/<uuid:uuid>/eligibility', logged.proposal.ProposalEligibilityUpdate.as_view(),
         name='logged-proposal-eligibility-update'),

    path('logged/proposals/export/excel/<int:call>/', logged.proposal.ProposalsExportExcel.as_view(),
         name='logged-export-proposals-for-call-excel'),
    path('logged/proposals/export/csv/summary/<int:call>/', logged.proposal.ProposalsExportCsvSummary.as_view(),
         name='logged-export-proposals-csv-summary-call'),
    path('logged/proposals/export/csv/summary/', logged.proposal.ProposalsExportCsvSummary.as_view(),
         name='logged-export-proposals-csv-summary-all'),

    path('logged/call/list', logged.call.CallsList.as_view(), name='logged-calls-list'),
    path('logged/call/add/', logged.call.CallView.as_view(), name='call-add'),
    path('logged/call/<int:id>/update', logged.call.CallView.as_view(),
         name='logged-call-update'),
    path('logged/call/<int:id>/', logged.call.CallDetailView.as_view(),
         name='logged-call-detail'),
    path('logged/calls/', logged.call.CallsList.as_view(), name='logged-calls'),
    path('logged/', logged.homepage.Homepage.as_view(), name='logged-homepage'),

    path('logged/template_question/add', logged.template_question.TemplateQuestionCreateView.as_view(),
         name='template-question-add'),
    path('logged/template_question/<int:pk>/', logged.template_question.TemplateQuestionDetailView.as_view(),
         name='template-question-detail'),
    path('logged/template_question/<int:pk>/update',
         logged.template_question.TemplateQuestionUpdateView.as_view(),
         name='template-question-update'),
    path('logged/template_questions/', logged.template_question.TemplateQuestionList.as_view(),
         name='template-questions-list'),

    path('logged/funding_instrument/add', logged.funding_instrument.FundingInstrumentView.as_view(),
         name='funding-instrument-add'),
    path('logged/funding_instrument/<int:pk>/', logged.funding_instrument.FundingInstrumentDetailView.as_view(),
         name='funding-instrument-detail'),
    path('logged/funding_instrument/<int:pk>/update',
         logged.funding_instrument.FundingInstrumentView.as_view(),
         name='funding-instrument-update'),
    path('logged/funding_instruments/', logged.funding_instrument.FundingInstrumentList.as_view(),
         name='funding-instruments-list'),

    path('logged/person_position/add', logged.person_position.PersonPositionCreateView.as_view(), name='logged-person-position-add'),
    path('logged/person_position/<int:pk>/', logged.person_position.PersonPositionDetailView.as_view(), name='person-position-detail'),
    path('logged/person_position/<int:pk>/update', logged.person_position.PersonPositionUpdateView.as_view(), name='person-position-update'),
    path('logged/person_position/', logged.person_position.PersonPositionsListView.as_view(), name='person-position-list'),

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
