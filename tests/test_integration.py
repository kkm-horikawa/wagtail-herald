"""
Integration tests for wagtail-herald text file endpoints.

Tests the full HTTP request/response cycle through Django's URL routing,
view dispatch, and database interaction using Django TestClient.
"""

import pytest
from django.test import Client
from wagtail.models import Page, Site

from wagtail_herald.models import SEOSettings


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def root_page(db):
    """Get or create the root page."""
    try:
        return Page.objects.get(depth=1)
    except Page.DoesNotExist:
        return Page.add_root(title="Root", slug="root")


@pytest.fixture
def default_site(db, root_page):
    """Get or create the default site bound to localhost."""
    site, _created = Site.objects.get_or_create(
        hostname="localhost",
        defaults={
            "root_page": root_page,
            "is_default_site": True,
            "site_name": "Test Site",
        },
    )
    if site.site_name != "Test Site":
        site.site_name = "Test Site"
        site.save()
    return site


class TestAdsTxtEndpoint:
    """Integration tests for the GET /ads.txt endpoint."""

    @pytest.mark.django_db
    def test_returns_404_when_no_settings_exist(self, client, default_site):
        """GET /ads.txt returns 404 when no SEOSettings record exists.

        Purpose: Verify that the ads.txt endpoint returns a 404 response
                 when no SEOSettings has been created for the site, confirming
                 the full request pipeline (URL routing -> view -> DB lookup)
                 handles the unconfigured state correctly.
        Category: Normal
        Technique: API endpoint
        Integration: GET /ads.txt -> ads_txt view -> Site.find_for_request -> SEOSettings.for_request -> Http404
        Test data:
        - Default Wagtail site (localhost) with no SEOSettings record
        Verification:
        1. Send GET /ads.txt via TestClient
        2. Confirm response status code is 404
        """
        response = client.get("/ads.txt")

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_returns_404_when_ads_txt_field_is_empty(self, client, default_site):
        """GET /ads.txt returns 404 when ads_txt field is blank.

        Purpose: Verify that the endpoint returns 404 when SEOSettings exists
                 but the ads_txt field is empty, confirming the view treats
                 blank content as "not configured" per the ads.txt spec.
        Category: Boundary
        Technique: API endpoint
        Integration: GET /ads.txt -> ads_txt view -> SEOSettings(ads_txt="") -> Http404
        Test data:
        - SEOSettings with empty ads_txt (default value)
        Verification:
        1. Create SEOSettings with empty ads_txt for the default site
        2. Send GET /ads.txt
        3. Confirm response status code is 404
        """
        SEOSettings.objects.create(site=default_site, ads_txt="")

        response = client.get("/ads.txt")

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_returns_200_with_text_plain_when_configured(self, client, default_site):
        """GET /ads.txt returns 200 with text/plain Content-Type when configured.

        Purpose: Verify that the endpoint returns HTTP 200 with the correct
                 text/plain Content-Type header when ads.txt content is
                 configured, ensuring the response is served as a plain text
                 file as required by the ads.txt specification.
        Category: Normal
        Technique: API endpoint
        Integration: GET /ads.txt -> ads_txt view -> SEOSettings.for_request -> HttpResponse(text/plain)
        Test data:
        - SEOSettings with a single ads.txt entry (Google AdSense format)
        Verification:
        1. Create SEOSettings with ads_txt content
        2. Send GET /ads.txt
        3. Confirm response status code is 200
        4. Confirm Content-Type header is text/plain
        """
        SEOSettings.objects.create(
            site=default_site,
            ads_txt="google.com, pub-1234567890, DIRECT, f08c47fec0942fa0",
        )

        response = client.get("/ads.txt")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"

    @pytest.mark.django_db
    def test_returns_exact_configured_content(self, client, default_site):
        """GET /ads.txt returns the exact content stored in SEOSettings.

        Purpose: Verify that the endpoint returns the ads.txt content
                 verbatim from the database, without modification, ensuring
                 ad network verification works correctly with multi-line
                 entries from different ad providers.
        Category: Normal
        Technique: API endpoint
        Integration: GET /ads.txt -> ads_txt view -> SEOSettings.ads_txt -> HttpResponse body
        Test data:
        - Multi-line ads.txt with DIRECT and RESELLER entries from different networks
        Verification:
        1. Create SEOSettings with multi-line ads.txt content
        2. Send GET /ads.txt
        3. Confirm response body matches the stored content exactly
        """
        ads_content = (
            "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0\n"
            "adnetwork.com, pub-9876543210, RESELLER\n"
            "# This is a comment\n"
            "example.com, 12345, DIRECT"
        )
        SEOSettings.objects.create(site=default_site, ads_txt=ads_content)

        response = client.get("/ads.txt")

        assert response.content.decode("utf-8") == ads_content

    @pytest.mark.django_db
    def test_multisite_different_ads_txt_content(self, client, root_page):
        """Different sites serve different ads.txt content.

        Purpose: Verify that the ads.txt endpoint is site-aware and returns
                 different content for different Wagtail sites, confirming
                 the multi-tenancy support via Site.find_for_request and
                 SEOSettings.for_request per-site resolution.
        Category: Normal
        Technique: API endpoint
        Integration: GET /ads.txt (Host: site-a) -> Site.find_for_request -> SEOSettings(site_a)
                     GET /ads.txt (Host: site-b) -> Site.find_for_request -> SEOSettings(site_b)
        Test data:
        - Two sites with different hostnames and different ads.txt content
        Verification:
        1. Create two sites with distinct ads.txt content
        2. Send GET /ads.txt with Host header for site A
        3. Confirm response contains site A's ads.txt content
        4. Send GET /ads.txt with Host header for site B
        5. Confirm response contains site B's ads.txt content
        """
        Site.objects.all().delete()

        child_a = root_page.add_child(title="Site A Home", slug="site-a-home")
        child_b = root_page.add_child(title="Site B Home", slug="site-b-home")

        site_a = Site.objects.create(
            hostname="site-a.example.com",
            root_page=child_a,
            is_default_site=True,
            site_name="Site A",
        )
        site_b = Site.objects.create(
            hostname="site-b.example.com",
            root_page=child_b,
            is_default_site=False,
            site_name="Site B",
        )

        ads_a = "google.com, pub-AAAA, DIRECT, f08c47fec0942fa0"
        ads_b = "google.com, pub-BBBB, DIRECT, f08c47fec0942fa0"
        SEOSettings.objects.create(site=site_a, ads_txt=ads_a)
        SEOSettings.objects.create(site=site_b, ads_txt=ads_b)

        response_a = client.get("/ads.txt", HTTP_HOST="site-a.example.com")
        response_b = client.get("/ads.txt", HTTP_HOST="site-b.example.com")

        assert response_a.status_code == 200
        assert response_a.content.decode("utf-8") == ads_a
        assert response_b.status_code == 200
        assert response_b.content.decode("utf-8") == ads_b

    @pytest.mark.django_db
    def test_multisite_one_configured_one_not(self, client, root_page):
        """One site has ads.txt configured, the other does not.

        Purpose: Verify that multi-site ads.txt configuration is independent:
                 one site returning 200 does not affect another site that
                 should return 404, confirming per-site SEOSettings isolation.
        Category: Abnormal
        Technique: API endpoint
        Integration: GET /ads.txt (configured site) -> 200
                     GET /ads.txt (unconfigured site) -> 404
        Test data:
        - Site A with ads.txt content configured
        - Site B without SEOSettings record
        Verification:
        1. Create two sites, only one with ads.txt content
        2. Confirm the configured site returns 200
        3. Confirm the unconfigured site returns 404
        """
        Site.objects.all().delete()

        child_a = root_page.add_child(title="Configured Home", slug="configured-home")
        child_b = root_page.add_child(
            title="Unconfigured Home", slug="unconfigured-home"
        )

        site_a = Site.objects.create(
            hostname="configured.example.com",
            root_page=child_a,
            is_default_site=True,
            site_name="Configured Site",
        )
        Site.objects.create(
            hostname="unconfigured.example.com",
            root_page=child_b,
            is_default_site=False,
            site_name="Unconfigured Site",
        )

        SEOSettings.objects.create(
            site=site_a,
            ads_txt="google.com, pub-1234567890, DIRECT, f08c47fec0942fa0",
        )

        response_configured = client.get("/ads.txt", HTTP_HOST="configured.example.com")
        response_unconfigured = client.get(
            "/ads.txt", HTTP_HOST="unconfigured.example.com"
        )

        assert response_configured.status_code == 200
        assert response_unconfigured.status_code == 404


