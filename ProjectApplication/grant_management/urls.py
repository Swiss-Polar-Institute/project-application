from django.urls import path

import grant_management.views

urlpatterns = [
    path('logged/grant-management/project/list/',
         grant_management.views.ProjectList.as_view(),
         name='logged-grant_management-project-list'),
    path('logged/grant-management/project/<int:pk>/',
         grant_management.views.ProjectDetail.as_view(),
         name='logged-grant_management-project-detail'),

    path('logged/grant-management/project/<int:pk>/information/update/',
         grant_management.views.ProjectBasicInformationUpdateView.as_view(),
         name='logged-grant_management-project-update'),
    path('logged/grant-management/project/<int:project>/grant-agreement/add/',
         grant_management.views.GrantAgreementAddView.as_view(),
         name='logged-grant_management-grant_agreement-add')
]