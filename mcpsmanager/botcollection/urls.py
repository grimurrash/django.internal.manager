from django.urls import path
from botcollection.views import survey_bot_webhook

urlpatterns = [
    path('surveybotwebhook', survey_bot_webhook)
]
