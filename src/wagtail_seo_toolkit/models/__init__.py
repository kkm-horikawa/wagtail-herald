"""
wagtail-seo-toolkit models.
"""

from wagtail_seo_toolkit.models.mixins import SEOPageMixin
from wagtail_seo_toolkit.models.settings import SEOSettings

__all__ = [
    "SEOPageMixin",
    "SEOSettings",
]
