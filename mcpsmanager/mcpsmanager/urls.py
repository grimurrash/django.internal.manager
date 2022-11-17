"""mcpsmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('eventtimeline/', include('eventtimeline.urls')),
    path('helpdesk/', include('helpdesk.urls')),
    path('teamsevent/', include('teamsevent.urls')),
    path('botcollection/', include('botcollection.urls')),
    path('museumregistration/', include('museumregistration.urls')),
    path('answerstoquestions/', include('answerstoquestions.urls')),
    path('eventregistration/', include('eventregistration.urls')),
    path('surveysmanager/', include('surveysmanager.urls')),
    path('modeling/', include('modeling.urls'))
] + static(settings.UPLOADS_URL, document_root=settings.UPLOADS_ROOT)
