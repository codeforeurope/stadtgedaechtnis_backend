__author__ = 'jpi'

from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView
from django.contrib.auth.models import User
from stadtgedaechtnis_backend.serializers import UserSerizalier


class UserView(GenericAPIView):
    """
    Class that handles user creation and updating.
    """
    queryset = User.objects.all()
    serializer_class = UserSerizalier


class UserCreateView(UserView, CreateAPIView):
    """
    View that creates a new user
    """


class UserUpdateView(UserView, UpdateAPIView):
    """
    View that updates a user
    """