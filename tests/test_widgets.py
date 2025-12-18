"""Tests for wagtail_herald widgets."""

from __future__ import annotations

import json

from django.forms import Form

from wagtail_herald.widgets import SchemaWidget


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

    def test_value_from_datadict_parses_json(self) -> None:
        """Widget should parse JSON from form data."""
        widget = SchemaWidget()
        data = {"schema_data": '{"types": ["FAQPage"], "properties": {}}'}

        result = widget.value_from_datadict(data, {}, "schema_data")

        assert result == {"types": ["FAQPage"], "properties": {}}

    def test_value_from_datadict_handles_empty(self) -> None:
        """Widget should handle empty form data."""
        widget = SchemaWidget()

        result = widget.value_from_datadict({}, {}, "schema_data")

        assert result == {"types": [], "properties": {}}

    def test_value_from_datadict_handles_invalid_json(self) -> None:
        """Widget should handle invalid JSON in form data."""
        widget = SchemaWidget()
        data = {"schema_data": "{ invalid }"}

        result = widget.value_from_datadict(data, {}, "schema_data")

        assert result == {"types": [], "properties": {}}

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
