"""
Django app configuration for wagtail-herald.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailHeraldConfig(AppConfig):
    """Django app configuration for wagtail-herald."""

    name = "wagtail_herald"
    label = "wagtail_herald"
    verbose_name = _("Wagtail Herald")
    default_auto_field = "django.db.models.BigAutoField"
