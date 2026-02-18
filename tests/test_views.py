"""
Tests for wagtail-herald views.
"""

import pytest
from django.http import Http404

from wagtail_herald.models import SEOSettings
from wagtail_herald.views import (
    ads_txt,
    get_default_robots_txt,
    robots_txt,
    security_txt,
)


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


class TestAdsTxtView:
    """Tests for the ads_txt view."""

    def test_returns_text_plain_content_type(self, rf, site, db):
        """Test that ads.txt returns text/plain content type.

        Purpose: Verify ads_txt view returns correct Content-Type header
        when ads.txt content is configured.
        Category: Normal
        Target: ads_txt(request)
        Technique: Equivalence partitioning
        Test data: Valid ads.txt content with site configured
        """
        custom_content = "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0"
        SEOSettings.objects.create(site=site, ads_txt=custom_content)

        request = rf.get("/ads.txt")
        request.site = site

        response = ads_txt(request)

        assert response["Content-Type"] == "text/plain"

    def test_returns_custom_content_when_configured(self, rf, site, db):
        """Test custom ads.txt content from SEOSettings.

        Purpose: Verify ads_txt view returns exact content stored in
        SEOSettings.ads_txt field when configured.
        Category: Normal
        Target: ads_txt(request)
        Technique: Equivalence partitioning
        Test data: Multi-line ads.txt with multiple ad network entries
        """
        custom_content = (
            "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0\n"
            "adnetwork.com, pub-9876543210, RESELLER"
        )
        SEOSettings.objects.create(site=site, ads_txt=custom_content)

        request = rf.get("/ads.txt")
        request.site = site

        response = ads_txt(request)
        content = response.content.decode("utf-8")

        assert content == custom_content

    def test_returns_404_when_no_ads_txt_content(self, rf, site, db):
        """Test that ads.txt returns 404 when field is empty.

        Purpose: Verify ads_txt view raises Http404 when ads_txt field
        is empty, unlike robots.txt which returns default content.
        Category: Boundary / Edge case
        Target: ads_txt(request)
        Technique: Boundary value analysis (empty string boundary)
        Test data: SEOSettings with empty ads_txt (default)
        """
        SEOSettings.objects.create(site=site)

        request = rf.get("/ads.txt")
        request.site = site

        with pytest.raises(Http404):
            ads_txt(request)

    def test_returns_404_when_no_settings(self, rf, site, db):
        """Test that ads.txt returns 404 when no SEOSettings exists.

        Purpose: Verify ads_txt view raises Http404 when SEOSettings
        has not been created for the site.
        Category: Abnormal
        Target: ads_txt(request)
        Technique: Equivalence partitioning (no settings partition)
        Test data: Site without SEOSettings
        """
        request = rf.get("/ads.txt")
        request.site = site

        with pytest.raises(Http404):
            ads_txt(request)

    def test_handles_missing_site_gracefully(self, rf, db):
        """Test that view handles missing site without error.

        Purpose: Verify ads_txt view raises Http404 when request
        has no site attribute (e.g., non-Wagtail-managed domain).
        Category: Abnormal
        Target: ads_txt(request)
        Technique: Error guessing (missing site attribute)
        Test data: Request without site attribute
        """
        request = rf.get("/ads.txt")

        with pytest.raises(Http404):
            ads_txt(request)


class TestAdsTxtField:
    """Tests for the ads_txt field in SEOSettings."""

    def test_field_exists(self):
        """Test that ads_txt field exists on SEOSettings.

        Purpose: Verify the ads_txt TextField is defined on the model.
        Category: Normal
        Target: SEOSettings.ads_txt field
        Technique: Equivalence partitioning
        Test data: Model meta inspection
        """
        field = SEOSettings._meta.get_field("ads_txt")
        assert field is not None

    def test_field_is_blank(self):
        """Test that ads_txt field allows blank values.

        Purpose: Verify ads_txt field is optional (blank=True),
        since not all sites use advertising.
        Category: Normal
        Target: SEOSettings.ads_txt field
        Technique: Equivalence partitioning
        Test data: Field meta inspection
        """
        field = SEOSettings._meta.get_field("ads_txt")
        assert field.blank is True

    def test_field_has_help_text(self):
        """Test that ads_txt field has help text.

        Purpose: Verify ads_txt field provides help text for
        admin UI usability.
        Category: Normal
        Target: SEOSettings.ads_txt field
        Technique: Equivalence partitioning
        Test data: Field meta inspection
        """
        field = SEOSettings._meta.get_field("ads_txt")
        assert field.help_text

    def test_default_value_is_empty(self, site, db):
        """Test that ads_txt defaults to empty string.

        Purpose: Verify ads_txt field defaults to empty string,
        which causes the view to return 404 by design.
        Category: Boundary
        Target: SEOSettings.ads_txt field
        Technique: Boundary value analysis
        Test data: Newly created SEOSettings instance
        """
        settings = SEOSettings.objects.create(site=site)
        assert settings.ads_txt == ""


