__author__ = 'Jan'

from django.conf.urls import patterns, url
from stadtgedaechtnis_backend.services.views.assets import *

urlpatterns = patterns(
    '',
    url(r'^$', AssetList.as_view(), name="all-assets"),
)