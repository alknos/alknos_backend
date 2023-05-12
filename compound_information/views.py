# Create your views here.
import json
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


response_data = None
# Create your views here.
class CompoundQueryAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print(request)
        query = request.data['query']
        query = query.upper()

        global response_data
        response_data = None

        def get_compounds_by_cid(cids):
            response_data = []
            cids = list(filter(lambda x: x != '', cids))
            request_cids = ','.join(map(str, cids))

            compounds_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{request_cids}/property/MolecularFormula,MolecularWeight,IUPACName/JSON'
            compounds_response = requests.get(compounds_url)
            compounds_data = json.loads(compounds_response.text)
            compounds = compounds_data['PropertyTable']['Properties']

            synonyms_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{request_cids}/synonyms/JSON'
            synonyms_response = requests.get(synonyms_url)
            synonyms_data = json.loads(synonyms_response.text)
            synonyms = synonyms_data['InformationList']['Information']

            for i, compound in enumerate(compounds):
                common_name = synonyms[i]["Synonym"][0]
                response_data.append({"cid": compound['CID'], "common_name":common_name ,"iupac_name" : compound['IUPACName'], "molecular_formula": compound['MolecularFormula'], "molecular_weight": compound['MolecularWeight'], "2d_thumbnail": f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={compound['CID']}&t=s" })

            return response_data

        def get_compounds():
            global response_data
            url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(query)}/cids/TXT?name_type=word'

            response = requests.get(url)

            if response.status_code == 200:
                cids = response.text.split('\n')[:15]
                response_data = get_compounds_by_cid(cids)
            elif response.status_code == 404:
                url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/{urllib.parse.quote(query)}/cids/TXT'
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    print(f"Error {response.status_code} - {response.reason}: {e}")
                    return Response(status=response.status_code)
                cids = response.text.split('\n')[:15]
                response_data = get_compounds_by_cid(cids)
            else:
                print(f"Error {response.status_code} - {response.reason}: {e}")
                return Response(status=response.status_code)
                                
        thread = threading.Thread(target=get_compounds)
        thread.start()
        thread.join()
        return Response(response_data)
    
class CompoundInformationAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        cid = request.data['cid']

        global response_data
        response_data = None

        def get_compound_information_by_cid():
            global response_data
            # URL de la solicitud que devuelve los datos que necesitas
            url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/" + str(cid) + "/JSON/"

            # Realizar la solicitud GET y obtener los datos en formato JSON
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

            chemical_safety_section = None
            names_and_identifiers_section = None
            chemical_and_physical_properties_section = None

            for section in data["Record"]["Section"]:
                if section["TOCHeading"] == "Chemical Safety":
                    chemical_safety_section = section
                elif section["TOCHeading"] == "Names and Identifiers":
                    names_and_identifiers_section = section
                elif section["TOCHeading"] == "Chemical and Physical Properties":
                    chemical_and_physical_properties_section = section

            # get chemical safety data
            chemical_safety_data = []
            chemical_safety_info_dict = None

            try:
                for info_dict in chemical_safety_section["Information"]:
                    if info_dict["Name"] == "Chemical Safety":
                        chemical_safety_info_dict = info_dict
                        break
            except:
                pass

            if chemical_safety_info_dict:
                try:
                    markup_dicts = chemical_safety_info_dict["Value"]["StringWithMarkup"][0]["Markup"]
                    for markup_dict in markup_dicts:
                        url = markup_dict["URL"]
                        extra = markup_dict["Extra"]
                        chemical_safety_data.append({ "name":"Chemical Safety", "url": url, "description":extra })
                except KeyError:
                    chemical_safety_data = []

            # get names and identifiers data
            names_and_identifiers_data = []
            iupac_name_data = None
            molecular_formula_data = None

            for subsection in names_and_identifiers_section["Section"]:
                if subsection["TOCHeading"] == "Computed Descriptors":
                    for desc_section in subsection["Section"]:
                        if desc_section["TOCHeading"] == "IUPAC Name":
                            iupac_name = desc_section["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                            iupac_name_data = {"name": desc_section["TOCHeading"], "value":iupac_name, "description":desc_section["Description"]}
                            names_and_identifiers_data.append(iupac_name_data)
                elif subsection["TOCHeading"] == "Molecular Formula":
                    mol_formula = subsection["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                    molecular_formula_data = {"name": subsection["TOCHeading"], "value":mol_formula}
                    names_and_identifiers_data.append(molecular_formula_data)

            # get chemical and physical properties data
            chemical_and_physical_properties_list = [
                "Physical Description","Color/Form","Odor","Taste", "Boiling Point","Melting Point","Solubility","Density","Vapor Pressure","Viscosity","Corrosivity","Heat of Vaporization","Surface Tension","Refractive Index"
            ]
            chemical_and_physical_properties_data = []

            for subsection in chemical_and_physical_properties_section["Section"]:
                if subsection["TOCHeading"] == "Experimental Properties":
                    for desc_section in subsection["Section"]:
                        if desc_section["TOCHeading"] in chemical_and_physical_properties_list:
                            try:
                                prop = desc_section["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                            except KeyError:
                                prop = desc_section["Information"][0]["Value"]["Number"][0]
                            property_data = {"name": desc_section["TOCHeading"], "value":prop, "description":desc_section["Description"]}
                            chemical_and_physical_properties_data.append(property_data)


            synonyms_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON'
            synonyms_response = requests.get(synonyms_url)
            synonyms_data = json.loads(synonyms_response.text)
            synonyms = synonyms_data['InformationList']['Information'][0]['Synonym'][:5]

            # get compound data
            compound_data = []
            compound_data.append({"name" : "Title", "value": data["Record"]["RecordTitle"]})
            compound_data.append({ "name":"CID", "value": cid})
            compound_data.append({ "name":"2D Thumbnail Structure", "url": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid="+str(cid)+"&t=s" })
            compound_data.append({ "name":"3D Thumbnail Structure", "url": "https://pubchem.ncbi.nlm.nih.gov/image/img3d.cgi?&cid="+str(cid)+"&t=s" })
            compound_data.append({ "name":"2D Structure", "url": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid="+str(cid)+"&t=l" })
            compound_data.append({ "name":"Synonyms", "value": synonyms})

            properties_data = []

            properties_data.extend(compound_data)
            properties_data.extend(chemical_safety_data)
            properties_data.extend(names_and_identifiers_data)
            properties_data.extend(chemical_and_physical_properties_data)

            #response_data = json.dumps(properties_data)
            response_data = properties_data

                                
        thread = threading.Thread(target=get_compound_information_by_cid)
        thread.start()
        thread.join()
        return Response(response_data)
    
