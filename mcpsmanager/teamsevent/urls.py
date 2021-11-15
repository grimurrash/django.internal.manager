from django.urls import path
from . import views

urlpatterns = [
    path('create_microsoft_user', views.create_microsoft_user),
    path('delete_microsoft_user', views.delete_microsoft_user),
    path('send_mails', views.send_mails),
    path('send_mail', views.send_mail),
    path('get_member', views.get_member)
]
