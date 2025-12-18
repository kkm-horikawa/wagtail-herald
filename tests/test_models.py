"""
Tests for wagtail-herald models.
"""

import pytest

from wagtail_herald.models import SEOPageMixin, SEOSettings


class TestSEOSettings:
    """Tests for SEOSettings model."""

    def test_model_exists(self):
        """Test that SEOSettings model can be imported."""
        assert SEOSettings is not None

    def test_default_values(self, site):
        """Test default values for SEOSettings fields."""
        settings = SEOSettings.objects.create(site=site)

        assert settings.organization_name == ""
        assert settings.organization_type == "Organization"
        assert settings.twitter_handle == ""
        assert settings.facebook_url == ""
        assert settings.title_separator == "|"
        assert settings.default_locale == "en_US"
        assert settings.default_og_image_alt == ""
        assert settings.google_site_verification == ""
        assert settings.bing_site_verification == ""
        assert settings.custom_head_html == ""

    def test_image_fields_are_nullable(self, site):
        """Test that image fields accept null values."""
        settings = SEOSettings.objects.create(site=site)

        assert settings.organization_logo is None
        assert settings.default_og_image is None
        assert settings.favicon_svg is None
        assert settings.favicon_png is None
        assert settings.apple_touch_icon is None

    def test_verbose_name(self):
        """Test that verbose_name is set correctly."""
        assert SEOSettings._meta.verbose_name == "SEO Settings"

    def test_organization_type_choices(self):
        """Test that organization_type has valid choices."""
        field = SEOSettings._meta.get_field("organization_type")
        choices = dict(field.choices)

        assert "Organization" in choices
        assert "Corporation" in choices
        assert "LocalBusiness" in choices
        assert "OnlineStore" in choices

    def test_locale_choices(self):
        """Test that default_locale has valid choices."""
        field = SEOSettings._meta.get_field("default_locale")
        choices = dict(field.choices)

        assert "en_US" in choices
        assert "ja_JP" in choices
        assert "zh_CN" in choices

    def test_for_request(self, site, rf):
        """Test for_request method returns settings for site."""
        SEOSettings.objects.create(
            site=site,
            organization_name="Test Org",
        )

        request = rf.get("/")
        request.site = site

        retrieved = SEOSettings.for_request(request)
        assert retrieved.organization_name == "Test Org"

    def test_panels_defined(self):
        """Test that panels are defined for admin UI."""
        assert hasattr(SEOSettings, "panels")
        assert len(SEOSettings.panels) > 0

    def test_field_help_texts(self):
        """Test that all fields have help_text defined."""
        fields_with_help_text = [
            "organization_name",
            "organization_type",
            "twitter_handle",
            "facebook_url",
            "title_separator",
            "default_locale",
            "default_og_image_alt",
            "google_site_verification",
            "bing_site_verification",
            "custom_head_html",
        ]

        for field_name in fields_with_help_text:
            field = SEOSettings._meta.get_field(field_name)
            assert field.help_text, f"{field_name} should have help_text"


