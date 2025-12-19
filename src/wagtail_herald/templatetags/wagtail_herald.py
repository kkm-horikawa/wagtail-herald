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

    # Get enabled schema types from page's schema_data
    schema_data = getattr(page, "schema_data", None) if page else None
    enabled_types = (
        schema_data.get("types", []) if isinstance(schema_data, dict) else []
    )

    # WebSite schema (only if enabled in schema_data)
    if "WebSite" in enabled_types:
        website_schema = _build_website_schema(request)
        if website_schema:
            schemas.append(website_schema)

    # Organization schema (only if enabled and organization_name is set)
    if (
        "Organization" in enabled_types
        and seo_settings
        and seo_settings.organization_name
    ):
        org_schema = _build_organization_schema(request, seo_settings)
        if org_schema:
            schemas.append(org_schema)

    # BreadcrumbList schema (only if enabled)
    if "BreadcrumbList" in enabled_types and page:
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


@register.simple_tag(takes_context=True)
def seo_body(context: dict[str, Any]) -> SafeString:
    """Output analytics noscript fallbacks and custom body HTML.

    Should be placed immediately after the opening <body> tag.

    Usage in templates:
        {% load wagtail_herald %}
        <body>
            {% seo_body %}
            <!-- Your content -->
        </body>
    """
    request = context.get("request")

    from wagtail_herald.models import SEOSettings

    seo_settings = None
    if request:
        seo_settings = SEOSettings.for_request(request)

    body_context = {
        "gtm_container_id": seo_settings.gtm_container_id if seo_settings else "",
        "custom_body_end_html": seo_settings.custom_body_end_html
        if seo_settings
        else "",
    }

    return mark_safe(
        render_to_string(
            "wagtail_herald/seo_body.html",
            body_context,
            request=request,
        )
    )


@register.simple_tag(takes_context=True)
def page_lang(context: dict[str, Any]) -> str:
    """Return the language code for the current page (e.g., 'ja', 'en', 'zh').

    Usage in templates:
        {% load wagtail_herald %}
        <html lang="{% page_lang %}">

    Fallback chain:
    1. Page's locale field (if SEOPageMixin)
    2. SEOSettings.default_locale
    3. 'en'
    """
    page = context.get("page") or context.get("self")

    # Try to get from page's method
    if page and hasattr(page, "get_page_lang"):
        return str(page.get_page_lang())

    # Fallback: try to get from SEOSettings
    request = context.get("request")
    if request:
        from wagtail_herald.models import SEOSettings

        settings = SEOSettings.for_request(request)
        if settings and settings.default_locale:
            return str(settings.default_locale).split("_")[0].lower()

    return "en"


@register.simple_tag(takes_context=True)
def page_locale(context: dict[str, Any]) -> str:
    """Return the full locale for the current page (e.g., 'ja_JP', 'en_US').

    Usage in templates:
        {% load wagtail_herald %}
        <meta property="og:locale" content="{% page_locale %}">

    Fallback chain:
    1. Page's locale field (if SEOPageMixin)
    2. SEOSettings.default_locale
    3. 'en_US'
    """
    page = context.get("page") or context.get("self")

    # Try to get from page's method
    if page and hasattr(page, "get_page_locale"):
        return str(page.get_page_locale())

    # Fallback: try to get from SEOSettings
    request = context.get("request")
    if request:
        from wagtail_herald.models import SEOSettings

        settings = SEOSettings.for_request(request)
        if settings and settings.default_locale:
            return str(settings.default_locale)

    return "en_US"


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

    # Add inLanguage for applicable schema types
    # Person type uses knowsLanguage instead of inLanguage
    if schema_type != "Person":
        lang = _get_schema_language(page, settings)
        if lang:
            schema["inLanguage"] = lang

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

    # Filter out empty values from custom properties before merging
    filtered_props = _filter_empty_values(custom_properties)
    if filtered_props and isinstance(filtered_props, dict):
        _deep_merge(schema, filtered_props)

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


def _filter_empty_values(data: Any) -> Any:
    """Recursively filter out empty values from data.

    Removes:
    - Empty strings ""
    - Empty lists []
    - Dicts with only empty values (after filtering)
    - None values

    Preserves:
    - Numbers (including 0)
    - Booleans (including False)
    - Non-empty strings, lists, dicts

    Args:
        data: Data to filter (dict, list, or primitive).

    Returns:
        Filtered data, or None if entirely empty.
    """
    if data is None:
        return None

    if isinstance(data, str):
        return data if data else None

    if isinstance(data, bool):
        return data

    if isinstance(data, (int, float)):
        return data

    if isinstance(data, list):
        filtered_list = [_filter_empty_values(item) for item in data]
        filtered_list = [item for item in filtered_list if item is not None]
        return filtered_list if filtered_list else None

    if isinstance(data, dict):
        filtered_dict: dict[str, Any] = {}
        for key, value in data.items():
            # Keep @type and @context even if technically "empty check" passes
            if key in ("@type", "@context"):
                filtered_dict[key] = value
                continue
            filtered_value = _filter_empty_values(value)
            if filtered_value is not None:
                filtered_dict[key] = filtered_value
        # Return None if only @type/@context remain (no actual data)
        meaningful_keys = [k for k in filtered_dict if k not in ("@type", "@context")]
        return filtered_dict if meaningful_keys else None

    return data


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

    # Locale (page-specific takes priority over settings default)
    locale = "en_US"
    if page and hasattr(page, "get_page_locale"):
        locale = page.get_page_locale()
    elif settings and settings.default_locale:
        locale = settings.default_locale

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
        "gtm_container_id": settings.gtm_container_id if settings else "",
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


def _get_schema_language(page: Any, settings: Any) -> str:
    """Get BCP 47 language code for Schema.org inLanguage property.

    Uses page's get_schema_language method if available (SEOPageMixin),
    otherwise falls back to settings.default_locale or 'en'.

    Args:
        page: Wagtail page instance.
        settings: SEOSettings instance.

    Returns:
        BCP 47 language code string (e.g., 'ja', 'en', 'zh-Hans').
    """
    # Try page's method first (SEOPageMixin)
    if page and hasattr(page, "get_schema_language"):
        return str(page.get_schema_language())

    # Fall back to settings default_locale
    if settings and hasattr(settings, "default_locale") and settings.default_locale:
        locale = str(settings.default_locale)
        # Chinese requires script subtags
        if locale == "zh_CN":
            return "zh-Hans"
        elif locale == "zh_TW":
            return "zh-Hant"
        return locale.split("_")[0].lower()

    return "en"


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
