from django.urls import path
from museumregistration.views import *

urlpatterns = [
    path('registration_limit', registration_limit),
    path('save_registration_member', save_registration_member),
    path('refresh_google_table', refresh_google_table),
]
