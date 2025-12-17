"""
Django app configuration for wagtail-seo-toolkit.
"""

from django.apps import AppConfig


class WagtailSeoToolkitConfig(AppConfig):
    """Django app configuration for wagtail-seo-toolkit."""

    name = "wagtail_seo_toolkit"
    label = "wagtail_seo_toolkit"
    verbose_name = "Wagtail SEO Toolkit"
    default_auto_field = "django.db.models.BigAutoField"
