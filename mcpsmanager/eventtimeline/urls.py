from django.urls import path
from eventtimeline.views import *

urlpatterns = [
    path('events', get_all_events)
]
