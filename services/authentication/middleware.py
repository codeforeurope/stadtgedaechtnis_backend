__author__ = 'jpi'

from django.conf import settings
from django.utils.importlib import import_module
from rest_framework.authentication import get_authorization_header, SessionAuthentication
from django.http.response import HttpResponseBadRequest


class TokenSessionMiddleware(object):
    """
    Middleware that processes the sessions similar to the SessionMiddleware of Django.
    """
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        auth = get_authorization_header(request).split()
        session_key = None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            return HttpResponseBadRequest(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            return HttpResponseBadRequest(msg)
        elif len(auth) == 2:
            session_key = auth[1]

        request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        try:
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                # Save the session data and refresh the client cookie.
                # Skip session save for 500 responses, refs #3881.
                if response.status_code != 500:
                    request.session.save()
        return response


class TokenSessionAuthentication(SessionAuthentication):
    """
    Class that provides the token authentication method. Works exactly the same way
    as the built-in SessionAuthentication does (since the session is being retrieved
    by the Authorization HTTP header, but provides a Authentication Header.
    """

    def authenticate_header(self, request):
        return 'Token'

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        Only feasible when the authentication mode is set to moderation.
        """
        if settings.AUTHENTICATION_MODE == "moderation":
            from rest_framework.authentication import CSRFCheck, exceptions

            reason = CSRFCheck().process_view(request, None, (), {})
            if reason:
                # CSRF failed, bail with explicit error message
                raise exceptions.AuthenticationFailed('CSRF Failed: %s' % reason)