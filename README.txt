stadtgedaechtnis_backend
=========================
This is a Django app that serves stories and historical photographs to locations.
It provides an API 

Installation
------------

This is a non-standalone Django-App. To use it, you must have a standard Django installation.
To use this app with a Django installation, clone this repository into your Django-folder and
add 'stadtgedaechtnis_backend' to INSTALLED_APPS. Then hook up the urlpatterns found in this
repository into your urls.py. Then add the following line to your settings.py:

```
GOOGLE_API_KEY = 'your_google_api_key'
```

The "master" branch works with a SQLite-Database. You can find a version for MSSQL in the "staging-branch".

The following python modules are required to run this software:
- sparqlwrapper
- jsonpickle
- django-apptemplates
- django-mssql (for usage with MSSQL)

For a standard Django-App with both backend and frontend installed and all the necessary settings,
see the following repository::
```
https://github.com/jessepeng/coburg-city-memory
```

API Documentation
-----------------

Will follow later.