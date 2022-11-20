from django.urls import path
from botadvisors.views import bot_webhook, start_test, refresh_questions

urlpatterns = [
    path("bot_webhook", bot_webhook),
    path("test", start_test),
    path("refresh-questions", refresh_questions)
]
