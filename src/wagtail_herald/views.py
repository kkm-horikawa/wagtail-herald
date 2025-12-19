"""
Views for wagtail-herald.
"""

from django.http import HttpRequest, HttpResponse
from wagtail.models import Site

from wagtail_herald.models import SEOSettings


def get_default_robots_txt(request: HttpRequest) -> str:
    """Generate default robots.txt content.

    Args:
        request: The HTTP request object.

    Returns:
        Default robots.txt content with sitemap URL.
    """
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
    ]

    # Add sitemap URL
    try:
        sitemap_url = request.build_absolute_uri("/sitemap.xml")
        lines.append(f"Sitemap: {sitemap_url}")
    except Exception:
        pass

    return "\n".join(lines)


def robots_txt(request: HttpRequest) -> HttpResponse:
    """Serve robots.txt for the current site.

    Returns custom content from SEOSettings if configured,
    otherwise returns a sensible default.

    Usage in urls.py:
        from wagtail_herald.views import robots_txt

        urlpatterns = [
            path('robots.txt', robots_txt, name='robots_txt'),
            # ...
        ]

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse with text/plain content type.
    """
    site = Site.find_for_request(request)
    content = ""

    if site:
        try:
            seo_settings = SEOSettings.for_request(request)
            if seo_settings and seo_settings.robots_txt:
                content = seo_settings.robots_txt
        except Exception:
            pass

    if not content:
        content = get_default_robots_txt(request)

    return HttpResponse(content, content_type="text/plain")
