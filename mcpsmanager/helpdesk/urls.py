from django.urls import path

from .views import *

urlpatterns = [
    path('request/new/<int:row_number>', new_request),
    path('request/accept/<int:row_number>', accept_request),
    path('request/done/<int:row_number>', done_request),
    path('report/reminder', reminder),
]
