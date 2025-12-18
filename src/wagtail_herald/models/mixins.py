"""
SEO mixin for Wagtail Page models.
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images import get_image_model_string

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
