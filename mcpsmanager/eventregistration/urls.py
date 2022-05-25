from django.urls import path
from eventregistration.views import *

urlpatterns = [
    path('event/<str:event_slug>', get_event_info),
    path('event/<str:event_slug>/registration', save_registration),
]