class TestAdsTxtIdempotency:
    """Tests for idempotent behavior of the ads.txt endpoint."""

    @pytest.mark.django_db
    def test_repeated_requests_return_same_content(self, client, default_site):
        """Multiple GET /ads.txt requests return identical responses.

        Purpose: Verify that the ads.txt endpoint is idempotent: repeated
                 GET requests return the same content without side effects,
                 ensuring caching proxies and crawlers get consistent results.
        Category: Normal
        Technique: Idempotency
        Integration: GET /ads.txt (x3) -> same HttpResponse
        Test data:
        - SEOSettings with ads.txt content
        Verification:
        1. Create SEOSettings with ads.txt content
        2. Send GET /ads.txt three times
        3. Confirm all responses have identical status code and body
        """
        ads_content = "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0"
        SEOSettings.objects.create(site=default_site, ads_txt=ads_content)

        responses = [client.get("/ads.txt") for _ in range(3)]

        for resp in responses:
            assert resp.status_code == 200
            assert resp.content.decode("utf-8") == ads_content


class TestAdsTxtWithRobotsTxtCoexistence:
    """Tests that ads.txt and robots.txt endpoints coexist correctly."""

    @pytest.mark.django_db
    def test_ads_txt_and_robots_txt_independent(self, client, default_site):
        """ads.txt and robots.txt endpoints serve independently.

        Purpose: Verify that configuring ads.txt does not interfere with
                 robots.txt, and vice versa. Both endpoints should resolve
                 independently through the same URL configuration.
        Category: Normal
        Technique: API endpoint
        Integration: GET /ads.txt -> ads_txt view
                     GET /robots.txt -> robots_txt view
        Test data:
        - SEOSettings with both ads_txt and robots_txt content configured
        Verification:
        1. Create SEOSettings with both ads_txt and robots_txt content
        2. Confirm GET /ads.txt returns ads.txt content
        3. Confirm GET /robots.txt returns robots.txt content
        4. Confirm contents do not leak between endpoints
        """
        ads_content = "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0"
        robots_content = "User-agent: *\nDisallow: /admin/"
        SEOSettings.objects.create(
            site=default_site,
            ads_txt=ads_content,
            robots_txt=robots_content,
        )

        ads_response = client.get("/ads.txt")
        robots_response = client.get("/robots.txt")

        assert ads_response.status_code == 200
        assert ads_response.content.decode("utf-8") == ads_content
        assert ads_response["Content-Type"] == "text/plain"

        assert robots_response.status_code == 200
        assert robots_response.content.decode("utf-8") == robots_content
        assert robots_response["Content-Type"] == "text/plain"


