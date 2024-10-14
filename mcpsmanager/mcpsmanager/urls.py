
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
    path('vesnapobed/', include('vesnapobed.urls')),
    path('answerstoquestions/', include('answerstoquestions.urls')),
    path('eventregistration/', include('eventregistration.urls')),
    path('surveysmanager/', include('surveysmanager.urls')),
    path('modeling/', include('modeling.urls')),
    path('abvisors/', include('botadvisors.urls')),
    path('abvisors-mcvp/', include('botadvisorsmcvp.urls')),
    path('videorationg/', include('videorating.urls'))
] + static(settings.UPLOADS_URL, document_root=settings.UPLOADS_ROOT)
