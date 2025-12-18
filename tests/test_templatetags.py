"""
Tests for wagtail-herald template tags.
"""

from django.template import Context, Template

from wagtail_herald.models import SEOSettings
from wagtail_herald.templatetags.wagtail_herald import (
    _build_organization_schema,
    _build_website_schema,
    _get_canonical_url,
    _get_og_image_data,
    _get_page_title,
    _get_robots_meta,
    _make_absolute_url,
    build_seo_context,
)


class TestSeoHeadTemplateTag:
    """Tests for the seo_head template tag."""

    def test_tag_is_registered(self):
        """Test that seo_head tag can be loaded."""
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        assert template is not None

    def test_tag_renders_without_context(self, rf, db, site):
        """Test tag renders with minimal context."""
        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "<title>" in html
        assert 'property="og:type"' in html

    def test_tag_renders_title(self, rf, site):
        """Test tag renders page title."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert "<title>Test Page | Test Site</title>" in html

    def test_tag_renders_seo_title_override(self, rf, site):
        """Test tag uses seo_title when available."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Regular Title"
            seo_title = "SEO Title"

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert "SEO Title | Test Site" in html

    def test_tag_renders_description(self, rf, site):
        """Test tag renders meta description."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = "This is a test description"

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'name="description"' in html
        assert "This is a test description" in html

    def test_tag_renders_og_tags(self, rf, site):
        """Test tag renders Open Graph tags."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = "Test description"
            full_url = "https://example.com/test/"

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'property="og:type" content="website"' in html
        assert 'property="og:title" content="Test Page"' in html
        assert 'property="og:locale"' in html

    def test_tag_renders_twitter_card(self, rf, site):
        """Test tag renders Twitter Card tags."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = ""

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'name="twitter:card" content="summary_large_image"' in html

    def test_tag_renders_twitter_site(self, rf, site, db):
        """Test tag renders twitter:site when configured."""
        SEOSettings.objects.create(site=site, twitter_handle="testhandle")

        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = ""

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'name="twitter:site" content="@testhandle"' in html

    def test_tag_renders_robots_noindex(self, rf, site):
        """Test tag renders robots meta for noindex pages."""
        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = ""
            noindex = True
            nofollow = False

            def get_robots_meta(self):
                return "noindex"

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'name="robots" content="noindex"' in html

    def test_tag_renders_canonical_url(self, rf, site):
        """Test tag renders canonical link."""
        request = rf.get("/test/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""
            search_description = ""
            full_url = "https://example.com/test/"

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert 'rel="canonical"' in html
        assert "https://example.com/test/" in html

    def test_tag_renders_verification_codes(self, rf, site, db):
        """Test tag renders site verification meta tags."""
        SEOSettings.objects.create(
            site=site,
            google_site_verification="google123",
            bing_site_verification="bing456",
        )

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert 'name="google-site-verification" content="google123"' in html
        assert 'name="msvalidate.01" content="bing456"' in html

    def test_tag_renders_custom_head_html(self, rf, site, db):
        """Test tag renders custom head HTML."""
        SEOSettings.objects.create(
            site=site,
            custom_head_html='<meta name="custom" content="value">',
        )

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '<meta name="custom" content="value">' in html

    def test_tag_uses_configured_separator(self, rf, site, db):
        """Test tag uses configured title separator."""
        SEOSettings.objects.create(site=site, title_separator="-")

        request = rf.get("/")
        request.site = site

        class MockPage:
            title = "Test Page"
            seo_title = ""

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert "<title>Test Page - Test Site</title>" in html

    def test_tag_uses_configured_locale(self, rf, site, db):
        """Test tag uses configured default locale."""
        SEOSettings.objects.create(site=site, default_locale="ja_JP")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert 'property="og:locale" content="ja_JP"' in html


class TestBuildSeoContext:
    """Tests for build_seo_context function."""

    def test_returns_dict(self, rf, site):
        """Test function returns a dictionary."""
        request = rf.get("/")
        request.site = site
        result = build_seo_context(request, None, None)
        assert isinstance(result, dict)

    def test_contains_required_keys(self, rf, site):
        """Test result contains all required keys."""
        request = rf.get("/")
        request.site = site
        result = build_seo_context(request, None, None)

        required_keys = [
            "title",
            "description",
            "canonical_url",
            "robots",
            "og_type",
            "og_title",
            "og_locale",
            "twitter_card",
        ]

        for key in required_keys:
            assert key in result

    def test_handles_none_page(self, rf, site):
        """Test function handles None page gracefully."""
        request = rf.get("/")
        request.site = site
        result = build_seo_context(request, None, None)

        assert result["title"] == " | Test Site"
        assert result["og_title"] == ""


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_page_title_with_title(self):
        """Test _get_page_title returns title."""

        class MockPage:
            title = "Page Title"
            seo_title = ""

        result = _get_page_title(MockPage())
        assert result == "Page Title"

    def test_get_page_title_prefers_seo_title(self):
        """Test _get_page_title prefers seo_title."""

        class MockPage:
            title = "Page Title"
            seo_title = "SEO Title"

        result = _get_page_title(MockPage())
        assert result == "SEO Title"

    def test_get_page_title_with_none(self):
        """Test _get_page_title handles None."""
        result = _get_page_title(None)
        assert result == ""

    def test_get_canonical_url_uses_method(self, rf):
        """Test _get_canonical_url uses page method."""
        request = rf.get("/test/")

        class MockPage:
            def get_canonical_url(self, request):
                return "https://example.com/canonical/"

        result = _get_canonical_url(request, MockPage())
        assert result == "https://example.com/canonical/"

    def test_get_canonical_url_falls_back_to_full_url(self, rf):
        """Test _get_canonical_url falls back to full_url."""
        request = rf.get("/test/")

        class MockPage:
            full_url = "https://example.com/full/"

        result = _get_canonical_url(request, MockPage())
        assert result == "https://example.com/full/"

    def test_get_robots_meta_uses_method(self):
        """Test _get_robots_meta uses page method."""

        class MockPage:
            def get_robots_meta(self):
                return "noindex, nofollow"

        result = _get_robots_meta(MockPage())
        assert result == "noindex, nofollow"

    def test_get_robots_meta_with_none(self):
        """Test _get_robots_meta handles None."""
        result = _get_robots_meta(None)
        assert result == ""

    def test_make_absolute_url_already_absolute(self, rf):
        """Test _make_absolute_url with already absolute URL."""
        request = rf.get("/")
        result = _make_absolute_url(request, "https://example.com/path/")
        assert result == "https://example.com/path/"

    def test_make_absolute_url_relative(self, rf):
        """Test _make_absolute_url converts relative URL."""
        request = rf.get("/")
        result = _make_absolute_url(request, "/media/image.jpg")
        assert result == "http://testserver/media/image.jpg"

    def test_make_absolute_url_empty(self, rf):
        """Test _make_absolute_url handles empty string."""
        request = rf.get("/")
        result = _make_absolute_url(request, "")
        assert result == ""


class TestOgImageData:
    """Tests for _get_og_image_data function."""

    def test_returns_empty_dict_when_no_image(self, rf):
        """Test returns empty values when no image available."""
        request = rf.get("/")
        result = _get_og_image_data(request, None, None)

        assert result["url"] == ""
        assert result["alt"] == ""
        assert result["width"] == ""
        assert result["height"] == ""

    def test_uses_page_og_image(self, rf):
        """Test uses page og_image when available."""
        request = rf.get("/")

        class MockImage:
            width = 1200
            height = 630

            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/og-image.jpg"
            width = 1200
            height = 630

        class MockPage:
            og_image = MockImage()
            og_image_alt = "Test alt"

            def get_og_image_alt(self):
                return "Test alt"

        result = _get_og_image_data(request, MockPage(), None)

        assert "/media/og-image.jpg" in result["url"]
        assert result["alt"] == "Test alt"

    def test_falls_back_to_settings_default(self, rf, site, db):
        """Test falls back to settings default_og_image."""
        request = rf.get("/")
        request.site = site

        class MockImage:
            width = 1200
            height = 630

            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/default-og.jpg"
            width = 1200
            height = 630

        class MockPage:
            og_image = None

        # Create settings with mock image
        settings = SEOSettings(
            site=site,
            default_og_image_alt="Default alt",
        )
        settings._default_og_image_mock = MockImage()

        # Patch the image access
        type(settings).default_og_image = property(
            lambda self: getattr(self, "_default_og_image_mock", None)
        )

        result = _get_og_image_data(request, MockPage(), settings)

        assert result["alt"] == "Default alt"


class TestSeoSchemaTemplateTag:
    """Tests for the seo_schema template tag."""

    def test_tag_is_registered(self):
        """Test that seo_schema tag can be loaded."""
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        assert template is not None

    def test_tag_renders_without_context(self, rf, db, site):
        """Test tag renders with minimal context."""
        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        assert 'type="application/ld+json"' in html
        assert '"@type": "WebSite"' in html

    def test_tag_renders_website_schema(self, rf, site):
        """Test tag renders WebSite schema."""
        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '"@context": "https://schema.org"' in html
        assert '"@type": "WebSite"' in html
        assert '"name": "Test Site"' in html
        assert '"url":' in html

    def test_tag_renders_organization_schema(self, rf, site, db):
        """Test tag renders Organization schema when configured."""
        SEOSettings.objects.create(
            site=site,
            organization_name="Test Organization",
            organization_type="Corporation",
        )

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '"@type": "Corporation"' in html
        assert '"name": "Test Organization"' in html

    def test_tag_includes_same_as(self, rf, site, db):
        """Test tag includes sameAs array with social profiles."""
        SEOSettings.objects.create(
            site=site,
            organization_name="Test Org",
            twitter_handle="testhandle",
            facebook_url="https://facebook.com/testorg",
        )

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '"sameAs"' in html
        assert "https://twitter.com/testhandle" in html
        assert "https://facebook.com/testorg" in html

    def test_tag_no_organization_without_name(self, rf, site, db):
        """Test tag doesn't include Organization schema without name."""
        SEOSettings.objects.create(
            site=site,
            organization_name="",
            twitter_handle="testhandle",
        )

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '"@type": "WebSite"' in html
        assert '"@type": "Organization"' not in html


