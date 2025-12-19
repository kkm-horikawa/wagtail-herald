"""
URL configuration for wagtail-herald.

Usage in your project's urls.py:
    from django.urls import include, path

    urlpatterns = [
        path('', include('wagtail_herald.urls')),
        # ...
    ]
"""

from django.urls import path

from wagtail_herald.views import robots_txt

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
]
