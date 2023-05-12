from django.urls import path, include
from django.contrib import admin

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1.0/', include('api.urls')),
    path('api/v1.0/', include('chem_detection.urls')),
    path('api/v1.0/', include('compound_information.urls')),
    path('api/v1.0/', include('stoichiometry.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
