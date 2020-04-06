from django.urls import path

import grant_management.views

urlpatterns = [
    path('logged/grant-management/project_list/',
         grant_management.views.ProjectList.as_view(),
         name='logged-grant_management-project-list'),
]
