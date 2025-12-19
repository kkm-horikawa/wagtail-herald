"""
Tests for wagtail-herald views.
"""

from wagtail_herald.models import SEOSettings
from wagtail_herald.views import get_default_robots_txt, robots_txt


class TestRobotsTxtView:
    """Tests for the robots_txt view."""

    def test_returns_text_plain_content_type(self, rf, site, db):
        """Test that robots.txt returns text/plain content type."""
        request = rf.get("/robots.txt")
        request.site = site

        response = robots_txt(request)

        assert response["Content-Type"] == "text/plain"

    def test_returns_default_content_when_no_settings(self, rf, site, db):
        """Test default robots.txt content when SEOSettings is empty."""
        request = rf.get("/robots.txt")
        request.site = site

        response = robots_txt(request)
        content = response.content.decode("utf-8")

        assert "User-agent: *" in content
        assert "Allow: /" in content

    def test_returns_custom_content_when_configured(self, rf, site, db):
        """Test custom robots.txt content from SEOSettings."""
        custom_content = "User-agent: Googlebot\nDisallow: /private/"
        SEOSettings.objects.create(site=site, robots_txt=custom_content)

        request = rf.get("/robots.txt")
        request.site = site

        response = robots_txt(request)
        content = response.content.decode("utf-8")

        assert content == custom_content

    def test_includes_sitemap_in_default(self, rf, site, db):
        """Test that default robots.txt includes sitemap URL."""
        request = rf.get("/robots.txt")
        request.site = site

        response = robots_txt(request)
        content = response.content.decode("utf-8")

        assert "Sitemap:" in content
        assert "/sitemap.xml" in content

    def test_custom_content_does_not_add_sitemap(self, rf, site, db):
        """Test that custom content is returned as-is without auto-sitemap."""
        custom_content = "User-agent: *\nDisallow: /admin/"
        SEOSettings.objects.create(site=site, robots_txt=custom_content)

        request = rf.get("/robots.txt")
        request.site = site

        response = robots_txt(request)
        content = response.content.decode("utf-8")

        # Custom content should not have sitemap auto-added
        assert content == custom_content

    def test_handles_missing_site_gracefully(self, rf, db):
        """Test that view handles missing site without error."""
        request = rf.get("/robots.txt")
        # Don't set request.site

        response = robots_txt(request)

        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"


class TestGetDefaultRobotsTxt:
    """Tests for the get_default_robots_txt helper function."""

    def test_returns_user_agent_allow(self, rf):
        """Test default content includes User-agent and Allow directives."""
        request = rf.get("/robots.txt")

        content = get_default_robots_txt(request)

        assert "User-agent: *" in content
        assert "Allow: /" in content

    def test_includes_sitemap_url(self, rf):
        """Test default content includes sitemap URL."""
        request = rf.get("/robots.txt")

        content = get_default_robots_txt(request)

        assert "Sitemap:" in content
        assert "sitemap.xml" in content


class TestRobotsTxtField:
    """Tests for the robots_txt field in SEOSettings."""

    def test_field_exists(self):
        """Test that robots_txt field exists on SEOSettings."""
        field = SEOSettings._meta.get_field("robots_txt")
        assert field is not None

    def test_field_is_blank(self):
        """Test that robots_txt field allows blank values."""
        field = SEOSettings._meta.get_field("robots_txt")
        assert field.blank is True

    def test_field_has_help_text(self):
        """Test that robots_txt field has help text."""
        field = SEOSettings._meta.get_field("robots_txt")
        assert field.help_text

    def test_default_value_is_empty(self, site, db):
        """Test that robots_txt defaults to empty string."""
        settings = SEOSettings.objects.create(site=site)
        assert settings.robots_txt == ""
