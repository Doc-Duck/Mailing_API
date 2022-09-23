from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('mailing_list/', MailListView.as_view()),
    path('mailing_list/<int:pk>/', MailListDetail.as_view()),
    path('client_list/', ClientListView.as_view()),
    path('client_list/<int:pk>/', ClientDetail.as_view()),
    path('mailing_list/stats/<int:ml_id>/', MailingListStats.as_view()),
    path('message/all/<str:status>/', AllMessagesStats.as_view()),
]
