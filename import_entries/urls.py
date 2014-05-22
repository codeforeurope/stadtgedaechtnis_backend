__author__ = 'jpi'

from django.conf.urls import patterns, url

from stadtgedaechtnis_backend.import_entries.views import *

from stadtgedaechtnis_backend import admin

JSON_URL = "http://www.stadtgeschichte-coburg.de/portaldata/1/Resources/_internal/data/json/dsg_coburg.js"

urlpatterns = patterns('',
    url(r'^simple-json/$', admin.site.admin_view(SimpleJSONImport.as_view(
            source=JSON_URL,
            interactive=True,)),
        name="simple-json"),
    url(r'^simple-json-silent/$', SimpleJSONImport.as_view(
            source=JSON_URL,
            interactive=False,
            redirect=True,
            redirect_to="/admin/"),
        name="simple-json-silent"),
    url(r'^import-entry/(?P<id>\d+)/(?P<location>\d+)/$', ImportEntry.as_view(
            source=JSON_URL
        ),
        name="import-entry"),
)