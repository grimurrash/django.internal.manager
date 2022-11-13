from django.urls import path
from surveysmanager.views import *

urlpatterns = [
    path('survey/<str:url>', get_info),
    path('survey/<str:url>/answer', save_result),
]
