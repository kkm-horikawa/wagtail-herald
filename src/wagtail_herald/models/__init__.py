"""
wagtail-herald models.
"""

from wagtail_herald.models.mixins import SEOPageMixin
from wagtail_herald.models.settings import SEOSettings

__all__ = [
    "SEOPageMixin",
    "SEOSettings",
]
