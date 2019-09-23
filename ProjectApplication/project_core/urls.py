from django.urls import path

from .views import Homepage, CallsView, ProposalView

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('calls/', CallsView.as_view(), name='calls-list'),
    path('proposal/add/', ProposalView.as_view(), name='proposal-add'),
    path('proposal/<int:pk>/', ProposalView.as_view(), name='proposal-update'),

]
