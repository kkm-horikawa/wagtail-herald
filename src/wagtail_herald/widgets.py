"""Custom widgets for wagtail-herald."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from collections.abc import Mapping

# Required fields for each schema type (based on Google's rich results requirements)
# Format: schema_type -> list of (field_name, field_type, display_name)
SCHEMA_REQUIRED_FIELDS: dict[str, list[tuple[str, str, Any]]] = {
    "LocalBusiness": [
        ("address", "object", _("Address")),
    ],
    "FAQPage": [
        ("mainEntity", "array", _("Questions")),
    ],
    "HowTo": [
        ("step", "array", _("Steps")),
    ],
    "Event": [
        ("startDate", "string", _("Start Date")),
        ("location", "object", _("Location")),
    ],
    "Recipe": [
        ("recipeIngredient", "array", _("Ingredients")),
        ("recipeInstructions", "array", _("Instructions")),
    ],
    "JobPosting": [
        ("jobLocation", "object", _("Job Location")),
    ],
}


def _is_empty_value(value: Any, field_type: str) -> bool:
    """Check if a value is considered empty for validation.

    Args:
        value: The value to check.
        field_type: The expected type ('string', 'array', 'object', 'datetime').

    Returns:
        True if the value is empty, False otherwise.
    """
    if value is None:
        return True

    if field_type == "string" or field_type == "datetime":
        return not bool(value) or (isinstance(value, str) and not value.strip())

    if field_type == "array":
        if not isinstance(value, list):
            return True
        if len(value) == 0:
            return True
        # Check if array has at least one non-empty item
        for item in value:
            if isinstance(item, dict):
                # For objects like Question, HowToStep, check if they have content
                # Recursively check nested objects
                if not _is_empty_value(item, "object"):
                    return False
            elif isinstance(item, str) and item.strip():
                return False
        return True

    if field_type == "object":
        if not isinstance(value, dict):
            return True
        # Check if object has at least one non-empty field (excluding @type)
        for key, val in value.items():
            if key == "@type":
                continue
            if isinstance(val, str) and val.strip():
                return False
            if isinstance(val, dict):
                # Recursively check nested objects
                if not _is_empty_value(val, "object"):
                    return False
            if isinstance(val, (int, float, bool)):
                return False
        return True

    return not bool(value)


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
    ) -> str:
        """Return raw JSON string from form data.

        Django's JSONField handles the parsing, so we just return the string.
        """
        value: Any = data.get(name)
        if value and isinstance(value, str):
            return str(value)
        return '{"types":[],"properties":{}}'

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


class SchemaFormField(forms.JSONField):
    """Form field for schema data with validation.

    Validates that required fields for each selected schema type are filled in.
    """

    widget = SchemaWidget

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def clean(self, value: Any) -> dict[str, Any]:
        """Validate the schema data.

        Args:
            value: The schema data dict with 'types' and 'properties'.

        Returns:
            The validated schema data.

        Raises:
            ValidationError: If required fields are missing for selected types,
                or if the JSON is invalid.
        """
        # First, let parent handle JSON parsing
        if isinstance(value, str) and value:
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValidationError(
                    _("Invalid JSON: %(error)s") % {"error": str(e)}
                ) from e

        if not value:
            return {"types": [], "properties": {}}

        if not isinstance(value, dict):
            raise ValidationError(_("Invalid schema data format"))

        schema_types = value.get("types", [])
        properties = value.get("properties", {})

        errors: list[str] = []

        for schema_type in schema_types:
            required_fields = SCHEMA_REQUIRED_FIELDS.get(schema_type, [])
            type_props = properties.get(schema_type, {})

            for field_name, field_type, display_name in required_fields:
                field_value = type_props.get(field_name)
                if _is_empty_value(field_value, field_type):
                    errors.append(
                        _("%(schema_type)s: %(field_name)s is required")
                        % {"schema_type": schema_type, "field_name": display_name}
                    )

        if errors:
            # Join errors into a single message to avoid UI duplication
            raise ValidationError("; ".join(str(e) for e in errors))

        return value


# Alias for backwards compatibility
SchemaField = SchemaFormField


class SchemaJSONField(models.JSONField):
    """JSONField that uses SchemaFormField for form validation.

    This field validates that required fields for each selected schema type
    are filled in when the form is submitted.
    """

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Return SchemaFormField for form rendering and validation."""
        defaults: dict[str, Any] = {
            "form_class": SchemaFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
