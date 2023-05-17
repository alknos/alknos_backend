from django.urls import path

from .views import BalanceReactionAPI, CalculateStoichiometryAPI, CalculateReactantAPI, GalvanicCellAPI


urlpatterns = [
    path("balance-reaction", BalanceReactionAPI.as_view()),
    path("calculate-stoichiometry", CalculateStoichiometryAPI.as_view()),
    path("calculate-reactant", CalculateReactantAPI.as_view()),
    path("galvanic-cell",GalvanicCellAPI.as_view()),
]
