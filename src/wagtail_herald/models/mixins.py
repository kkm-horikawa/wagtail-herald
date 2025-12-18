"""
SEO mixin for Wagtail Page models.
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images import get_image_model_string

from wagtail_herald.models.settings import LOCALE_CHOICES
from wagtail_herald.widgets import SchemaJSONField


def _get_schema_data_default() -> dict[str, Any]:
    """Return default value for schema_data field."""
    return {"types": [], "properties": {}}


class SEOPageMixin(models.Model):
    """Mixin to add SEO fields to any Page model.

    Usage:
        class ArticlePage(SEOPageMixin, Page):
            promote_panels = Page.promote_panels + SEOPageMixin.seo_panels
    """

    og_image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("OG image override"),
        help_text=_("Override the default Open Graph image. Recommended: 1200x630px"),
    )

    og_image_alt = models.CharField(
        _("OG image alt text"),
        max_length=255,
        blank=True,
        help_text=_("Alt text for OG image. Describe the image for accessibility"),
    )

    noindex = models.BooleanField(
        _("noindex"),
        default=False,
        help_text=_(
            "Prevent search engines from indexing this page. "
            "Use for private or duplicate content"
        ),
    )

    nofollow = models.BooleanField(
        _("nofollow"),
        default=False,
        help_text=_("Prevent search engines from following links on this page"),
    )

    canonical_url = models.URLField(
        _("Canonical URL"),
        blank=True,
        help_text=_(
            "Override the canonical URL. "
            "Must be absolute URL with protocol (e.g., 'https://example.com/page/')"
        ),
    )

    seo_locale = models.CharField(
        _("SEO locale"),
        max_length=10,
        choices=LOCALE_CHOICES,
        blank=True,
        help_text=_("Override locale for this page (og:locale, html lang attribute)"),
    )

    schema_data = SchemaJSONField(
        _("Structured data"),
        default=_get_schema_data_default,
        blank=True,
        help_text=_("Schema.org structured data configuration for this page"),
    )

    class Meta:
        abstract = True

    seo_panels = [
        MultiFieldPanel(
            [
                FieldPanel("og_image"),
                FieldPanel("og_image_alt"),
                FieldPanel("seo_locale"),
                FieldPanel("noindex"),
                FieldPanel("nofollow"),
                FieldPanel("canonical_url"),
            ],
            heading=_("SEO"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("schema_data"),
            ],
            heading=_("Structured Data"),
        ),
    ]

    def get_robots_meta(self) -> str:
        """Return robots meta content based on noindex/nofollow settings.

        Returns empty string when using defaults (index, follow) to avoid
        redundant meta tags.
        """
        if not self.noindex and not self.nofollow:
            return ""
        directives = []
        if self.noindex:
            directives.append("noindex")
        if self.nofollow:
            directives.append("nofollow")
        return ", ".join(directives)

    def get_canonical_url(self, request: object = None) -> str:
        """Return canonical URL, using override if set.

        Args:
            request: Optional HTTP request for building absolute URI.

        Returns:
            The canonical URL string.
        """
        if self.canonical_url:
            return self.canonical_url
        if request and hasattr(request, "build_absolute_uri"):
            return str(request.build_absolute_uri(self.url))  # type: ignore[attr-defined]
        return str(self.full_url)  # type: ignore[attr-defined]

    def get_og_image_alt(self) -> str:
        """Return OG image alt text, with fallback to image title.

        Returns:
            The alt text string.
        """
        if self.og_image_alt:
            return self.og_image_alt
        if self.og_image and hasattr(self.og_image, "title"):
            return str(self.og_image.title)
        return ""

    def get_page_locale(self) -> str:
        """Return the page locale (og:locale format, e.g., 'ja_JP').

        Fallback chain:
        1. Page's seo_locale field
        2. SEOSettings.default_locale
        3. 'en_US'

        Returns:
            The locale string in og:locale format (underscore separator).
        """
        if self.seo_locale:
            return self.seo_locale

        # Try to get from site settings
        try:
            from wagtail_herald.models import SEOSettings

            # Get the site from page if available
            site = getattr(self, "get_site", lambda: None)()
            if site:
                settings = SEOSettings.for_site(site)
                if settings and settings.default_locale:
                    return str(settings.default_locale)
        except Exception:
            pass

        return "en_US"

    def get_page_lang(self) -> str:
        """Return the language code (e.g., 'ja', 'en', 'zh').

        Extracts the language portion from the full locale.

        Returns:
            The language code string.
        """
        locale = self.get_page_locale()
        return locale.split("_")[0].lower()

    def get_html_lang(self) -> str:
        """Return the locale in HTML lang attribute format (BCP 47).

        Converts underscore format (ja_JP) to hyphen format (ja-JP).

        Returns:
            The locale string in BCP 47 format (hyphen separator).
        """
        locale = self.get_page_locale()
        return locale.replace("_", "-")

    def get_schema_language(self) -> str:
        """Return BCP 47 language code for Schema.org inLanguage property.

        Uses script subtags for Chinese (zh-Hans, zh-Hant) as recommended
        by W3C, since the difference is script-based rather than regional.

        Returns:
            The language code string in BCP 47 format.
        """
        locale = self.get_page_locale()

        # Chinese requires script subtags (W3C recommendation)
        if locale == "zh_CN":
            return "zh-Hans"
        elif locale == "zh_TW":
            return "zh-Hant"

        # Other locales: use simple language code
        return locale.split("_")[0].lower()
