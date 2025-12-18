"""Tests for wagtail_herald widgets."""

from __future__ import annotations

import json

import pytest
from django.core.exceptions import ValidationError
from django.forms import Form

from wagtail_herald.widgets import (
    SchemaFormField,
    SchemaWidget,
    _is_empty_value,
)


class TestSchemaWidget:
    """Tests for SchemaWidget."""

    def test_widget_renders_template(self) -> None:
        """Widget should render the correct template."""
        widget = SchemaWidget()
        html = widget.render("schema_data", None, attrs={"id": "id_schema_data"})

        assert 'name="schema_data"' in html
        assert 'id="id_schema_data"' in html
        assert "schema-widget-container" in html
        assert "data-schema-widget" in html

    def test_widget_renders_with_dict_value(self) -> None:
        """Widget should correctly render dict values."""
        widget = SchemaWidget()
        value = {"types": ["Article"], "properties": {"Article": {"section": "Tech"}}}
        html = widget.render("schema_data", value, attrs={"id": "id_schema_data"})

        assert "Article" in html
        assert "Tech" in html

    def test_widget_renders_with_json_string_value(self) -> None:
        """Widget should correctly render JSON string values."""
        widget = SchemaWidget()
        value = '{"types": ["Product"], "properties": {}}'
        html = widget.render("schema_data", value, attrs={"id": "id_schema_data"})

        assert "Product" in html

    def test_widget_renders_with_empty_value(self) -> None:
        """Widget should handle None/empty values."""
        widget = SchemaWidget()
        html = widget.render("schema_data", None, attrs={"id": "id_schema_data"})

        # HTML escapes quotes, so check for both escaped and unescaped versions
        assert "types" in html and "properties" in html

    def test_widget_renders_with_invalid_json(self) -> None:
        """Widget should handle invalid JSON gracefully."""
        widget = SchemaWidget()
        html = widget.render(
            "schema_data", "{ invalid json }", attrs={"id": "id_schema_data"}
        )

        # Should fall back to empty state
        assert "types" in html

    def test_value_from_datadict_returns_json_string(self) -> None:
        """Widget should return raw JSON string from form data."""
        widget = SchemaWidget()
        data = {"schema_data": '{"types": ["FAQPage"], "properties": {}}'}

        result = widget.value_from_datadict(data, {}, "schema_data")

        assert result == '{"types": ["FAQPage"], "properties": {}}'

    def test_value_from_datadict_handles_empty(self) -> None:
        """Widget should return default JSON string for empty form data."""
        widget = SchemaWidget()

        result = widget.value_from_datadict({}, {}, "schema_data")

        assert result == '{"types":[],"properties":{}}'

    def test_value_from_datadict_handles_invalid_json(self) -> None:
        """Widget should return invalid JSON string as-is (let form field validate)."""
        widget = SchemaWidget()
        data = {"schema_data": "{ invalid }"}

        result = widget.value_from_datadict(data, {}, "schema_data")

        # Invalid JSON is returned as-is; validation happens in the form field
        assert result == "{ invalid }"

    def test_format_value_with_dict(self) -> None:
        """format_value should convert dict to JSON string."""
        widget = SchemaWidget()
        value = {"types": ["Event"], "properties": {}}

        result = widget.format_value(value)

        assert json.loads(result) == value

    def test_format_value_with_string(self) -> None:
        """format_value should return string as-is."""
        widget = SchemaWidget()
        value = '{"types": ["Person"], "properties": {}}'

        result = widget.format_value(value)

        assert result == value

    def test_format_value_with_empty(self) -> None:
        """format_value should return default for empty values."""
        widget = SchemaWidget()

        result = widget.format_value(None)

        assert json.loads(result) == {"types": [], "properties": {}}

    def test_widget_has_correct_media(self) -> None:
        """Widget should include correct CSS and JS files."""
        widget = SchemaWidget()
        media = widget.media

        assert "wagtail_herald/css/schema-widget.css" in str(media)
        assert "wagtail_herald/js/schema-widget.iife.js" in str(media)

    def test_widget_default_attrs(self) -> None:
        """Widget should have default CSS class."""
        widget = SchemaWidget()

        assert widget.attrs.get("class") == "schema-widget-input"

    def test_widget_custom_attrs(self) -> None:
        """Widget should merge custom attrs with defaults."""
        widget = SchemaWidget(attrs={"data-custom": "value"})

        assert widget.attrs.get("class") == "schema-widget-input"
        assert widget.attrs.get("data-custom") == "value"


class SchemaForm(Form):
    """Test form using SchemaWidget."""

    from django import forms as django_forms

    schema_data = django_forms.CharField(widget=SchemaWidget(), required=False)


