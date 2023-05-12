from django.urls import path

from rest_framework.authtoken import views
from .views import UserDetailAPI, RegisterUserAPI, InorganicReactionAPI,VerifyUserAPI,LoginUserAPI,PasswordResetAPI


urlpatterns = [
    # reactions
    path("inorganic-reaction", InorganicReactionAPI.as_view()),
    path("get-details", UserDetailAPI.as_view()),
    path('register', RegisterUserAPI.as_view()),
    path('login', LoginUserAPI.as_view()),
    path('verify', VerifyUserAPI.as_view()),
    path('reset', PasswordResetAPI.as_view()),
]
