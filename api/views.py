# Create your views here.
import json
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions

import os
from django.conf import settings

from .inorganic_reaction_utils import react

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import UserSerializer, RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework.authtoken.models import Token
# Class based view to Get User Details using Token Authentication

import threading
import base64

from email.message import EmailMessage
import smtplib

import datetime

from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.schemas import ManualSchema
from rest_framework.authtoken.serializers import AuthTokenSerializer

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# custom thread


class ProductsThread(threading.Thread):
    # constructor
    def __init__(self, compounds):
        # execute the base constructor
        threading.Thread.__init__(self)
        # set a default value
        self.products = None
        self.compounds = compounds

    # function executed in a new thread
    def run(self):
        self.products = react(self.compounds)


class CheckIfUserExists(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        email = request

        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserDetailAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            email = request.data['email']
        except KeyError:
            try:
                email=None
                username = request.data['username']
            except KeyError:
                username=None
                return Response({'error': "Required fields were not specified."})

        if email:
            user = User.objects.filter(email=email)
            if user:
                return Response({'user_exists': True})
            else:
                return Response({'user_exists': False})
        elif username:
            user = User.objects.filter(username=username)
            if user:
                return Response({'user_exists': True})
            else:
                return Response({'user_exists': False})



class RegisterUserAPI(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LoginUserAPI(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    renderer_classes = (JSONRenderer,)
    serializer_class = AuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="username",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid username for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        now = datetime.datetime.now()
        user.last_login = str(now)
        user.save()
        return Response({'token': token.key})


class VerifyUserAPI(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    #serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):

        uidb64 = request.data['uid']
        token = request.data['token']

        uidb64_bytes = uidb64.encode('ascii')
        uid_bytes = base64.b64decode(uidb64_bytes)
        uid = uid_bytes.decode('ascii')

        user = User.objects.get(id=int(uid))

        print(uid, token)

        token_generator = PasswordResetTokenGenerator()

        print(user.is_active)

        if not user.is_active:
            if token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response("User verified successfully")
            else:
                return Response("Tokens don't match")
        else:
            return Response("The user is already verified")


class PasswordResetAPI(generics.CreateAPIView):

    def get(self, request, *args, **kwargs):

        def send(user, email_to, token):
            email = EmailMessage()
            email["From"] = settings.EMAIL_HOST_USER
            email["To"] = email_to
            email["Subject"] = "Verificacion de cuenta ALKNOS"

            uid_bytes = str(user.id).encode('ascii')
            uidb64_bytes = base64.b64encode(uid_bytes)
            uidb64 = uidb64_bytes.decode('ascii')

            content = "UIDB64: " + uidb64 + "   TOKEN: " + token

            email.set_content(content)

            smtp = smtplib.SMTP(settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT)
            smtp.starttls()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.sendmail(settings.EMAIL_HOST_USER,
                          email_to, email.as_string())
            smtp.quit()
            print("--- Email has been sent")

        username = request.data['username']
        try:
            user = User.objects.get(username=username)
        except:
            return Response('User does not exist')

        email = user.email

        token_generator = PasswordResetTokenGenerator()

        token_generator = PasswordResetTokenGenerator()
        pwd_reset_token = token_generator.make_token(user)

        print(pwd_reset_token)

        thread = threading.Thread(
            target=send, args=(user, email, pwd_reset_token))
        thread.start()

        return Response('Token has been sent')

    def post(self, request, *args, **kwargs):

        uidb64 = request.data['uid']
        token = request.data['token']

        old_pwd = request.data['old_pwd']
        new_pwd = request.data['new_pwd']

        uidb64_bytes = uidb64.encode('ascii')
        uid_bytes = base64.b64decode(uidb64_bytes)
        uid = uid_bytes.decode('ascii')

        user = User.objects.get(id=int(uid))

        token_generator = PasswordResetTokenGenerator()

        if user.check_password(old_pwd):
            if token_generator.check_token(user, token):
                user.set_password(new_pwd)
                user.save()
                return Response("Password changed successfully")
            else:
                return Response("Tokens don't match")
        else:
            return Response("Incorrect password")


class InorganicReactionAPI(APIView):
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        compounds = request.data['compounds']

        thread = ProductsThread(compounds)
        # start the thread
        thread.start()
        # wait for the thread to finish
        thread.join()
        # report all values returned from a thread
        products = thread.products

        return Response(data=products)
