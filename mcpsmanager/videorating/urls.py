from django.urls import path
from videorating.views import *

urlpatterns = [
    path('import', import_participant),
    path('list', get_list),
    path('add_evaluation', add_evaluation),
]
