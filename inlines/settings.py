"""
These settings should not be edited directly.
Instead, overwrite them in the main project's setting file.
"""
from django.conf import settings

# Specify the keys that should be used to lookup objects.
INLINES_LOOKUP_KEYS = getattr(settings, 'INLINES_LOOKUP_KEYS', ['id'])
INLINES_DEBUG = getattr(settings, 'INLINES_DEBUG', settings.DEBUG)
INLINES_CACHE_TIMEOUT = getattr(settings, 'INLINES_CACHE_TIMEOUT', 0)
INLINES_ALLOWED_TYPES = getattr(settings, 'INLINES_ALLOWED_TYPES', None)
INLINES_MANAGERS = getattr(settings, 'INLINES_MANAGERS', None)