class TestBuildWebsiteSchema:
    """Tests for _build_website_schema function."""

    def test_returns_none_without_request(self):
        """Test returns None when no request."""
        result = _build_website_schema(None)
        assert result is None

    def test_returns_none_without_site(self, rf, db):
        """Test returns None when no site matches request."""
        # Use a hostname that doesn't match any site
        request = rf.get("/", HTTP_HOST="unknown.example.com")
        result = _build_website_schema(request)
        assert result is None

    def test_returns_none_without_site_name(self, rf, site):
        """Test returns None when site has no name."""
        site.site_name = ""
        site.save()
        request = rf.get("/")
        result = _build_website_schema(request)
        assert result is None

    def test_returns_schema_with_site(self, rf, site):
        """Test returns valid schema with site."""
        request = rf.get("/")
        result = _build_website_schema(request)

        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "WebSite"
        assert result["name"] == "Test Site"
        assert "url" in result


class TestBuildOrganizationSchema:
    """Tests for _build_organization_schema function."""

    def test_returns_none_without_name(self, rf, site, db):
        """Test returns None when no organization name."""
        settings = SEOSettings(site=site, organization_name="")
        result = _build_organization_schema(rf.get("/"), settings)
        assert result is None

    def test_returns_schema_with_name(self, rf, site, db):
        """Test returns valid schema with organization name."""
        request = rf.get("/")
        request.site = site
        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
            organization_type="Corporation",
        )
        result = _build_organization_schema(request, settings)

        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "Corporation"
        assert result["name"] == "Test Org"

    def test_includes_twitter_in_same_as(self, rf, site, db):
        """Test includes Twitter in sameAs."""
        request = rf.get("/")
        request.site = site
        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
            twitter_handle="testhandle",
        )
        result = _build_organization_schema(request, settings)

        assert "sameAs" in result
        assert "https://twitter.com/testhandle" in result["sameAs"]

    def test_includes_facebook_in_same_as(self, rf, site, db):
        """Test includes Facebook in sameAs."""
        request = rf.get("/")
        request.site = site
        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
            facebook_url="https://facebook.com/testorg",
        )
        result = _build_organization_schema(request, settings)

        assert "sameAs" in result
        assert "https://facebook.com/testorg" in result["sameAs"]

    def test_no_same_as_without_social(self, rf, site, db):
        """Test no sameAs when no social profiles."""
        request = rf.get("/")
        request.site = site
        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
        )
        result = _build_organization_schema(request, settings)

        assert "sameAs" not in result
