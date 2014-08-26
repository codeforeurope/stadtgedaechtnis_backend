__author__ = 'jpi'

from django.conf.urls import patterns, url

from stadtgedaechtnis_backend.import_entries.views import *

from stadtgedaechtnis_backend import admin

JSON_URL = "http://www.stadtgeschichte-coburg.de/portaldata/1/Resources/\
_internal/data/json/dsg_coburg_fraunhofer_focus.js"

urlpatterns = patterns('',
    url(r'^simple-json/$', admin.site.admin_view(SimpleJSONImport.as_view(source=JSON_URL,)),
        name="simple-json"),
    url(r'^import-entry/(?P<id>\d+)/(?P<location>\d+)/$', ImportEntry.as_view(
            source=JSON_URL
        ),
        name="import-entry"),
)