"""
URL configuration for tests.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("wagtail_herald.urls")),
]