class TestSEOPageMixin:
    """Tests for SEOPageMixin abstract model."""

    def test_mixin_exists(self):
        """Test that SEOPageMixin can be imported."""
        assert SEOPageMixin is not None

    def test_is_abstract(self):
        """Test that SEOPageMixin is an abstract model."""
        assert SEOPageMixin._meta.abstract is True

    def test_seo_panels_defined(self):
        """Test that seo_panels class attribute is defined."""
        assert hasattr(SEOPageMixin, "seo_panels")
        assert len(SEOPageMixin.seo_panels) > 0

    def test_has_expected_fields(self):
        """Test that SEOPageMixin defines expected fields."""
        field_names = [f.name for f in SEOPageMixin._meta.get_fields()]

        assert "og_image" in field_names
        assert "og_image_alt" in field_names
        assert "noindex" in field_names
        assert "nofollow" in field_names
        assert "canonical_url" in field_names
        assert "schema_data" in field_names

    def test_schema_data_default(self):
        """Test that schema_data has correct default value."""
        from wagtail_herald.models.mixins import _get_schema_data_default

        default = _get_schema_data_default()
        assert default == {"types": [], "properties": {}}

    def test_schema_data_uses_custom_field(self):
        """Test that schema_data uses SchemaJSONField with validation."""
        from wagtail_herald.widgets import SchemaFormField, SchemaJSONField

        # Verify the model field is SchemaJSONField
        field = SEOPageMixin._meta.get_field("schema_data")
        assert isinstance(field, SchemaJSONField)

        # Verify the formfield is SchemaFormField (which includes validation)
        formfield = field.formfield()
        assert isinstance(formfield, SchemaFormField)

    def test_field_help_texts(self):
        """Test that all fields have help_text defined."""
        fields_with_help_text = [
            "og_image",
            "og_image_alt",
            "noindex",
            "nofollow",
            "canonical_url",
        ]

        for field_name in fields_with_help_text:
            field = SEOPageMixin._meta.get_field(field_name)
            assert field.help_text, f"{field_name} should have help_text"

    def test_noindex_default_is_false(self):
        """Test that noindex defaults to False."""
        field = SEOPageMixin._meta.get_field("noindex")
        assert field.default is False

    def test_nofollow_default_is_false(self):
        """Test that nofollow defaults to False."""
        field = SEOPageMixin._meta.get_field("nofollow")
        assert field.default is False

    def test_og_image_is_nullable(self):
        """Test that og_image field is nullable."""
        field = SEOPageMixin._meta.get_field("og_image")
        assert field.null is True
        assert field.blank is True

    def test_canonical_url_is_blank(self):
        """Test that canonical_url allows blank values."""
        field = SEOPageMixin._meta.get_field("canonical_url")
        assert field.blank is True


