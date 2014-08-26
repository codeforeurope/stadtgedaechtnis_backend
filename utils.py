__author__ = 'jpi'

import re
from stadtgedaechtnis_backend.models import Location
from decimal import Decimal


def replace_multiple(text, dictionary):
    """
    Replaces different words in a string using a dictionary.
    """
    # escape for regular expressions
    dictionary = dict((re.escape(key), value) for key, value in dictionary.iteritems())
    # compile joint pattern
    pattern = re.compile("|".join(dictionary.keys()))
    # replace all the keys with the values
    text = pattern.sub(lambda m: dictionary[re.escape(m.group(0))], text)
    return text


def get_nearby_locations(lat, lon, max_lat=0, max_lon=0, stories_only=False):
    """
    Gets near Locations to given geolocations
    """
    if max_lat == 0:
        min_lat, max_lat = Decimal(lat) - Decimal(0.01), Decimal(lat) + Decimal(0.01)
    else:
        min_lat = Decimal(lat)

    if max_lon == 0:
        min_lon, max_lon = Decimal(lon) - Decimal(0.01), Decimal(lon) + Decimal(0.01)
    else:
        min_lon = Decimal(lon)

    if stories_only:
        locations = Location.objects.filter(latitude__gte=min_lat,
                                            latitude__lte=max_lat,
                                            longitude__gte=min_lon,
                                            longitude__lte=max_lon,
                                            stories__isnull=False, stories__temporary__exact=False).distinct()
    else:
        locations = Location.objects.filter(latitude__gte=min_lat,
                                            latitude__lte=max_lat,
                                            longitude__gte=min_lon,
                                            longitude__lte=max_lon)

    return locations
