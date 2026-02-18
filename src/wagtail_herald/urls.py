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

from wagtail_herald.views import ads_txt, robots_txt

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("ads.txt", ads_txt, name="ads_txt"),
]
