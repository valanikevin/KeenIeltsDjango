
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from KeenIeltsDjango import wanderwave

admin.site.site_header = "KeenIELTS Admin"
admin.site.site_title = "KeenIELTS Admin Portal"


urlpatterns = [
    path('wanderwave/', wanderwave.generate_itinerary, name='wanderwave'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
