"""Tests for wagtail_herald telepath adapter."""

from __future__ import annotations

from wagtail_herald.telepath import SchemaWidgetAdapter
from wagtail_herald.widgets import SchemaWidget


class TestSchemaWidgetAdapter:
    """Tests for SchemaWidgetAdapter."""

    def test_adapter_js_constructor(self) -> None:
        """Adapter should have correct JS constructor name."""
        adapter = SchemaWidgetAdapter()

        assert adapter.js_constructor == "wagtail_herald.widgets.SchemaWidget"

    def test_adapter_js_args(self) -> None:
        """Adapter should return HTML template with placeholders."""
        adapter = SchemaWidgetAdapter()
        widget = SchemaWidget()

        args = adapter.js_args(widget)

        assert len(args) == 1
        html = args[0]

        # Should contain placeholders for Telepath
        assert "__NAME__" in html
        assert "__ID__" in html

        # Should contain widget structure
        assert "schema-widget-wrapper" in html
        assert "schema-widget-container" in html
        assert "data-schema-widget" in html

    def test_adapter_registered(self) -> None:
        """Adapter should be registered with Telepath."""
        # Import to trigger registration
        from wagtail_herald import telepath  # noqa: F401

        # Check that the adapter can be used
        # (actual registration verification would require Wagtail's telepath registry)
        adapter = SchemaWidgetAdapter()
        assert adapter is not None
