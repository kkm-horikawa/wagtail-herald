"""
Tests for wagtail-seo-toolkit models.
"""

from wagtail_seo_toolkit.models import SEOSettings


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
