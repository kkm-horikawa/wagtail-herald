"""
Site-wide SEO settings model.
"""

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string

LOCALE_CHOICES = [
    ("en_US", "English (US)"),
    ("en_GB", "English (UK)"),
    ("ja_JP", "日本語 (日本)"),
    ("zh_CN", "中文 (简体)"),
    ("zh_TW", "中文 (繁體)"),
    ("ko_KR", "한국어"),
    ("fr_FR", "Français"),
    ("de_DE", "Deutsch"),
    ("es_ES", "Español"),
    ("pt_BR", "Português (Brasil)"),
]

ORGANIZATION_TYPE_CHOICES = [
    ("Organization", "Organization"),
    ("Corporation", "Corporation"),
    ("LocalBusiness", "Local Business"),
    ("OnlineStore", "Online Store"),
    ("EducationalOrganization", "Educational Organization"),
    ("GovernmentOrganization", "Government Organization"),
    ("NGO", "NGO"),
]


@register_setting(icon="cog")
class SEOSettings(BaseSiteSetting):
    """Site-wide SEO configuration."""

    # Fetch all image ForeignKeys in a single query
    select_related = [
        "organization_logo",
        "default_og_image",
        "favicon_svg",
        "favicon_png",
        "apple_touch_icon",
    ]

    class Meta:
        verbose_name = _("SEO Settings")

    # Organization
    organization_name = models.CharField(
        _("Organization name"),
        max_length=255,
        blank=True,
        help_text=_("Organization name for Schema.org structured data"),
    )
    organization_type = models.CharField(
        _("Organization type"),
        max_length=50,
        choices=ORGANIZATION_TYPE_CHOICES,
        default="Organization",
        help_text=_(
            "Organization type for Schema.org (e.g., Corporation, LocalBusiness)"
        ),
    )
    organization_logo = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Organization logo"),
        help_text=_("Logo for Schema.org. Recommended: 112x112px minimum, PNG/JPEG"),
    )

    # Social
    twitter_handle = models.CharField(
        _("Twitter handle"),
        max_length=255,
        blank=True,
        help_text=_("Twitter username without @ (e.g., 'example' not '@example')"),
    )
    facebook_url = models.URLField(
        _("Facebook URL"),
        blank=True,
        help_text=_("Full Facebook page URL (e.g., 'https://facebook.com/example')"),
    )

    # Default SEO
    title_separator = models.CharField(
        _("Title separator"),
        max_length=10,
        default="|",
        help_text=_(
            "Character(s) between page title and site name (e.g., '|', '-', '·')"
        ),
    )
    default_locale = models.CharField(
        _("Default locale"),
        max_length=10,
        choices=LOCALE_CHOICES,
        default="en_US",
        help_text=_("Default locale for og:locale meta tag (e.g., en_US, ja_JP)"),
    )

    # Images
    default_og_image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Default OG image"),
        help_text=_(
            "Default image for social sharing. Recommended: 1200x630px, JPEG/PNG"
        ),
    )
    default_og_image_alt = models.CharField(
        _("Default OG image alt text"),
        max_length=255,
        blank=True,
        help_text=_(
            "Alt text for default OG image. Describe the image for accessibility"
        ),
    )
    favicon_svg = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Favicon (SVG)"),
        help_text=_(
            "SVG favicon for modern browsers. "
            "Requires WAGTAILIMAGES_EXTENSIONS to include 'svg' in settings"
        ),
    )
    favicon_png = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Favicon (PNG)"),
        help_text=_("PNG favicon fallback. Minimum: 48x48px (Google requirement)"),
    )
    apple_touch_icon = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Apple Touch Icon"),
        help_text=_("iOS home screen icon. Recommended: 180x180px, PNG format"),
    )

    # Analytics
    gtm_container_id = models.CharField(
        _("GTM Container ID"),
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^GTM-[A-Z0-9]+$",
                message=_("Enter a valid GTM Container ID (e.g., GTM-XXXXXX)"),
            ),
        ],
        help_text=_("Google Tag Manager Container ID (e.g., GTM-XXXXXX)"),
    )

    # robots.txt
    robots_txt = models.TextField(
        _("robots.txt content"),
        blank=True,
        help_text=_(
            "Custom robots.txt content. Leave empty for default "
            "(allow all crawlers, include sitemap). "
            "Requires including wagtail_herald.urls in your urls.py."
        ),
    )

    # Custom Code
    custom_head_html = models.TextField(
        _("Custom head HTML"),
        blank=True,
        help_text=_(
            "Custom HTML to insert in <head>. Use for additional verification tags, "
            "analytics code, preload links, etc. No validation - use with caution."
        ),
    )
    custom_body_end_html = models.TextField(
        _("Custom body end HTML"),
        blank=True,
        help_text=_(
            "Custom HTML to insert before </body>. Use for chat widgets, "
            "deferred scripts, etc. No validation - use with caution."
        ),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("organization_name"),
                FieldPanel("organization_type"),
                FieldPanel("organization_logo"),
            ],
            heading=_("Organization"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_handle"),
                FieldPanel("facebook_url"),
            ],
            heading=_("Social Profiles"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("title_separator"),
                FieldPanel("default_locale"),
            ],
            heading=_("Default SEO Settings"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("default_og_image"),
                FieldPanel("default_og_image_alt"),
                FieldPanel("favicon_svg"),
                FieldPanel("favicon_png"),
                FieldPanel("apple_touch_icon"),
            ],
            heading=_("Images"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("gtm_container_id"),
            ],
            heading=_("Analytics"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("robots_txt"),
            ],
            heading=_("robots.txt"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("custom_head_html"),
                FieldPanel("custom_body_end_html"),
            ],
            heading=_("Custom Code"),
        ),
    ]
