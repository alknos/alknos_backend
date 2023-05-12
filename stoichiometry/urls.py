from django.urls import path

from .views import BalanceReactionAPI, CalculateStoichiometryAPI 


urlpatterns = [
    path("balance-reaction", BalanceReactionAPI.as_view()),
    path("calculate-stoichiometry", CalculateStoichiometryAPI.as_view()),
]