class TestSecurityTxtEndpoint:
    """Integration tests for the GET /.well-known/security.txt endpoint."""

    @pytest.mark.django_db
    def test_returns_404_when_no_settings_exist(self, client, default_site):
        """GET /.well-known/security.txt returns 404 when no SEOSettings record exists.

        Purpose: Verify that the security.txt endpoint returns a 404 response
                 when no SEOSettings has been created for the site, confirming
                 the full request pipeline handles the unconfigured state correctly
                 per RFC 9116 (no sensible default since Contact is mandatory).
        Category: Normal
        Technique: API endpoint
        Integration: GET /.well-known/security.txt -> security_txt view -> Site.find_for_request -> SEOSettings.for_request -> Http404
        Test data:
        - Default Wagtail site (localhost) with no SEOSettings record
        Verification:
        1. Send GET /.well-known/security.txt via TestClient
        2. Confirm response status code is 404
        """
        response = client.get("/.well-known/security.txt")

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_returns_404_when_security_txt_field_is_empty(self, client, default_site):
        """GET /.well-known/security.txt returns 404 when security_txt field is blank.

        Purpose: Verify that the endpoint returns 404 when SEOSettings exists
                 but the security_txt field is empty, confirming the view treats
                 blank content as "not configured" since RFC 9116 requires at
                 minimum the Contact field.
        Category: Boundary
        Technique: API endpoint
        Integration: GET /.well-known/security.txt -> security_txt view -> SEOSettings(security_txt="") -> Http404
        Test data:
        - SEOSettings with empty security_txt (default value)
        Verification:
        1. Create SEOSettings with empty security_txt for the default site
        2. Send GET /.well-known/security.txt
        3. Confirm response status code is 404
        """
        SEOSettings.objects.create(site=default_site, security_txt="")

        response = client.get("/.well-known/security.txt")

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_returns_200_with_text_plain_when_configured(self, client, default_site):
        """GET /.well-known/security.txt returns 200 with text/plain when configured.

        Purpose: Verify that the endpoint returns HTTP 200 with the correct
                 text/plain Content-Type header when security.txt content is
                 configured, ensuring the response is served as a plain text
                 file as required by RFC 9116.
        Category: Normal
        Technique: API endpoint
        Integration: GET /.well-known/security.txt -> security_txt view -> SEOSettings.for_request -> HttpResponse(text/plain)
        Test data:
        - SEOSettings with a minimal security.txt (Contact + Expires per RFC 9116)
        Verification:
        1. Create SEOSettings with security_txt content
        2. Send GET /.well-known/security.txt
        3. Confirm response status code is 200
        4. Confirm Content-Type header is text/plain
        """
        SEOSettings.objects.create(
            site=default_site,
            security_txt="Contact: mailto:security@example.com\nExpires: 2027-01-01T00:00:00z",
        )

        response = client.get("/.well-known/security.txt")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"

    @pytest.mark.django_db
    def test_returns_exact_configured_content(self, client, default_site):
        """GET /.well-known/security.txt returns the exact content stored in SEOSettings.

        Purpose: Verify that the endpoint returns the security.txt content
                 verbatim from the database, without modification, ensuring
                 RFC 9116 compliance with realistic multi-line content including
                 mandatory Contact and Expires fields plus optional fields.
        Category: Normal
        Technique: API endpoint
        Integration: GET /.well-known/security.txt -> security_txt view -> SEOSettings.security_txt -> HttpResponse body
        Test data:
        - Realistic security.txt with Contact, Expires, Encryption, Preferred-Languages, and Policy fields
        Verification:
        1. Create SEOSettings with realistic multi-field security.txt content
        2. Send GET /.well-known/security.txt
        3. Confirm response body matches the stored content exactly
        """
        security_content = (
            "Contact: mailto:security@example.com\n"
            "Expires: 2027-12-31T23:59:59z\n"
            "Encryption: https://example.com/.well-known/pgp-key.txt\n"
            "Preferred-Languages: en, ja\n"
            "Policy: https://example.com/security-policy"
        )
        SEOSettings.objects.create(site=default_site, security_txt=security_content)

        response = client.get("/.well-known/security.txt")

        assert response.content.decode("utf-8") == security_content

    @pytest.mark.django_db
    def test_multisite_different_security_txt_content(self, client, root_page):
        """Different sites serve different security.txt content.

        Purpose: Verify that the security.txt endpoint is site-aware and returns
                 different content for different Wagtail sites, confirming
                 the multi-tenancy support via Site.find_for_request and
                 SEOSettings.for_request per-site resolution.
        Category: Normal
        Technique: API endpoint
        Integration: GET /.well-known/security.txt (Host: site-a) -> Site.find_for_request -> SEOSettings(site_a)
                     GET /.well-known/security.txt (Host: site-b) -> Site.find_for_request -> SEOSettings(site_b)
        Test data:
        - Two sites with different hostnames and different security.txt content
        Verification:
        1. Create two sites with distinct security.txt content
        2. Send GET /.well-known/security.txt with Host header for site A
        3. Confirm response contains site A's security.txt content
        4. Send GET /.well-known/security.txt with Host header for site B
        5. Confirm response contains site B's security.txt content
        """
        Site.objects.all().delete()

        child_a = root_page.add_child(title="Site A Home", slug="sec-site-a-home")
        child_b = root_page.add_child(title="Site B Home", slug="sec-site-b-home")

        site_a = Site.objects.create(
            hostname="site-a.example.com",
            root_page=child_a,
            is_default_site=True,
            site_name="Site A",
        )
        site_b = Site.objects.create(
            hostname="site-b.example.com",
            root_page=child_b,
            is_default_site=False,
            site_name="Site B",
        )

        security_a = (
            "Contact: mailto:security@site-a.example.com\nExpires: 2027-01-01T00:00:00z"
        )
        security_b = (
            "Contact: mailto:security@site-b.example.com\nExpires: 2027-06-01T00:00:00z"
        )
        SEOSettings.objects.create(site=site_a, security_txt=security_a)
        SEOSettings.objects.create(site=site_b, security_txt=security_b)

        response_a = client.get(
            "/.well-known/security.txt", HTTP_HOST="site-a.example.com"
        )
        response_b = client.get(
            "/.well-known/security.txt", HTTP_HOST="site-b.example.com"
        )

        assert response_a.status_code == 200
        assert response_a.content.decode("utf-8") == security_a
        assert response_b.status_code == 200
        assert response_b.content.decode("utf-8") == security_b


