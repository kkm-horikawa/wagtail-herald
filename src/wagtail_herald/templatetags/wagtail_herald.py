"""
Template tags for wagtail-herald SEO output.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from django import template
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe
from wagtail.models import Site

if TYPE_CHECKING:
    from wagtail_herald.models import SEOSettings

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_head(context: dict[str, Any]) -> SafeString:
    """Output all SEO meta tags, OG tags, Twitter Card, favicons, and custom HTML.

    Usage in templates:
        {% load wagtail_herald %}
        <head>
            {% seo_head %}
        </head>
    """
    request = context.get("request")
    page = context.get("page") or context.get("self")

    from wagtail_herald.models import SEOSettings

    seo_settings = None
    if request:
        seo_settings = SEOSettings.for_request(request)

    seo_context = build_seo_context(request, page, seo_settings)

    return mark_safe(
        render_to_string(
            "wagtail_herald/seo_head.html",
            seo_context,
            request=request,
        )
    )


@register.simple_tag(takes_context=True)
def seo_schema(context: dict[str, Any]) -> SafeString:
    """Output JSON-LD structured data for WebSite, Organization, and BreadcrumbList.

    Usage in templates:
        {% load wagtail_herald %}
        <head>
            {% seo_schema %}
        </head>
    """
    request = context.get("request")
    page = context.get("page") or context.get("self")

    from wagtail_herald.models import SEOSettings

    seo_settings = None
    if request:
        seo_settings = SEOSettings.for_request(request)

    schemas: list[dict[str, Any]] = []

    # WebSite schema
    website_schema = _build_website_schema(request)
    if website_schema:
        schemas.append(website_schema)

    # Organization schema (only if organization_name is set)
    if seo_settings and seo_settings.organization_name:
        org_schema = _build_organization_schema(request, seo_settings)
        if org_schema:
            schemas.append(org_schema)

    # BreadcrumbList schema (auto-generated from page hierarchy)
    if page:
        breadcrumb_schema = _build_breadcrumb_schema(request, page)
        if breadcrumb_schema:
            schemas.append(breadcrumb_schema)

    # Page-specific schemas (from schema_data field)
    if page:
        page_schemas = _build_page_schemas(request, page, seo_settings)
        schemas.extend(page_schemas)

    if not schemas:
        return mark_safe("")

    output = '<script type="application/ld+json">\n'
    output += json.dumps(schemas, indent=2, ensure_ascii=False)
    output += "\n</script>"

    return mark_safe(output)


def _build_website_schema(request: HttpRequest | None) -> dict[str, Any] | None:
    """Build WebSite schema.

    Args:
        request: HTTP request object.

    Returns:
        WebSite schema dict or None if no site available.
    """
    if not request:
        return None

    site = Site.find_for_request(request)
    if not site:
        return None

    site_name = site.site_name or ""
    if not site_name:
        return None

    site_url = request.build_absolute_uri("/")

    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": site_url,
    }


def _build_organization_schema(
    request: HttpRequest | None,
    settings: SEOSettings,
) -> dict[str, Any] | None:
    """Build Organization schema.

    Args:
        request: HTTP request object.
        settings: SEOSettings instance.

    Returns:
        Organization schema dict or None.
    """
    if not settings.organization_name:
        return None

    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": settings.organization_type,
        "name": settings.organization_name,
    }

    # Add URL
    if request:
        schema["url"] = request.build_absolute_uri("/")

    # Add logo
    if settings.organization_logo:
        logo_url = _get_logo_url(request, settings.organization_logo)
        if logo_url:
            schema["logo"] = logo_url

    # Add sameAs (social profiles)
    same_as: list[str] = []
    if settings.twitter_handle:
        same_as.append(f"https://twitter.com/{settings.twitter_handle}")
    if settings.facebook_url:
        same_as.append(settings.facebook_url)
    if same_as:
        schema["sameAs"] = same_as

    return schema


def _build_breadcrumb_schema(
    request: HttpRequest | None,
    page: Any,
) -> dict[str, Any] | None:
    """Build BreadcrumbList schema from page hierarchy.

    Args:
        request: HTTP request object.
        page: Wagtail page instance.

    Returns:
        BreadcrumbList schema dict or None if not applicable.
    """
    if not page:
        return None

    # Get ancestors excluding root (depth=1)
    try:
        ancestors = list(page.get_ancestors().filter(depth__gt=1))
    except Exception:
        return None

    # Skip if page is at root level (depth <= 2)
    if not ancestors and getattr(page, "depth", 0) <= 2:
        return None

    items: list[dict[str, Any]] = []
    position = 1

    # Add ancestor pages
    for ancestor in ancestors:
        # Skip unpublished ancestors
        if not getattr(ancestor, "live", True):
            continue

        item: dict[str, Any] = {
            "@type": "ListItem",
            "position": position,
            "name": ancestor.title,
        }

        # Add URL for ancestors (not for current page)
        url = getattr(ancestor, "url", None)
        if url:
            item["item"] = _make_absolute_url(request, url)

        items.append(item)
        position += 1

    # Add current page (without "item" URL per Google guidelines)
    items.append(
        {
            "@type": "ListItem",
            "position": position,
            "name": page.title,
        }
    )

    # Need at least 2 items for a meaningful breadcrumb
    if len(items) < 2:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def _build_page_schemas(
    request: HttpRequest | None,
    page: Any,
    settings: Any,
) -> list[dict[str, Any]]:
    """Build schemas from page's schema_data field.

    Args:
        request: HTTP request object.
        page: Wagtail page instance.
        settings: SEOSettings instance.

    Returns:
        List of schema dicts for selected types.
    """
    schemas: list[dict[str, Any]] = []

    schema_data = getattr(page, "schema_data", None)
    if not schema_data or not isinstance(schema_data, dict):
        return schemas

    schema_types = schema_data.get("types", [])
    schema_properties = schema_data.get("properties", {})

    for schema_type in schema_types:
        # Skip site-wide schemas (handled separately)
        if schema_type in ("WebSite", "Organization", "BreadcrumbList"):
            continue

        custom_props = schema_properties.get(schema_type, {})
        schema = _build_schema_for_type(
            request, page, settings, schema_type, custom_props
        )
        if schema:
            schemas.append(schema)

    return schemas


def _build_schema_for_type(
    request: HttpRequest | None,
    page: Any,
    settings: Any,
    schema_type: str,
    custom_properties: dict[str, Any],
) -> dict[str, Any] | None:
    """Build a single schema with auto-populated and custom fields.

    Args:
        request: HTTP request object.
        page: Wagtail page instance.
        settings: SEOSettings instance.
        schema_type: Schema.org type name.
        custom_properties: Custom properties from user input.

    Returns:
        Schema dict or None.
    """
    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": _get_page_title(page),
        "url": _get_canonical_url(request, page),
    }

    # Add description if available
    description = getattr(page, "search_description", "")
    if description:
        schema["description"] = description

    # Type-specific auto fields
    if schema_type in ("Article", "NewsArticle", "BlogPosting"):
        _add_article_auto_fields(schema, request, page, settings)
    elif schema_type == "Product":
        _add_product_auto_fields(schema, request, page, settings)
    elif schema_type in ("Event", "Course", "Recipe", "HowTo", "JobPosting"):
        _add_content_auto_fields(schema, request, page, settings)

    # Merge custom properties (override auto)
    _deep_merge(schema, custom_properties)

    return schema


def _add_article_auto_fields(
    schema: dict[str, Any],
    request: HttpRequest | None,
    page: Any,
    settings: Any,
) -> None:
    """Add auto-populated fields for Article types."""
    # headline
    schema["headline"] = _get_page_title(page)

    # author
    owner = getattr(page, "owner", None)
    if owner:
        name = getattr(owner, "get_full_name", lambda: "")() or getattr(
            owner, "username", ""
        )
        if name:
            schema["author"] = {"@type": "Person", "name": name}

    # dates
    first_pub = getattr(page, "first_published_at", None)
    if first_pub:
        schema["datePublished"] = first_pub.isoformat()

    last_pub = getattr(page, "last_published_at", None)
    if last_pub:
        schema["dateModified"] = last_pub.isoformat()

    # publisher
    if settings and getattr(settings, "organization_name", None):
        publisher: dict[str, Any] = {
            "@type": "Organization",
            "name": settings.organization_name,
        }
        logo = getattr(settings, "organization_logo", None)
        if logo:
            logo_url = _get_logo_url(request, logo)
            if logo_url:
                publisher["logo"] = {"@type": "ImageObject", "url": logo_url}
        schema["publisher"] = publisher

    # image
    og_data = _get_og_image_data(request, page, settings)
    if og_data.get("url"):
        schema["image"] = og_data["url"]


def _add_product_auto_fields(
    schema: dict[str, Any],
    request: HttpRequest | None,
    page: Any,
    settings: Any,
) -> None:
    """Add auto-populated fields for Product type."""
    # image
    og_data = _get_og_image_data(request, page, settings)
    if og_data.get("url"):
        schema["image"] = og_data["url"]


def _add_content_auto_fields(
    schema: dict[str, Any],
    request: HttpRequest | None,
    page: Any,
    settings: Any,
) -> None:
    """Add auto-populated fields for content types (Event, Course, etc.)."""
    # image
    og_data = _get_og_image_data(request, page, settings)
    if og_data.get("url"):
        schema["image"] = og_data["url"]

    # provider/organizer for Course, Event, JobPosting
    if settings and getattr(settings, "organization_name", None):
        org = {"@type": "Organization", "name": settings.organization_name}
        schema_type = schema.get("@type", "")
        if schema_type == "Course":
            schema.setdefault("provider", org)
        elif schema_type == "Event":
            schema.setdefault("organizer", org)
        elif schema_type == "JobPosting":
            schema.setdefault("hiringOrganization", org)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge override into base dict.

    Args:
        base: Base dictionary to merge into.
        override: Dictionary with values to override.

    Returns:
        Merged dictionary (base is modified in place).
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def _get_logo_url(request: HttpRequest | None, logo: Any) -> str:
    """Get logo URL with appropriate rendition.

    Args:
        request: HTTP request object.
        logo: Wagtail image instance.

    Returns:
        Absolute URL string or empty string.
    """
    if not logo:
        return ""

    try:
        # Google recommends min 112x112px for logo
        rendition = logo.get_rendition("fill-112x112")
        return _make_absolute_url(request, rendition.url)
    except Exception:
        return _get_image_url(request, logo)


def build_seo_context(
    request: HttpRequest | None,
    page: Any,
    settings: SEOSettings | None,
) -> dict[str, Any]:
    """Build context dict for SEO template.

    Args:
        request: HTTP request object.
        page: Wagtail page instance.
        settings: SEOSettings instance.

    Returns:
        Dictionary with all SEO template variables.
    """
    site = Site.find_for_request(request) if request else None

    # Title with separator
    page_title = _get_page_title(page)
    site_name = site.site_name if site else ""
    separator = settings.title_separator if settings else "|"
    full_title = f"{page_title} {separator} {site_name}" if site_name else page_title

    # Description
    description = getattr(page, "search_description", "") or ""

    # Canonical URL
    canonical_url = _get_canonical_url(request, page)

    # Robots
    robots = _get_robots_meta(page)

    # OG Image with dimensions
    og_image_data = _get_og_image_data(request, page, settings)

    # Locale
    locale = settings.default_locale if settings else "en_US"

    # Favicon URLs
    favicon_svg_url = _get_image_url(request, settings.favicon_svg) if settings else ""
    favicon_png_url = _get_image_url(request, settings.favicon_png) if settings else ""
    apple_touch_icon_url = (
        _get_image_url(request, settings.apple_touch_icon) if settings else ""
    )

    return {
        "title": full_title,
        "description": description,
        "canonical_url": canonical_url,
        "robots": robots,
        "og_type": "website",
        "og_title": page_title,
        "og_description": description,
        "og_image": og_image_data.get("url"),
        "og_image_alt": og_image_data.get("alt"),
        "og_image_width": og_image_data.get("width"),
        "og_image_height": og_image_data.get("height"),
        "og_url": canonical_url,
        "og_site_name": site_name,
        "og_locale": locale,
        "twitter_card": "summary_large_image",
        "twitter_site": settings.twitter_handle if settings else "",
        "twitter_title": page_title,
        "twitter_description": description,
        "twitter_image": og_image_data.get("url"),
        "twitter_image_alt": og_image_data.get("alt"),
        "favicon_svg": favicon_svg_url,
        "favicon_png": favicon_png_url,
        "apple_touch_icon": apple_touch_icon_url,
        "google_verification": settings.google_site_verification if settings else "",
        "bing_verification": settings.bing_site_verification if settings else "",
        "custom_head_html": settings.custom_head_html if settings else "",
    }


def _get_page_title(page: Any) -> str:
    """Get page title with seo_title fallback.

    Args:
        page: Wagtail page instance.

    Returns:
        Page title string.
    """
    if not page:
        return ""
    seo_title = getattr(page, "seo_title", None)
    if seo_title:
        return str(seo_title)
    return str(getattr(page, "title", ""))


def _get_canonical_url(request: HttpRequest | None, page: Any) -> str:
    """Get canonical URL for page.

    Uses page's get_canonical_url method if available (SEOPageMixin),
    otherwise falls back to full_url.

    Args:
        request: HTTP request object.
        page: Wagtail page instance.

    Returns:
        Canonical URL string.
    """
    if not page:
        return ""

    if hasattr(page, "get_canonical_url"):
        return str(page.get_canonical_url(request))

    return str(getattr(page, "full_url", ""))


def _get_robots_meta(page: Any) -> str:
    """Get robots meta content.

    Uses page's get_robots_meta method if available (SEOPageMixin).

    Args:
        page: Wagtail page instance.

    Returns:
        Robots meta string (e.g., "noindex, nofollow") or empty string.
    """
    if not page:
        return ""

    if hasattr(page, "get_robots_meta"):
        return str(page.get_robots_meta())

    return ""


def _get_og_image_data(
    request: HttpRequest | None,
    page: Any,
    settings: SEOSettings | None,
) -> dict[str, Any]:
    """Get OG image data with fallback chain.

    Priority: page.og_image → settings.default_og_image → None

    Args:
        request: HTTP request object.
        page: Wagtail page instance.
        settings: SEOSettings instance.

    Returns:
        Dict with url, alt, width, height keys.
    """
    image = None
    alt_text = ""

    # Try page-level og_image first
    if page and hasattr(page, "og_image") and page.og_image:
        image = page.og_image
        if hasattr(page, "get_og_image_alt"):
            alt_text = page.get_og_image_alt()
        else:
            alt_text = getattr(page, "og_image_alt", "") or ""

    # Fall back to settings default_og_image
    elif settings and settings.default_og_image:
        image = settings.default_og_image
        alt_text = settings.default_og_image_alt or ""

    if not image:
        return {"url": "", "alt": "", "width": "", "height": ""}

    # Generate rendition for optimal OG size (1200x630)
    try:
        rendition = image.get_rendition("fill-1200x630")
        url = _make_absolute_url(request, rendition.url)
        return {
            "url": url,
            "alt": alt_text,
            "width": rendition.width,
            "height": rendition.height,
        }
    except Exception:
        # Fallback to original image if rendition fails
        url = _get_image_url(request, image)
        return {
            "url": url,
            "alt": alt_text,
            "width": getattr(image, "width", ""),
            "height": getattr(image, "height", ""),
        }


def _get_image_url(request: HttpRequest | None, image: Any) -> str:
    """Get absolute URL for an image.

    Args:
        request: HTTP request object.
        image: Wagtail image instance.

    Returns:
        Absolute URL string or empty string.
    """
    if not image:
        return ""

    url = getattr(image, "url", "")
    if hasattr(image, "file") and hasattr(image.file, "url"):
        url = image.file.url

    return _make_absolute_url(request, url)


def _make_absolute_url(request: HttpRequest | None, url: str) -> str:
    """Convert relative URL to absolute URL.

    Args:
        request: HTTP request object.
        url: URL string (relative or absolute).

    Returns:
        Absolute URL string.
    """
    if not url:
        return ""

    if url.startswith(("http://", "https://")):
        return url

    if request and hasattr(request, "build_absolute_uri"):
        return str(request.build_absolute_uri(url))

    return url
