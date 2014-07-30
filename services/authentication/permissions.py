__author__ = 'jpi'

from rest_framework import permissions
from django.conf import settings
from rest_framework.permissions import SAFE_METHODS
from stadtgedaechtnis_backend.services.serializer.fields import create_secret_signature


class IsSameSessionAsLoggedIn(permissions.BasePermission):
    """
    Permission that checks if the currently logged-in user is the same user
    as the one that is to be modified or viewed.
    """
    def has_object_permission(self, request, view, obj):
        session_key_logged_in = request.session.session_key
        session_key_requested = obj.session_key

        return session_key_logged_in == session_key_requested


class IsSameUserAsLoggedIn(permissions.BasePermission):
    """
    Permission that checks if the currently logged-in user is the same user
    as the one that is to be modified or viewed.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsAuthenticatedOrModerated(permissions.IsAuthenticated):
    """
    Permission that checks the authentication mode.
    If user_authentication is active, the normal authentication
    scheme will be used. Otherwise, the CSRF-mechanism is used.
    """
    def has_permission(self, request, view):
        authentication_mode = getattr(settings, 'AUTHENTICATION_MODE', "user_authentication")
        if authentication_mode == "moderation":
            from rest_framework.authentication import CSRFCheck

            reason = CSRFCheck().process_view(request, None, (), {})
            return not reason
        else:
            return super(IsAuthenticatedOrModerated, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        try:
            unique_id = request.DATA["unique_id"]
            return create_secret_signature(obj) == unique_id
        except KeyError:
            return False


class IsAuthenticatedOrReadOnlyOrModerated(IsAuthenticatedOrModerated):
    """
    Permission that first checks if the request method is safe. If so, accept,
    otherwise use IsAuthenticatedOrModerated to determine the permission.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or \
            super(IsAuthenticatedOrReadOnlyOrModerated, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or \
            super(IsAuthenticatedOrReadOnlyOrModerated, self).has_object_permission(request, view, obj)