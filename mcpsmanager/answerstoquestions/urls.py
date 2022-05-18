from django.urls import path
from answerstoquestions.views import *

urlpatterns = [
    path('question/create', create_question),
    path('question/<int:question_id>', get_question),
    path('question/<int:question_id>/update', update_question),
]
