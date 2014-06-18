__author__ = 'jpi'

from rest_framework import permissions


class IsSameUserAsLoggedIn(permissions.BasePermission):
    """
    Permission that checks if the currently logged-in user is the same user
    as the one that is to be modified or viewed.
    """
    def has_object_permission(self, request, view, obj):
        session_key_logged_in = request.session.session_key
        session_key_requested = obj.session_key

        return session_key_logged_in == session_key_requested