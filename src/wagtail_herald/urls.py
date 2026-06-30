"""
URL configuration for wagtail-herald.

Usage in your project's urls.py:
    from django.urls import include, path

    urlpatterns = [
        path('', include('wagtail_herald.urls')),
        # ...
    ]
"""

from django.urls import path, re_path

from wagtail_herald.views import (
    ads_txt,
    apple_touch_icon,
    favicon,
    favicon_svg,
    indexnow_key_file,
    robots_txt,
    security_txt,
)

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("ads.txt", ads_txt, name="ads_txt"),
    path(".well-known/security.txt", security_txt, name="security_txt"),
    # ファビコンを恒久ルートパスで配信（地球儀化対策）
    path("favicon.ico", favicon, name="favicon"),
    path("favicon.svg", favicon_svg, name="favicon_svg"),
    path("apple-touch-icon.png", apple_touch_icon, name="apple_touch_icon"),
    re_path(
        r"^(?P<key>[a-zA-Z0-9\-]{8,128})\.txt$",
        indexnow_key_file,
        name="indexnow_key_file",
    ),
]
