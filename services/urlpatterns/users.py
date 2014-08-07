__author__ = 'jpi'

from django.conf.urls import patterns, url
from stadtgedaechtnis_backend.services.authentication.views import UserCreateView, UserUpdateView, UserSearchView

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$', UserUpdateView.as_view(), name="user-detail"),
    url(r'^$', UserCreateView.as_view(), name="create-new-user"),
    url(r'^name/(?P<query>[^/]+)/$', UserSearchView.as_view(), name="search-user"),
)