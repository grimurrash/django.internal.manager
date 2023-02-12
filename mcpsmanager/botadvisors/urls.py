from django.urls import path
from botadvisors.views import *

urlpatterns = [
    path("bot_webhook", bot_webhook),
    path("refresh_test_results", refresh_test_results),
    path("send_finish_message", send_finish_message),
    path("send_result_message", send_result_message),
    path("refresh-questions", refresh_questions)
]
