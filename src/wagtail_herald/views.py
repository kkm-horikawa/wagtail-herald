"""
Views for wagtail-herald.
"""

import mimetypes

from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from wagtail.models import Site

from wagtail_herald.models import SEOSettings

# ファビコンは中身が変わらないため 1 年・immutable でキャッシュさせる
FAVICON_CACHE_CONTROL = "public, max-age=31536000, immutable"


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


def ads_txt(request: HttpRequest) -> HttpResponse:
    """Serve ads.txt for the current site.

    Returns ads.txt content from SEOSettings if configured,
    otherwise raises Http404.

    Usage in urls.py:
        from wagtail_herald.views import ads_txt

        urlpatterns = [
            path('ads.txt', ads_txt, name='ads_txt'),
            # ...
        ]

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse with text/plain content type.

    Raises:
        Http404: If no ads.txt content is configured.
    """
    site = Site.find_for_request(request)

    if site:
        seo_settings = SEOSettings.for_request(request)
        if seo_settings and seo_settings.ads_txt:
            return HttpResponse(seo_settings.ads_txt, content_type="text/plain")

    raise Http404


def security_txt(request: HttpRequest) -> HttpResponse:
    """Serve security.txt for the current site.

    Serves ``/.well-known/security.txt`` as defined in RFC 9116.
    Returns content from SEOSettings if configured, otherwise raises Http404
    (no sensible default exists because Contact is a required field).

    Usage in urls.py:
        from wagtail_herald.views import security_txt

        urlpatterns = [
            path('.well-known/security.txt', security_txt, name='security_txt'),
            # ...
        ]

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse with text/plain content type.

    Raises:
        Http404: If no security.txt content is configured.
    """
    site = Site.find_for_request(request)

    if site:
        seo_settings = SEOSettings.for_request(request)
        if seo_settings and seo_settings.security_txt:
            return HttpResponse(seo_settings.security_txt, content_type="text/plain")

    raise Http404


def indexnow_key_file(request: HttpRequest, key: str) -> HttpResponse:
    """Serve IndexNow key verification file.

    IndexNow requires a ``/{api_key}.txt`` endpoint that returns the key
    as plain text to prove domain ownership.

    Args:
        request: The HTTP request object.
        key: The key from the URL path (without .txt extension).

    Returns:
        HttpResponse with text/plain content type.

    Raises:
        Http404: If IndexNow is not configured or key does not match.
    """
    site = Site.find_for_request(request)

    if site:
        seo_settings = SEOSettings.for_request(request)
        if seo_settings and seo_settings.indexnow_api_key == key:
            return HttpResponse(key, content_type="text/plain")

    raise Http404


def _serve_favicon(
    request: HttpRequest, field_name: str, default_content_type: str
) -> FileResponse:
    """Serve a configured favicon image from a stable root path.

    Google のファビコン取得は ``/favicon.ico`` などのルートを必ず探し、リトライにも
    寛容ではない。404 や取得失敗が一度でもあると検索結果のファビコンが地球儀に戻る。
    そこで設定済みのファビコン画像を恒久ルートパスで・長期キャッシュ付きで返す。

    CMS のメディア URL（再アップロードで変わる・エッジから消えやすい）に依存させず、
    この herald 所有の URL を不変の入口にすることで地球儀化を防ぐ。

    Args:
        request: The HTTP request object.
        field_name: SEOSettings の画像フィールド名（favicon_png など）。
        default_content_type: 拡張子から判定できなかった場合の Content-Type。

    Returns:
        FileResponse with a long-lived Cache-Control header.

    Raises:
        Http404: If no image is configured for the current site.
    """
    site = Site.find_for_request(request)

    if site:
        seo_settings = SEOSettings.for_request(request)
        image = getattr(seo_settings, field_name, None) if seo_settings else None
        if image:
            content_type = (
                mimetypes.guess_type(image.file.name)[0] or default_content_type
            )
            response = FileResponse(image.file.open("rb"), content_type=content_type)
            response["Cache-Control"] = FAVICON_CACHE_CONTROL
            return response

    raise Http404


def favicon(request: HttpRequest) -> FileResponse:
    """Serve ``/favicon.ico`` from the configured PNG favicon.

    ブラウザと Google が暗黙に叩くルート。設定の ``favicon_png`` を返す。
    """
    return _serve_favicon(request, "favicon_png", "image/png")


def favicon_svg(request: HttpRequest) -> FileResponse:
    """Serve ``/favicon.svg`` from the configured SVG favicon."""
    return _serve_favicon(request, "favicon_svg", "image/svg+xml")


def apple_touch_icon(request: HttpRequest) -> FileResponse:
    """Serve ``/apple-touch-icon.png`` from the configured Apple touch icon."""
    return _serve_favicon(request, "apple_touch_icon", "image/png")
