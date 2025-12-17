"""
Django app configuration for wagtail-herald.
"""

from django.apps import AppConfig


class WagtailHeraldConfig(AppConfig):
    """Django app configuration for wagtail-herald."""

    name = "wagtail_herald"
    label = "wagtail_herald"
    verbose_name = "Wagtail Herald"
    default_auto_field = "django.db.models.BigAutoField"
