from django.urls import path

from .views import BalanceReactionAPI, CalculateStoichiometryAPI, LimitingReagentAPI, GalvanicCellAPI, EmpiricalFormulaAPI, ElectromagneticWaveAPI


urlpatterns = [
    path("balance-reaction", BalanceReactionAPI.as_view()),
    path("calculate-stoichiometry", CalculateStoichiometryAPI.as_view()),
    path("limiting-reagent", LimitingReagentAPI.as_view()),
    path("galvanic-cell",GalvanicCellAPI.as_view()),
    path("empirical-formula",EmpiricalFormulaAPI.as_view()),
    path("electromagnetic-wave" ,ElectromagneticWaveAPI.as_view()),
]