class TestSecurityTxtCoexistence:
    """Tests that security.txt coexists with ads.txt and robots.txt independently."""

    @pytest.mark.django_db
    def test_security_txt_ads_txt_robots_txt_independent(self, client, default_site):
        """security.txt, ads.txt, and robots.txt endpoints serve independently.

        Purpose: Verify that configuring security.txt does not interfere with
                 ads.txt or robots.txt, and vice versa. All three endpoints
                 should resolve independently through the same URL configuration.
        Category: Normal
        Technique: API endpoint
        Integration: GET /.well-known/security.txt -> security_txt view
                     GET /ads.txt -> ads_txt view
                     GET /robots.txt -> robots_txt view
        Test data:
        - SEOSettings with all three text file fields configured
        Verification:
        1. Create SEOSettings with security_txt, ads_txt, and robots_txt content
        2. Confirm GET /.well-known/security.txt returns security.txt content
        3. Confirm GET /ads.txt returns ads.txt content
        4. Confirm GET /robots.txt returns robots.txt content
        5. Confirm contents do not leak between endpoints
        """
        security_content = (
            "Contact: mailto:security@example.com\nExpires: 2027-12-31T23:59:59z"
        )
        ads_content = "google.com, pub-1234567890, DIRECT, f08c47fec0942fa0"
        robots_content = "User-agent: *\nDisallow: /admin/"
        SEOSettings.objects.create(
            site=default_site,
            security_txt=security_content,
            ads_txt=ads_content,
            robots_txt=robots_content,
        )

        security_response = client.get("/.well-known/security.txt")
        ads_response = client.get("/ads.txt")
        robots_response = client.get("/robots.txt")

        assert security_response.status_code == 200
        assert security_response.content.decode("utf-8") == security_content
        assert security_response["Content-Type"] == "text/plain"

        assert ads_response.status_code == 200
        assert ads_response.content.decode("utf-8") == ads_content
        assert ads_response["Content-Type"] == "text/plain"

        assert robots_response.status_code == 200
        assert robots_response.content.decode("utf-8") == robots_content
        assert robots_response["Content-Type"] == "text/plain"