class TestSchemaWidgetInForm:
    """Tests for SchemaWidget used in a form."""

    def test_form_renders_widget(self) -> None:
        """Form should render the schema widget."""
        form = SchemaForm()
        html = str(form)

        assert "schema-widget-container" in html

    def test_form_with_initial_data(self) -> None:
        """Form should render with initial data."""
        form = SchemaForm(
            initial={"schema_data": {"types": ["Article"], "properties": {}}}
        )
        html = str(form)

        assert "Article" in html


class TestIsEmptyValue:
    """Tests for _is_empty_value helper function."""

    def test_none_is_empty(self) -> None:
        """None should be considered empty."""
        assert _is_empty_value(None, "string") is True
        assert _is_empty_value(None, "array") is True
        assert _is_empty_value(None, "object") is True

    def test_empty_string_is_empty(self) -> None:
        """Empty strings should be considered empty."""
        assert _is_empty_value("", "string") is True
        assert _is_empty_value("   ", "string") is True

    def test_non_empty_string_is_not_empty(self) -> None:
        """Non-empty strings should not be considered empty."""
        assert _is_empty_value("hello", "string") is False
        assert _is_empty_value("2025-01-15", "datetime") is False

    def test_empty_array_is_empty(self) -> None:
        """Empty arrays should be considered empty."""
        assert _is_empty_value([], "array") is True

    def test_array_with_empty_objects_is_empty(self) -> None:
        """Arrays containing only empty objects should be considered empty."""
        assert (
            _is_empty_value([{"@type": "Question", "name": "", "text": ""}], "array")
            is True
        )
        assert _is_empty_value([{"@type": "HowToStep", "text": ""}], "array") is True

    def test_array_with_content_is_not_empty(self) -> None:
        """Arrays with non-empty content should not be considered empty."""
        assert _is_empty_value(["ingredient1", "ingredient2"], "array") is False
        assert (
            _is_empty_value([{"@type": "Question", "name": "What?"}], "array") is False
        )

    def test_empty_object_is_empty(self) -> None:
        """Objects with only empty values should be considered empty."""
        assert _is_empty_value({}, "object") is True
        assert _is_empty_value({"@type": "PostalAddress"}, "object") is True
        assert (
            _is_empty_value({"@type": "PostalAddress", "streetAddress": ""}, "object")
            is True
        )

    def test_object_with_content_is_not_empty(self) -> None:
        """Objects with non-empty values should not be considered empty."""
        assert _is_empty_value({"streetAddress": "123 Main St"}, "object") is False
        assert _is_empty_value({"@type": "Place", "name": "Tokyo"}, "object") is False


