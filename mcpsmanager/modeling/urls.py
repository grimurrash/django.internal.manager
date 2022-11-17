from django.urls import path
from modeling.views import *

urlpatterns = [
    path('get_ship_models', get_models),
    path('add_ship_model', add_model),
    path('get_ship_model_types', get_model_types),
    path('get_ship_model_info/<model_id>', get_model_info),
]
