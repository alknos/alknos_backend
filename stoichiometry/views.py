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

from chemlib import Reaction, Galvanic_Cell, Wave, pH, electrolysis, Element, Compound
from chemlib import empirical_formula_by_percent_comp as efbpc
import base64
import io

import itertools
import copy

from .utils import convert_equation, oxidation_numbers

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
        reaction_compounds = raw_reaction.split("  ")

        for i in range(len(stoichiometry_reaction)):
            stoichiometry_reaction[i].update({'compound': convert_equation(reaction_compounds[i])})

        print(stoichiometry_reaction)

        return Response(stoichiometry_reaction)

class LimitingReagentAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        reaction = Reaction.by_formula(request.data['reaction'])
        reaction.balance()
        stoichiometry_unit = request.data['unit']
        reactant1_value = float(request.data['reagent1'])
        reactant2_value = float(request.data['reagent2'])

        limiting_reagent = convert_equation(reaction.limiting_reagent(reactant1_value, reactant2_value, mode = stoichiometry_unit).formula)

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
        
        empirical_formula = convert_equation(efbpc(**params_dict).formula)

        return Response({"empirical_formula": empirical_formula})

class ElectromagneticWaveAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)
        value = float(request.data['value'])
        prop = request.data['property']
        power = float(request.data['power'])
        real_value = float(value * (10 ** power))
        if (prop == "frequency"):
            wave = Wave(frequency= real_value)

        elif (prop == 'wavelength'):
            wave = Wave(wavelength=real_value)

        elif (prop == 'energy'):
            wave = Wave(energy=real_value)

        return Response(wave.properties)

class AcidityCalculationAPI(APIView): 
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)
        prop = request.data['property']
        value = float(request.data['value'])
        if (prop == "pH"):
           acidity = pH(pH = value)

        elif (prop == 'pOH'):
            acidity = pH(pOH=value)

        elif (prop == 'H'):
            power = float(request.data['power'])
            real_value = float(value * (10 ** power))
            acidity = pH(H=real_value)

        elif (prop == 'OH'):
            power = float(request.data['power'])
            real_value = float(value * (10 ** power))
            acidity = pH(OH=real_value)

        return Response(acidity)
    
class CalculateElectrolysisAPI(APIView): 
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        compound = request.data['compound']
        amps = None
        seconds = None
        grams = None

        try:
            amps = request.data['amps']
        except:
            pass

        try:
            seconds = float(request.data['seconds'])
        except:
            pass

        try:
            grams = float(request.data["grams"])
        except:
            pass

        ##############################################################
        occurences = Compound(compound).occurences

        # Creamos una copia profunda de oxidation_numbers
        oxidation_numbers_copy = copy.deepcopy(oxidation_numbers)

        # Convertimos los valores en lista o array
        for key, value in oxidation_numbers_copy.items():
            if not isinstance(value, list):
                oxidation_numbers_copy[key] = [value]

        # Generamos el array
        array = []
        for element, occurence in occurences.items():
            subarray = []
            for oxidation in oxidation_numbers_copy[element]:
                subarray.append(oxidation * occurence)
            array.append(subarray)

        compound_oxidation_numbers = dict()
        oxidation_numbers_combination = None

        # Buscamos las combinaciones que sumen cero
        combinations = list(itertools.product(*array))
        for combination in combinations:
            if sum(combination) == 0:
                oxidation_numbers_combination = combination
                break

        # Almacenamos los valores de oxidacion de los elementos en compound_oxidation_numbers
        for index, element in enumerate(occurences):
            compound_oxidation_numbers[element] = int(oxidation_numbers_combination[index] / occurences[element]) if occurences[element] != 0 else 0

        n = 0
        metal = None
        for element, value in compound_oxidation_numbers.items():
            # Evaluamos si el elemento es metal o no
            if Element(element).properties['Metal']:
                n = value
                metal = element
                break


        if amps == None:
            electrolysis_result = electrolysis(metal, n, grams = grams, seconds=seconds)
        if seconds == None:
            electrolysis_result = electrolysis(metal, n, grams = grams, amps=amps)
        if grams == None:
            electrolysis_result = electrolysis(metal, n, amps = amps, seconds=seconds)


        return Response(electrolysis_result)
