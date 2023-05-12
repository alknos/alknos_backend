# Create your views here.
import json
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import authentication, permissions

import base64
import re

import cv2
import numpy as np

import os
from django.conf import settings 

import cirpy
import pubchempy as pcp
from img2mol.inference import *

import threading

from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.authtoken.models import Token

# Class based view to Get User Details using Token Authentication

img2mol_instance = None
smiles = None

cont = 1

# Create your views here.
class ChemDetectionAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get(self, request, *args, **kwargs):
        
        data = "Model loading!"

        def start_inference_model():
            try:
                print("--- Starting inference model...")
                global img2mol_instance
                img2mol_instance = Img2MolInference(model_ckpt="../../model/model.ckpt",
                                    local_cddd=True)
                print("--- Model started")
            except:
                print("An error has ocurred")
                
        thread = threading.Thread(target=start_inference_model)
        thread.start()

        return Response(data)

    def post(self, request, *args, **kwargs):

        global cont
        cont += 1

        file_base64 = request.data['base64']
        file_base64 = re.sub(r'^.*?base64,', '', file_base64)

        print(file_base64)

        path = str(cont) + ".png"

        decoded_data = base64.b64decode(file_base64)
        np_data = np.fromstring(decoded_data, np.uint8)
        imagen = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)

        cv2.imwrite(path,imagen)

        def predict():
            global smiles
            res = img2mol_instance(path)
            smiles = res["smiles"]

        thread = threading.Thread(target=predict)
        thread.start()

        print("--- Detection started")

        thread.join()
        print("--- Detection finished")

        os.remove(path)

        print(" => ", smiles)
        print("--- Getting IUPAC name")

        compound = pcp.get_compounds(smiles, 'smiles')
        compound = compound[0]
        iupac_name = compound.iupac_name

        print(" => ", iupac_name)

        print("--- Getting possible common names")
        possible_common_names = []

       
        possible_common_names.append(compound.synonyms[:3])

        mol2_path = os.path.join(settings.MEDIA_ROOT + "/file.mol2")

        if os.path.exists(mol2_path):
            os.remove(mol2_path)  

        print("--- Writing file.mol2")

        with open(mol2_path, 'wb') as infile:
            mol2 = cirpy.resolve(smiles, 'mol2')
            infile.write(bytes(mol2, 'utf-8'))
            infile.close()

        print("--- Finished")

        return Response({"smiles": smiles, "iupac_name": iupac_name, "possible_common_name": possible_common_names})