class TestSecurityTxtView:
    """Tests for the security_txt view."""

    def test_returns_text_plain_content_type(self, rf, site, db):
        """Test that security.txt returns text/plain content type.

        Purpose: Verify security_txt view returns correct Content-Type header
        when security.txt content is configured.
        Category: Normal
        Target: security_txt(request)
        Technique: Equivalence partitioning
        Test data: Valid security.txt content with site configured
        """
        custom_content = (
            "Contact: mailto:security@example.com\nExpires: 2027-01-01T00:00:00.000Z"
        )
        SEOSettings.objects.create(site=site, security_txt=custom_content)

        request = rf.get("/.well-known/security.txt")
        request.site = site

        response = security_txt(request)

        assert response["Content-Type"] == "text/plain"

    def test_returns_custom_content_when_configured(self, rf, site, db):
        """Test custom security.txt content from SEOSettings.

        Purpose: Verify security_txt view returns exact content stored in
        SEOSettings.security_txt field when configured, following RFC 9116
        format with Contact and Expires fields.
        Category: Normal
        Target: security_txt(request)
        Technique: Equivalence partitioning
        Test data: Multi-line security.txt with Contact, Expires, and optional fields
        """
        custom_content = (
            "Contact: mailto:security@example.com\n"
            "Contact: https://example.com/security\n"
            "Expires: 2027-01-01T00:00:00.000Z\n"
            "Preferred-Languages: en, ja\n"
            "Canonical: https://example.com/.well-known/security.txt"
        )
        SEOSettings.objects.create(site=site, security_txt=custom_content)

        request = rf.get("/.well-known/security.txt")
        request.site = site

        response = security_txt(request)
        content = response.content.decode("utf-8")

        assert content == custom_content

    def test_returns_404_when_no_security_txt_content(self, rf, site, db):
        """Test that security.txt returns 404 when field is empty.

        Purpose: Verify security_txt view raises Http404 when security_txt field
        is empty, since no sensible default exists (Contact is required by RFC 9116).
        Category: Boundary / Edge case
        Target: security_txt(request)
        Technique: Boundary value analysis (empty string boundary)
        Test data: SEOSettings with empty security_txt (default)
        """
        SEOSettings.objects.create(site=site)

        request = rf.get("/.well-known/security.txt")
        request.site = site

        with pytest.raises(Http404):
            security_txt(request)

    def test_returns_404_when_no_settings(self, rf, site, db):
        """Test that security.txt returns 404 when no SEOSettings exists.

        Purpose: Verify security_txt view raises Http404 when SEOSettings
        has not been created for the site.
        Category: Abnormal
        Target: security_txt(request)
        Technique: Equivalence partitioning (no settings partition)
        Test data: Site without SEOSettings
        """
        request = rf.get("/.well-known/security.txt")
        request.site = site

        with pytest.raises(Http404):
            security_txt(request)

    def test_handles_missing_site_gracefully(self, rf, db):
        """Test that view handles missing site without error.

        Purpose: Verify security_txt view raises Http404 when request
        has no site attribute (e.g., non-Wagtail-managed domain).
        Category: Abnormal
        Target: security_txt(request)
        Technique: Error guessing (missing site attribute)
        Test data: Request without site attribute
        """
        request = rf.get("/.well-known/security.txt")

        with pytest.raises(Http404):
            security_txt(request)


class TestSecurityTxtField:
    """Tests for the security_txt field in SEOSettings."""

    def test_field_exists(self):
        """Test that security_txt field exists on SEOSettings.

        Purpose: Verify the security_txt TextField is defined on the model.
        Category: Normal
        Target: SEOSettings.security_txt field
        Technique: Equivalence partitioning
        Test data: Model meta inspection
        """
        field = SEOSettings._meta.get_field("security_txt")
        assert field is not None

    def test_field_is_blank(self):
        """Test that security_txt field allows blank values.

        Purpose: Verify security_txt field is optional (blank=True),
        since not all sites need a security.txt.
        Category: Normal
        Target: SEOSettings.security_txt field
        Technique: Equivalence partitioning
        Test data: Field meta inspection
        """
        field = SEOSettings._meta.get_field("security_txt")
        assert field.blank is True

    def test_field_has_help_text(self):
        """Test that security_txt field has help text.

        Purpose: Verify security_txt field provides help text for
        admin UI usability, including RFC 9116 reference.
        Category: Normal
        Target: SEOSettings.security_txt field
        Technique: Equivalence partitioning
        Test data: Field meta inspection
        """
        field = SEOSettings._meta.get_field("security_txt")
        assert field.help_text

    def test_default_value_is_empty(self, site, db):
        """Test that security_txt defaults to empty string.

        Purpose: Verify security_txt field defaults to empty string,
        which causes the view to return 404 by design.
        Category: Boundary
        Target: SEOSettings.security_txt field
        Technique: Boundary value analysis
        Test data: Newly created SEOSettings instance
        """
        settings = SEOSettings.objects.create(site=site)
        assert settings.security_txt == ""