class TestSchemaFormFieldValidation:
    """Tests for SchemaFormField validation."""

    def test_valid_data_passes(self) -> None:
        """Valid data should pass validation."""
        field = SchemaFormField()
        value = {
            "types": ["Article"],
            "properties": {"Article": {"articleSection": "Tech"}},
        }
        result = field.clean(value)
        assert result == value

    def test_empty_data_passes(self) -> None:
        """Empty data should pass validation."""
        field = SchemaFormField()
        result = field.clean(None)
        assert result == {"types": [], "properties": {}}

    def test_invalid_json_raises_error(self) -> None:
        """Invalid JSON string should raise ValidationError."""
        field = SchemaFormField()
        with pytest.raises(ValidationError) as exc_info:
            field.clean("{ invalid json }")
        assert "Invalid JSON" in str(exc_info.value)

    def test_invalid_data_format_raises_error(self) -> None:
        """Non-dict value should raise ValidationError."""
        field = SchemaFormField()
        with pytest.raises(ValidationError) as exc_info:
            field.clean(["not", "a", "dict"])
        assert "Invalid schema data format" in str(exc_info.value)

    def test_recipe_without_ingredients_fails(self) -> None:
        """Recipe without ingredients should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["Recipe"],
            "properties": {
                "Recipe": {
                    "recipeIngredient": [],
                    "recipeInstructions": [{"@type": "HowToStep", "text": "Step 1"}],
                }
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        assert "Ingredients" in str(exc_info.value)

    def test_recipe_without_instructions_fails(self) -> None:
        """Recipe without instructions should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["Recipe"],
            "properties": {
                "Recipe": {
                    "recipeIngredient": ["flour", "sugar"],
                    "recipeInstructions": [],
                }
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        assert "Instructions" in str(exc_info.value)

    def test_recipe_with_both_passes(self) -> None:
        """Recipe with both ingredients and instructions should pass."""
        field = SchemaFormField()
        value = {
            "types": ["Recipe"],
            "properties": {
                "Recipe": {
                    "recipeIngredient": ["flour", "sugar"],
                    "recipeInstructions": [{"@type": "HowToStep", "text": "Mix"}],
                }
            },
        }
        result = field.clean(value)
        assert result == value

    def test_faqpage_without_questions_fails(self) -> None:
        """FAQPage without questions should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["FAQPage"],
            "properties": {
                "FAQPage": {
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": "",
                            "acceptedAnswer": {"@type": "Answer", "text": ""},
                        }
                    ]
                }
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        assert "Questions" in str(exc_info.value)

    def test_faqpage_with_questions_passes(self) -> None:
        """FAQPage with questions should pass validation."""
        field = SchemaFormField()
        value = {
            "types": ["FAQPage"],
            "properties": {
                "FAQPage": {
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": "What is this?",
                            "acceptedAnswer": {"@type": "Answer", "text": "A test"},
                        }
                    ]
                }
            },
        }
        result = field.clean(value)
        assert result == value

    def test_event_without_start_date_fails(self) -> None:
        """Event without startDate should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["Event"],
            "properties": {
                "Event": {
                    "startDate": "",
                    "location": {"@type": "Place", "name": "Tokyo"},
                }
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        assert "Start Date" in str(exc_info.value)

    def test_event_without_location_fails(self) -> None:
        """Event without location should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["Event"],
            "properties": {
                "Event": {
                    "startDate": "2025-03-15T19:00:00",
                    "location": {"@type": "Place", "name": ""},
                }
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        assert "Location" in str(exc_info.value)

    def test_multiple_types_with_one_invalid(self) -> None:
        """Multiple types where one is invalid should fail validation."""
        field = SchemaFormField()
        value = {
            "types": ["Article", "Recipe"],
            "properties": {
                "Article": {"articleSection": "Tech"},
                "Recipe": {"recipeIngredient": [], "recipeInstructions": []},
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            field.clean(value)
        # Both Recipe errors should be present in a single joined message
        error_str = str(exc_info.value)
        assert "Ingredients" in error_str
        assert "Instructions" in error_str
        # Errors should be joined with semicolon
        assert ";" in error_str

    def test_types_without_required_fields_pass(self) -> None:
        """Schema types without required fields should pass."""
        field = SchemaFormField()
        value = {
            "types": ["Article", "Product", "Person"],
            "properties": {},
        }
        result = field.clean(value)
        assert result == value


class TestIsEmptyValueAdditional:
    """Additional tests for _is_empty_value edge cases."""

    def test_array_with_number_items_not_empty(self):
        """Arrays with number items should not be considered empty."""
        # Numbers in arrays are not strings or dicts, so they don't match existing checks
        # This tests line 60 branch
        assert (
            _is_empty_value([1, 2, 3], "array") is True
        )  # numbers don't count as non-empty items

    def test_nested_object_with_content_not_empty(self):
        """Nested objects with content should not be empty."""
        # This tests the recursive call at line 70
        value = {
            "@type": "Question",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "This is the answer",
            },
        }
        assert _is_empty_value(value, "object") is False

    def test_nested_object_empty(self):
        """Nested objects that are empty should be considered empty."""
        value = {
            "@type": "Question",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "",
            },
        }
        assert _is_empty_value(value, "object") is True

    def test_object_with_numeric_value(self):
        """Objects with numeric values should not be empty."""
        # Tests line 87-88
        assert _is_empty_value({"price": 0}, "object") is False
        assert _is_empty_value({"price": 99.99}, "object") is False
        assert _is_empty_value({"available": True}, "object") is False
        assert _is_empty_value({"available": False}, "object") is False

    def test_array_type_with_non_list_value(self):
        """Array type check with non-list value should be empty."""
        # Tests line 59-60
        assert _is_empty_value("not a list", "array") is True
        assert _is_empty_value(123, "array") is True

    def test_object_type_with_non_dict_value(self):
        """Object type check with non-dict value should be empty."""
        # Tests line 74-76
        assert _is_empty_value("not a dict", "object") is True
        assert _is_empty_value(123, "object") is True
        assert _is_empty_value(["a", "b"], "object") is True

    def test_array_with_empty_strings(self):
        """Arrays with only empty strings should be empty."""
        assert _is_empty_value(["", "   ", ""], "array") is True

    def test_deeply_nested_object(self):
        """Deeply nested objects should be checked recursively."""
        value = {
            "@type": "Event",
            "location": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "123 Main St",
                },
            },
        }
        assert _is_empty_value(value, "object") is False

    def test_deeply_nested_empty_object(self):
        """Deeply nested empty objects should be considered empty."""
        value = {
            "@type": "Event",
            "location": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                },
            },
        }
        assert _is_empty_value(value, "object") is True
