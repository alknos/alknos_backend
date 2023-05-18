# Create your views here.
import json
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import authentication, permissions

import threading
import requests
import urllib.request

from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.authtoken.models import Token

from chemlib import Reaction, Galvanic_Cell, Wave
from chemlib import empirical_formula_by_percent_comp as efbpc
import base64
import io

from .utils import convert_equation

# Create your views here.
class BalanceReactionAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):        
        reaction = Reaction.by_formula(request.data['reaction'])
        reaction.balance()
        reaction_formula = convert_equation(str(reaction))
        return Response({"reaction": str(reaction_formula)})

class CalculateStoichiometryAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        reaction = Reaction.by_formula(request.data['reaction'])
        stoichiometry_unit = request.data['unit']
        stoichiometry_value = int(request.data['quantity'])
        compound_position = int(request.data['position'])

        if (stoichiometry_unit=='moles'):
            stoichiometry_reaction = reaction.get_amounts(compound_position, moles=stoichiometry_value)
        elif (stoichiometry_unit=='grams'):
            stoichiometry_reaction = reaction.get_amounts(compound_position, grams=stoichiometry_value)
        elif (stoichiometry_unit=='molecules'):
            stoichiometry_reaction = reaction.get_amounts(compound_position, molecules=stoichiometry_value)

        raw_reaction = request.data['reaction']
        raw_reaction = raw_reaction.replace("+","")
        raw_reaction = raw_reaction.replace("-->","")
        print(raw_reaction)
        reaction_compounds = raw_reaction.split("  ")

        for i in range(len(stoichiometry_reaction)):
            stoichiometry_reaction[i].update({'compound': reaction_compounds[i]})

        print(stoichiometry_reaction)

        return Response(stoichiometry_reaction)

class LimitingReagentAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        reaction = Reaction.by_formula(request.data['reaction'])
        stoichiometry_unit = request.data['unit']
        reactant2_value = float(request.data['reagent2'])
        reactant1_value = float(request.data['reagent1'])

        limiting_reagent=reaction.limiting_reagent(reactant1_value, reactant2_value, mode = stoichiometry_unit)

        return Response({"limiting_reagent": limiting_reagent})
    
class GalvanicCellAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        electrode1 = request.data['electrode1']
        electrode2 = request.data['electrode2']
        g = Galvanic_Cell(electrode1, electrode2)
        g.draw()
        galvanic_image = g.diagram

        image_buffer = io.BytesIO()
        galvanic_image.save(image_buffer, format='png')
        galvanic_bytes = image_buffer.getvalue()
        galvanic_base64 = base64.b64encode(galvanic_bytes).decode('utf-8')

        return Response({"base64": str(galvanic_base64)})

class EmpiricalFormulaAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        elements = request.data['elements']
        
        params_dict = {}
        for element in elements:
            params_dict[element['symbol']] = element['percentage']
        
        empirical_formula =  convert_equation(efbpc(**params_dict).formula)

        return Response({"empirical_formula": empirical_formula})

class ElectromagneticWaveAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, args, **kwargs):
        print(request.data)
        value = float(request.data['value'])
        prop = request.data['property']
        power = float(request.data['power'])
        real_value = float(value * (10 ** power))
        if (prop == "frequency"):
            w = Wave(frequency= real_value)

        elif (prop == 'wavelength'):
            w = Wave(wavelength=real_value)

        elif (prop == 'energy'):
            w = Wave(energy=real_value)

        return Response(w.properties)