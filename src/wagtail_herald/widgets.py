"""Custom widgets for wagtail-herald."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from django import forms

if TYPE_CHECKING:
    from collections.abc import Mapping


class SchemaWidget(forms.Widget):
    """Widget for schema type selection and property editing."""

    template_name = "wagtail_herald/widgets/schema_widget.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        default_attrs = {"class": "schema-widget-input"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Add JSON-serialized value to context."""
        context = super().get_context(name, value, attrs)

        # Parse value if string
        if isinstance(value, str):
            try:
                parsed_value = (
                    json.loads(value) if value else {"types": [], "properties": {}}
                )
            except json.JSONDecodeError:
                parsed_value = {"types": [], "properties": {}}
        elif isinstance(value, dict):
            parsed_value = value
        else:
            parsed_value = {"types": [], "properties": {}}

        context["widget"]["value_json"] = json.dumps(parsed_value)
        return context

    def value_from_datadict(
        self, data: Mapping[str, Any], files: Mapping[str, Any], name: str
    ) -> dict[str, Any]:
        """Parse JSON value from form data."""
        value = data.get(name)
        if value:
            try:
                parsed: dict[str, Any] = json.loads(value)
                return parsed
            except json.JSONDecodeError:
                pass
        return {"types": [], "properties": {}}

    def format_value(self, value: Any) -> str:
        """Format value for the hidden input."""
        if isinstance(value, dict):
            return json.dumps(value)
        if isinstance(value, str) and value:
            return value
        return '{"types":[],"properties":{}}'

    class Media:
        css = {
            "all": ("wagtail_herald/css/schema-widget.css",),
        }
        js = ("wagtail_herald/js/schema-widget.iife.js",)
