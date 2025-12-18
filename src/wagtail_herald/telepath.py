"""
Wagtail Telepath adapter for SchemaWidget.

This module provides StreamField integration by registering a Telepath
adapter that allows the widget to be dynamically created on the client side.
"""

from __future__ import annotations

from django import forms

# Wagtail 7.1+ moved telepath imports to wagtail.admin.telepath
# Fall back to old locations for backwards compatibility
try:
    from wagtail.admin.telepath import register
    from wagtail.admin.telepath.widgets import WidgetAdapter
except ImportError:
    from wagtail.telepath import register
    from wagtail.widget_adapters import WidgetAdapter

from wagtail_herald.widgets import SchemaWidget


class SchemaWidgetAdapter(WidgetAdapter):  # type: ignore[misc]
    """
    Telepath adapter for SchemaWidget.

    This adapter serializes the widget's HTML template for client-side
    rendering and registers it with the JavaScript telepath registry.
    """

    js_constructor = "wagtail_herald.widgets.SchemaWidget"

    def js_args(self, widget: forms.Widget) -> list[str]:
        """
        Return arguments to pass to the JavaScript constructor.

        Args:
            widget: The SchemaWidget instance

        Returns:
            List containing the rendered HTML template with placeholders
        """
        return [
            widget.render("__NAME__", None, attrs={"id": "__ID__"}),
        ]


# Register the adapter
register(SchemaWidgetAdapter(), SchemaWidget)
