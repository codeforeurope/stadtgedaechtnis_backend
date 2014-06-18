__author__ = 'jpi'

from django.conf.urls import patterns, url
from stadtgedaechtnis_backend.services.authentication.views import CreateSessionView, SessionView

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>.+)/$', SessionView.as_view(), name="session-detail"),
    url(r'^$', CreateSessionView.as_view(), name="create-new-session"),
)
