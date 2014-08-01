__author__ = 'jpi'

import hashlib

from rest_framework.fields import Field, BooleanField
from django.conf import settings


class UniqueIDField(Field):
    """
    Field that provides a unique ID that can be used to identify this object.
    """
    read_only = True

    def field_to_native(self, obj, field_name):
        return create_secret_signature(obj)


class IgnoreValueBooleanField(BooleanField):
    """
    Field that ignores the actual value and sets it to a default value
    """

    def from_native(self, value):
        return self.default


def create_secret_signature(obj):
    """
    Creates a secret signature for a given object.
    :param obj:
    :return:
    """
    app_secret_key = settings.SECRET_KEY
    representation = repr(obj) + app_secret_key
    return hashlib.sha1(representation).hexdigest()