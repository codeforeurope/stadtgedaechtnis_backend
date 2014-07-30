__author__ = 'jpi'

from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import login, get_user_model
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden

from stadtgedaechtnis_backend.services.serializer.serializers import *
from stadtgedaechtnis_backend.services.authentication.permissions import \
    IsSameUserAsLoggedIn, IsSameSessionAsLoggedIn, IsAuthenticatedOrModerated


class UserView(GenericAPIView):
    """
    Class that handles user creation and updating.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserCreateView(UserView, CreateAPIView):
    """
    View that creates a new user
    """


class UserUpdateView(UserView, UpdateAPIView):
    """
    View that updates a user
    """
    permission_classes = (IsSameUserAsLoggedIn, IsAuthenticatedOrModerated, )


class CreateSessionView(ObtainAuthToken):
    """
    View that is used to obtain a session auth token after successfully logging in.
    """
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            user = serializer.object['user']

            login(request, user)

            request.session["user"] = user.id
            # set login timeout to ten minutes
            request.session.set_expiry(600)
            # save session to obtain a session key
            request.session.save()
            session_id = request.session.session_key
            # print Location header
            headers = {'Location': self.get_absolute_url(request, session_id)}
            return Response({'session_id': session_id}, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    view_name = "stadtgedaechtnis_backend:session-detail"

    def get_absolute_url(self, request, session_id):
        from rest_framework.reverse import reverse

        return reverse(self.view_name, None, {'pk': session_id}, request)


class SessionView(APIView):
    """
    View that handles session retrieving and session destroying.
    """
    permission_classes = (IsSameSessionAsLoggedIn, )

    def get(self, request, *args, **kwargs):
        if "pk" not in kwargs:
            # return 400 Bad Request if not correctly requested
            return HttpResponseBadRequest()
        else:
            session_key = kwargs["pk"]

        from django.conf import settings
        from django.utils.importlib import import_module

        # retrieve session
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore()
        if not session.exists(session_key):
            return HttpResponseBadRequest()

        session = engine.SessionStore(session_key=session_key)
        self.check_object_permissions(request, session)

        if "_auth_user_id" not in session:
            return HttpResponseForbidden()

        # get user ID
        user_id = session["_auth_user_id"]
        # get user
        user = get_user_model().objects.get(pk=user_id)
        serializer = UserSerializer(user)

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if "pk" not in kwargs:
            # return 400 Bad Request if not correctly requested
            return HttpResponseBadRequest()
        else:
            session_key = kwargs["pk"]

        from django.conf import settings
        from django.utils.importlib import import_module
        # retrieve session
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore()
        if not session.exists(session_key):
            return HttpResponseBadRequest()

        session = engine.SessionStore(session_key=session_key)
        self.check_object_permissions(request, session)

        session.flush()

        return Response(status=status.HTTP_204_NO_CONTENT)