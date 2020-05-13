from django.urls import path

import grant_management.views

urlpatterns = [
    path('logged/grant-management/project/list/',
         grant_management.views.ProjectList.as_view(),
         name='logged-grant_management-project-list'),
    path('logged/grant-management/project/<int:pk>/',
         grant_management.views.ProjectDetail.as_view(),
         name='logged-grant_management-project-detail'),
    path('logged/grant-management/project/<int:pk>/update/',
         grant_management.views.ProjectUpdate.as_view(),
         name='logged-grant_management-project-update'),

    path('logged/grant-management/project/<int:pk>/information/update/',
         grant_management.views.ProjectBasicInformationUpdateView.as_view(),
         name='logged-grant_management-project-basic-information-update'),
    path('logged/grant-management/project/<int:project>/lay_summaries/update/',
         grant_management.views.LaySummariesUpdateView.as_view(),
         name='logged-grant_management-lay_summaries-update'),
    path('logged/grant-management/project/<int:project>/blog_posts/update/',
         grant_management.views.BlogPostsUpdateView.as_view(),
         name='logged-grant_management-blog_posts-update'),
    path('logged/grant-management/project/<int:project>/scientific_reports/update/',
         grant_management.views.ScientificReportsUpdateView.as_view(),
         name='logged-grant_management-scientific_reports-update'),

    path('logged/grant-management/project/<int:project>/grant-agreement/add/',
         grant_management.views.GrantAgreementAddView.as_view(),
         name='logged-grant_management-grant_agreement-add'),
    path('logged/grant-management/grant-agreement/<int:pk>/update/',
         grant_management.views.GrantAgreementUpdateView.as_view(),
         name='logged-grant_management-grant_agreement-update'),

    path('logged/grant-management/project/<int:project>/finances/update/',
         grant_management.views.FinancesViewUpdate.as_view(),
         name='logged-grant_management-finances-update'),

    path('logged/grant-management/project/<int:project>/installments/update/',
         grant_management.views.InstallmentsUpdateView.as_view(),
         name='logged-grant_management-installments-update'),

    path('logged/grant-management/project/<int:project>/media/update/',
         grant_management.views.MediaUpdateView.as_view(),
         name='logged-grant_management-media-update'),

    path('logged/grant-management/project/<int:project>/data/update/',
         grant_management.views.DatasetUpdateView.as_view(),
         name='logged-grant_management-data-update'),

    path('lay-summaries/<int:call>/raw/',
         grant_management.views.LaySummariesRaw.as_view(),
         name='lay-summaries-raw'),

]
