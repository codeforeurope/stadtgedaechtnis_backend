"""
Created on 26.02.2014

@author: jpi
"""

from django.conf.urls import patterns, url, include

urlpatterns = patterns(
   '',
   url(r'^services/', include('stadtgedaechtnis_backend.services.urls')),
   )