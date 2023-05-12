from django.urls import path

from .views import ChemDetectionAPI

urlpatterns = [
    path("chem-detection", ChemDetectionAPI.as_view()),
]
