from django.urls import path

from .views import CompoundQueryAPI, CompoundInformationAPI


urlpatterns = [
    path("compound-query", CompoundQueryAPI.as_view()),
    path("compound-information", CompoundInformationAPI.as_view()),
]