class TestSEOPageMixinMethods:
    """Tests for SEOPageMixin helper methods."""

    @pytest.fixture
    def mixin_instance(self):
        """Create a mock instance with mixin attributes."""

        class MockPage:
            """Mock page with SEOPageMixin attributes."""

            noindex = False
            nofollow = False
            canonical_url = ""
            og_image = None
            og_image_alt = ""
            locale = ""
            url = "/test-page/"
            full_url = "https://example.com/test-page/"

            get_robots_meta = SEOPageMixin.get_robots_meta
            get_canonical_url = SEOPageMixin.get_canonical_url
            get_og_image_alt = SEOPageMixin.get_og_image_alt
            get_page_locale = SEOPageMixin.get_page_locale
            get_page_lang = SEOPageMixin.get_page_lang
            get_html_lang = SEOPageMixin.get_html_lang

        return MockPage()

    def test_get_robots_meta_default(self, mixin_instance):
        """Test robots meta returns empty string for defaults."""
        result = mixin_instance.get_robots_meta()
        assert result == ""

    def test_get_robots_meta_noindex(self, mixin_instance):
        """Test robots meta with noindex."""
        mixin_instance.noindex = True
        result = mixin_instance.get_robots_meta()
        assert result == "noindex"

    def test_get_robots_meta_nofollow(self, mixin_instance):
        """Test robots meta with nofollow."""
        mixin_instance.nofollow = True
        result = mixin_instance.get_robots_meta()
        assert result == "nofollow"

    def test_get_robots_meta_both(self, mixin_instance):
        """Test robots meta with both noindex and nofollow."""
        mixin_instance.noindex = True
        mixin_instance.nofollow = True
        result = mixin_instance.get_robots_meta()
        assert result == "noindex, nofollow"

    def test_get_canonical_url_default(self, mixin_instance):
        """Test canonical URL returns full_url by default."""
        result = mixin_instance.get_canonical_url()
        assert result == "https://example.com/test-page/"

    def test_get_canonical_url_override(self, mixin_instance):
        """Test canonical URL returns override when set."""
        mixin_instance.canonical_url = "https://other.com/canonical/"
        result = mixin_instance.get_canonical_url()
        assert result == "https://other.com/canonical/"

    def test_get_canonical_url_with_request(self, mixin_instance, rf):
        """Test canonical URL builds absolute URI with request."""
        request = rf.get("/test-page/")
        result = mixin_instance.get_canonical_url(request)
        assert "test-page" in result

    def test_get_og_image_alt_default(self, mixin_instance):
        """Test OG image alt returns empty string by default."""
        result = mixin_instance.get_og_image_alt()
        assert result == ""

    def test_get_og_image_alt_explicit(self, mixin_instance):
        """Test OG image alt returns explicit value."""
        mixin_instance.og_image_alt = "Test alt text"
        result = mixin_instance.get_og_image_alt()
        assert result == "Test alt text"

    def test_get_og_image_alt_fallback_to_image_title(self, mixin_instance):
        """Test OG image alt falls back to image title."""

        class MockImage:
            title = "Image Title"

        mixin_instance.og_image = MockImage()
        result = mixin_instance.get_og_image_alt()
        assert result == "Image Title"

    def test_get_og_image_alt_explicit_over_fallback(self, mixin_instance):
        """Test explicit alt text takes precedence over image title."""

        class MockImage:
            title = "Image Title"

        mixin_instance.og_image = MockImage()
        mixin_instance.og_image_alt = "Explicit Alt"
        result = mixin_instance.get_og_image_alt()
        assert result == "Explicit Alt"

    def test_locale_field_exists(self, mixin_instance):
        """Test that locale field exists and is empty by default."""
        assert hasattr(mixin_instance, "locale")
        assert mixin_instance.locale == ""

    def test_get_page_locale_default(self, mixin_instance):
        """Test get_page_locale returns en_US when no locale set."""
        result = mixin_instance.get_page_locale()
        assert result == "en_US"

    def test_get_page_locale_explicit(self, mixin_instance):
        """Test get_page_locale returns explicit value."""
        mixin_instance.locale = "ja_JP"
        result = mixin_instance.get_page_locale()
        assert result == "ja_JP"

    def test_get_page_lang_default(self, mixin_instance):
        """Test get_page_lang returns 'en' when no locale set."""
        result = mixin_instance.get_page_lang()
        assert result == "en"

    def test_get_page_lang_explicit(self, mixin_instance):
        """Test get_page_lang extracts language from locale."""
        mixin_instance.locale = "ja_JP"
        result = mixin_instance.get_page_lang()
        assert result == "ja"

    def test_get_page_lang_chinese(self, mixin_instance):
        """Test get_page_lang handles Chinese locales."""
        mixin_instance.locale = "zh_CN"
        result = mixin_instance.get_page_lang()
        assert result == "zh"

    def test_get_html_lang_default(self, mixin_instance):
        """Test get_html_lang returns en-US by default."""
        result = mixin_instance.get_html_lang()
        assert result == "en-US"

    def test_get_html_lang_explicit(self, mixin_instance):
        """Test get_html_lang converts underscore to hyphen."""
        mixin_instance.locale = "ja_JP"
        result = mixin_instance.get_html_lang()
        assert result == "ja-JP"

    def test_get_html_lang_german(self, mixin_instance):
        """Test get_html_lang works for German locale."""
        mixin_instance.locale = "de_DE"
        result = mixin_instance.get_html_lang()
        assert result == "de-DE"

    def test_get_page_locale_fallback_to_settings(self, mixin_instance, db, site):
        """Test get_page_locale falls back to SEOSettings.default_locale."""
        from wagtail_herald.models import SEOSettings

        # Create settings with custom locale
        SEOSettings.objects.create(site=site, default_locale="fr_FR")

        # Give the mock page a get_site method that returns our site
        mixin_instance.get_site = lambda: site

        result = mixin_instance.get_page_locale()
        assert result == "fr_FR"

    def test_get_page_locale_handles_exception(self, mixin_instance):
        """Test get_page_locale handles exceptions gracefully."""
        # Make get_site raise an exception
        def raise_error():
            raise RuntimeError("Test error")

        mixin_instance.get_site = raise_error

        # Should fall back to default without raising
        result = mixin_instance.get_page_locale()
        assert result == "en_US"
