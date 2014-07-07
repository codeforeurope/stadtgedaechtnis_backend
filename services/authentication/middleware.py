__author__ = 'jpi'

from django.conf import settings
from django.utils.importlib import import_module
from rest_framework.authentication import get_authorization_header, SessionAuthentication
from django.http.response import HttpResponseBadRequest
from django.contrib.sessions.middleware import SessionMiddleware


class TokenSessionMiddleware(SessionMiddleware):
    """
    Middleware that processes the sessions similar to the SessionMiddleware of Django.
    """
    def process_request(self, request):
        # redirect to normal SessionMiddleware if the path starts with admin
        if request.path.startswith("/admin/"):
            super(TokenSessionMiddleware, self).process_request(request)
        else:
            engine = import_module(settings.SESSION_ENGINE)
            auth = get_authorization_header(request).split()
            session_key = None

            if len(auth) == 1:
                msg = 'Invalid token header. No credentials provided.'
                return HttpResponseBadRequest(msg)
            elif len(auth) > 2:
                msg = 'Invalid token header. Token string should not contain spaces.'
                return HttpResponseBadRequest(msg)
            elif len(auth) == 2 and auth[0].lower() == b'token':
                session_key = auth[1]

            request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        # redirect to normal SessionMiddleware if the path starts with admin
        if request.path.startswith("/admin/"):
            return super(TokenSessionMiddleware, self).process_response(request, response)
        else:
            # save session if no server error occured
            # that way, users will stay logged in while doing requests.
            if response.status_code != 500:
                request.session.save()

            return response


class TokenSessionAuthentication(SessionAuthentication):
    """
    Class that provides the token authentication method. Works exactly the same way
    as the built-in SessionAuthentication does (since the session is being retrieved
    by the Authorization HTTP header, but provides a Authentication Header.
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        from rest_framework.authentication import exceptions

        _request = request._request
        user = getattr(_request, 'user', None)

        if len(auth) == 2 and auth[0].lower() == b'token' and not user.is_authenticated():
            raise exceptions.AuthenticationFailed('Invalid token')

        return super(TokenSessionAuthentication, self).authenticate(request)

    def authenticate_header(self, request):
        return 'Token'

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        Only feasible when the authentication mode is set to moderation.
        """
        authentication_mode = getattr(settings, 'AUTHENTICATION_MODE', "user_authentication")
        if authentication_mode == "moderation":
            from rest_framework.authentication import CSRFCheck, exceptions

            reason = CSRFCheck().process_view(request, None, (), {})
            if reason:
                # CSRF failed, bail with explicit error message
                raise exceptions.AuthenticationFailed('CSRF Failed: %s' % reason)