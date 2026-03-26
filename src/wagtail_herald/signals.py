"""
Signal handlers for wagtail-herald.
"""

import logging
from typing import Any

from wagtail.models import Page
from wagtail.signals import page_published

from wagtail_herald.indexnow import notify_indexnow

logger = logging.getLogger(__name__)


def handle_page_published(sender: type, instance: Page, **kwargs: Any) -> None:
    """Notify IndexNow when a page is published."""
    from wagtail_herald.models.settings import SEOSettings

    try:
        site = instance.get_site()
    except Exception:
        logger.debug("IndexNow: could not determine site for page %s", instance.pk)
        return

    if not site:
        return

    settings = SEOSettings.for_site(site)
    if settings.indexnow_api_key:
        notify_indexnow(instance, settings.indexnow_api_key)


def register_signals() -> None:
    """Connect signal handlers."""
    page_published.connect(handle_page_published)
