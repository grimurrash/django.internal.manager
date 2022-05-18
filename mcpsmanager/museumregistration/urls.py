from django.urls import path
from museumregistration.views import *

urlpatterns = [
    path('museum_registation_limit', museum_registation_limit),
    path('save_museum_registation_member', save_museum_registation_member)
]
