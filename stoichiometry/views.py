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

from chemlib import Reaction, Galvanic_Cell

# Create your views here.
class BalanceReactionAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response_data = None
        reaction = Reaction.by_formula(request.data['reaction'])
        reaction.balance()
        response_data = [str(reaction)]
            
        return Response({"reaction": response_data})

class CalculateStoichiometryAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)
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

        return Response(stoichiometry_reaction)

class CalculateReactantAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)
        reaction = Reaction.by_formula(request.data['reaction'])
        stoichiometry_unit = request.data['unit']
        reactant2_value = float(request.data['reagent2'])
        reactant1_value = float(request.data['reagent1'])

        lr=reaction.limiting_reagent(reactant1_value, reactant2_value, mode = stoichiometry_unit)

        return Response({"limiting_reagent": str(lr)})
    
class GalvanicCellAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request.data)
        electrode1 = request.data['electrode1']
        electrode2 = request.data['electrode2']
        g = Galvanic_Cell(electrode1, electrode2)
        g.draw()
        galvanic_image = g.diagram
        print(galvanic_image)
        galvanic_bytes = galvanic_image.tobytes()
        response = HttpResponse(content=galvanic_bytes, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="galvanic_cell_'+electrode1+'_'+electrode2+'.png"'

        return response