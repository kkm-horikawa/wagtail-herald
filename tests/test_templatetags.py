"""
Tests for wagtail-herald template tags.
"""

from django.template import Context, Template

from wagtail_herald.models import SEOSettings
from wagtail_herald.templatetags.wagtail_herald import (
    _add_article_auto_fields,
    _add_content_auto_fields,
    _add_product_auto_fields,
    _build_breadcrumb_schema,
    _build_organization_schema,
    _build_page_schemas,
    _build_schema_for_type,
    _build_website_schema,
    _deep_merge,
    _filter_empty_values,
    _get_canonical_url,
    _get_image_url,
    _get_logo_url,
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

    def test_tag_renders_without_request(self, db):
        """Test tag renders without request in context."""
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({})  # No request
        html = template.render(context)

        # Should still render title tag
        assert "<title>" in html

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

    def test_tag_renders_without_request(self, db):
        """Test seo_schema renders without request in context."""
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({})  # No request
        html = template.render(context)

        # Should return empty (no schemas can be generated without request)
        assert html.strip() == ""

    def test_tag_renders_without_context(self, rf, db, site):
        """Test tag renders empty when no page with schema_data."""
        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        # Without a page with schema_data, no schemas are rendered
        assert html == ""

    def test_tag_renders_website_schema(self, rf, site):
        """Test tag renders WebSite schema when enabled in schema_data."""

        class MockPage:
            schema_data = {"types": ["WebSite"], "properties": {}}

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert '"@context": "https://schema.org"' in html
        assert '"@type": "WebSite"' in html
        assert '"name": "Test Site"' in html
        assert '"url":' in html

    def test_tag_renders_organization_schema(self, rf, site, db):
        """Test tag renders Organization schema when enabled and configured."""
        SEOSettings.objects.create(
            site=site,
            organization_name="Test Organization",
            organization_type="Corporation",
        )

        class MockPage:
            schema_data = {"types": ["Organization"], "properties": {}}

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
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

        class MockPage:
            schema_data = {"types": ["Organization"], "properties": {}}

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert '"sameAs"' in html
        assert "https://twitter.com/testhandle" in html
        assert "https://facebook.com/testorg" in html

    def test_tag_no_organization_without_name(self, rf, site, db):
        """Test tag doesn't include Organization schema without name even if enabled."""
        SEOSettings.objects.create(
            site=site,
            organization_name="",
            twitter_handle="testhandle",
        )

        class MockPage:
            schema_data = {"types": ["WebSite", "Organization"], "properties": {}}

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
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
        """Test returns None when Site.find_for_request returns None."""
        from unittest.mock import patch

        from wagtail.models import Site

        # Mock Site.find_for_request to return None
        with patch.object(Site, "find_for_request", return_value=None):
            request = rf.get("/")
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

    def test_without_request_no_url(self, site, db):
        """Test organization schema without request has no URL."""
        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
        )
        result = _build_organization_schema(None, settings)

        assert "url" not in result
        assert result["name"] == "Test Org"

    def test_logo_returns_empty_url(self, rf, site, db):
        """Test organization schema when logo get_rendition returns empty URL."""
        request = rf.get("/")

        class MockLogo:
            file = None  # No file attribute

            def get_rendition(self, spec):
                raise Exception("Rendition error")

        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
        )
        settings._organization_logo = MockLogo()
        type(settings).organization_logo = property(
            lambda self: getattr(self, "_organization_logo", None)
        )

        result = _build_organization_schema(request, settings)

        # Logo should not be in schema because URL is empty
        assert "logo" not in result


class TestBuildBreadcrumbSchema:
    """Tests for _build_breadcrumb_schema function."""

    def test_returns_none_for_none_page(self, rf):
        """Test returns None when page is None."""
        request = rf.get("/")
        result = _build_breadcrumb_schema(request, None)
        assert result is None

    def test_returns_none_for_page_without_ancestors(self, rf):
        """Test returns None for page at root level without ancestors."""
        request = rf.get("/")

        class MockPage:
            title = "Home"
            depth = 2

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return []

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())
        assert result is None

    def test_generates_breadcrumb_for_nested_page(self, rf):
        """Test generates valid BreadcrumbList for nested page."""
        request = rf.get("/")

        class MockAncestor:
            title = "Parent Page"
            url = "/parent/"
            live = True

        class MockPage:
            title = "Child Page"
            depth = 3

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockAncestor()]

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        assert result is not None
        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "BreadcrumbList"
        assert len(result["itemListElement"]) == 2

    def test_ancestors_have_item_url(self, rf):
        """Test ancestor items have 'item' URL, current page does not."""
        request = rf.get("/")

        class MockAncestor:
            title = "Parent Page"
            url = "/parent/"
            live = True

        class MockPage:
            title = "Child Page"
            depth = 3

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockAncestor()]

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        # First item (ancestor) should have 'item' URL
        assert "item" in result["itemListElement"][0]

        # Last item (current page) should not have 'item'
        assert "item" not in result["itemListElement"][-1]

    def test_position_is_sequential(self, rf):
        """Test position numbers are sequential starting from 1."""
        request = rf.get("/")

        class MockAncestor1:
            title = "Level 1"
            url = "/level1/"
            live = True

        class MockAncestor2:
            title = "Level 2"
            url = "/level1/level2/"
            live = True

        class MockPage:
            title = "Current Page"
            depth = 4

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockAncestor1(), MockAncestor2()]

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        positions = [item["position"] for item in result["itemListElement"]]
        assert positions == [1, 2, 3]

    def test_skips_unpublished_ancestors(self, rf):
        """Test unpublished ancestors are skipped."""
        request = rf.get("/")

        class MockUnpublishedAncestor:
            title = "Unpublished"
            url = "/unpublished/"
            live = False

        class MockPublishedAncestor:
            title = "Published"
            url = "/published/"
            live = True

        class MockPage:
            title = "Current"
            depth = 4

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockUnpublishedAncestor(), MockPublishedAncestor()]

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        names = [item["name"] for item in result["itemListElement"]]
        assert "Unpublished" not in names
        assert "Published" in names

    def test_seo_schema_includes_breadcrumb(self, rf, site, db):
        """Test seo_schema tag includes breadcrumb for nested pages when enabled."""

        class MockAncestor:
            title = "Parent"
            url = "/parent/"
            live = True

        class MockPage:
            title = "Child"
            depth = 3
            schema_data = {"types": ["BreadcrumbList"], "properties": {}}

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockAncestor()]

                return MockQuerySet()

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert '"@type": "BreadcrumbList"' in html
        assert '"itemListElement"' in html


class TestBuildPageSchemas:
    """Tests for _build_page_schemas function."""

    def test_returns_empty_list_for_none_page(self, rf):
        """Test returns empty list when page is None."""
        request = rf.get("/")
        result = _build_page_schemas(request, None, None)
        assert result == []

    def test_returns_empty_list_without_schema_data(self, rf):
        """Test returns empty list when page has no schema_data."""
        request = rf.get("/")

        class MockPage:
            title = "Test Page"

        result = _build_page_schemas(request, MockPage(), None)
        assert result == []

    def test_returns_empty_list_for_invalid_schema_data(self, rf):
        """Test returns empty list when schema_data is not a dict."""
        request = rf.get("/")

        class MockPage:
            title = "Test Page"
            schema_data = "invalid"

        result = _build_page_schemas(request, MockPage(), None)
        assert result == []

    def test_generates_article_schema(self, rf):
        """Test generates Article schema from schema_data."""
        request = rf.get("/")

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            search_description = "Article description"
            schema_data = {"types": ["Article"], "properties": {}}

        result = _build_page_schemas(request, MockPage(), None)

        assert len(result) == 1
        assert result[0]["@type"] == "Article"
        assert result[0]["name"] == "Test Article"

    def test_skips_site_wide_schemas(self, rf):
        """Test skips WebSite, Organization, BreadcrumbList."""
        request = rf.get("/")

        class MockPage:
            title = "Test Page"
            full_url = "https://example.com/"
            schema_data = {
                "types": ["WebSite", "Organization", "BreadcrumbList", "Article"],
                "properties": {},
            }

        result = _build_page_schemas(request, MockPage(), None)

        # Only Article should be included
        assert len(result) == 1
        assert result[0]["@type"] == "Article"

    def test_merges_custom_properties(self, rf):
        """Test custom properties are merged into schema."""
        request = rf.get("/")

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            schema_data = {
                "types": ["Article"],
                "properties": {"Article": {"articleSection": "Technology"}},
            }

        result = _build_page_schemas(request, MockPage(), None)

        assert result[0]["articleSection"] == "Technology"

    def test_returns_empty_for_empty_types(self, rf):
        """Test returns empty list when types list is empty."""
        request = rf.get("/")

        class MockPage:
            title = "Test Page"
            full_url = "https://example.com/"
            schema_data = {"types": [], "properties": {}}

        result = _build_page_schemas(request, MockPage(), None)

        assert result == []


class TestBuildSchemaForType:
    """Tests for _build_schema_for_type function."""

    def test_includes_basic_fields(self, rf):
        """Test schema includes basic fields."""
        request = rf.get("/")

        class MockPage:
            title = "Test Page"
            full_url = "https://example.com/test/"
            search_description = "Test description"

        result = _build_schema_for_type(request, MockPage(), None, "WebPage", {})

        assert result["@context"] == "https://schema.org"
        assert result["@type"] == "WebPage"
        assert result["name"] == "Test Page"
        assert result["description"] == "Test description"

    def test_article_includes_auto_fields(self, rf):
        """Test Article type includes auto-populated fields."""
        request = rf.get("/")

        class MockOwner:
            username = "testuser"

            def get_full_name(self):
                return "Test User"

        class MockPage:
            title = "Test Article"
            seo_title = ""
            full_url = "https://example.com/article/"
            search_description = ""
            owner = MockOwner()

        result = _build_schema_for_type(request, MockPage(), None, "Article", {})

        assert result["headline"] == "Test Article"
        assert result["author"]["@type"] == "Person"
        assert result["author"]["name"] == "Test User"

    def test_custom_properties_override_auto(self, rf):
        """Test custom properties override auto-populated fields."""
        request = rf.get("/")

        class MockPage:
            title = "Auto Title"
            full_url = "https://example.com/"

        custom = {"name": "Custom Title"}
        result = _build_schema_for_type(request, MockPage(), None, "WebPage", custom)

        assert result["name"] == "Custom Title"


class TestDeepMerge:
    """Tests for _deep_merge function."""

    def test_shallow_merge(self):
        """Test shallow merge of dicts."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested(self):
        """Test deep merge of nested dicts."""
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"y": 3, "z": 4}}
        result = _deep_merge(base, override)

        assert result == {"a": {"x": 1, "y": 3, "z": 4}}

    def test_override_non_dict_with_dict(self):
        """Test override replaces non-dict with dict."""
        base = {"a": 1}
        override = {"a": {"x": 2}}
        result = _deep_merge(base, override)

        assert result == {"a": {"x": 2}}


class TestSeoSchemaWithPageSchemas:
    """Tests for seo_schema tag with page-specific schemas."""

    def test_includes_article_schema(self, rf, site, db):
        """Test seo_schema includes Article schema from page."""

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            schema_data = {"types": ["Article"], "properties": {}}

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert '"@type": "Article"' in html
        assert '"name": "Test Article"' in html

    def test_includes_custom_properties(self, rf, site, db):
        """Test seo_schema includes custom properties."""

        class MockPage:
            title = "Product Page"
            full_url = "https://example.com/product/"
            schema_data = {
                "types": ["Product"],
                "properties": {"Product": {"sku": "PROD-001", "brand": "TestBrand"}},
            }

        request = rf.get("/")
        request.site = site
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request, "page": MockPage()})
        html = template.render(context)

        assert '"@type": "Product"' in html
        assert '"sku": "PROD-001"' in html
        assert '"brand": "TestBrand"' in html


class TestSeoSchemaEmptySchemas:
    """Tests for seo_schema when no schemas are generated."""

    def test_returns_empty_when_no_schemas(self, rf, db):
        """Test seo_schema returns empty string when no schemas can be generated."""
        # Use a request without a site and no page
        request = rf.get("/", HTTP_HOST="unknown.example.com")
        template = Template("{% load wagtail_herald %}{% seo_schema %}")
        context = Context({"request": request})
        html = template.render(context)

        # Should be empty (no JSON-LD script)
        assert html.strip() == ""


class TestBuildOrganizationSchemaWithLogo:
    """Tests for organization schema with logo."""

    def test_includes_logo_url(self, rf, site, db):
        """Test organization schema includes logo URL when set."""
        request = rf.get("/")
        request.site = site

        class MockLogo:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/logo.jpg"

        settings = SEOSettings(
            site=site,
            organization_name="Test Org",
        )
        # Manually set the logo
        settings._organization_logo = MockLogo()
        type(settings).organization_logo = property(
            lambda self: getattr(self, "_organization_logo", None)
        )

        result = _build_organization_schema(request, settings)

        assert "logo" in result
        assert "logo.jpg" in result["logo"]


class TestBreadcrumbSchemaEdgeCases:
    """Tests for breadcrumb schema edge cases."""

    def test_ancestor_without_url(self, rf):
        """Test handles ancestor without URL attribute."""
        request = rf.get("/")

        class MockAncestor:
            title = "Ancestor"
            url = None  # No URL
            live = True

        class MockPage:
            title = "Current"
            depth = 3

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return [MockAncestor()]

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        # Ancestor should not have 'item' key when URL is None
        assert "item" not in result["itemListElement"][0]

    def test_single_item_returns_none(self, rf):
        """Test returns None when only 1 item (need at least 2)."""
        request = rf.get("/")

        class MockPage:
            title = "Current"
            depth = 3

            def get_ancestors(self):
                class MockQuerySet:
                    def filter(self, **kwargs):
                        return []  # No ancestors

                return MockQuerySet()

        result = _build_breadcrumb_schema(request, MockPage())

        # Should return None because only 1 item
        assert result is None

    def test_exception_in_get_ancestors(self, rf):
        """Test handles exception in get_ancestors."""
        request = rf.get("/")

        class MockPage:
            title = "Current"
            depth = 3

            def get_ancestors(self):
                raise Exception("Database error")

        result = _build_breadcrumb_schema(request, MockPage())

        assert result is None


class TestArticleAutoFields:
    """Tests for _add_article_auto_fields function."""

    def test_adds_headline(self, rf):
        """Test adds headline from page title."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockPage:
            title = "Test Headline"
            seo_title = ""

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert schema["headline"] == "Test Headline"

    def test_adds_author_from_owner(self, rf):
        """Test adds author from page owner."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockOwner:
            username = "testuser"

            def get_full_name(self):
                return "Test User"

        class MockPage:
            title = "Test"
            seo_title = ""
            owner = MockOwner()

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert schema["author"]["@type"] == "Person"
        assert schema["author"]["name"] == "Test User"

    def test_uses_username_when_no_full_name(self, rf):
        """Test uses username when get_full_name returns empty."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockOwner:
            username = "testuser"

            def get_full_name(self):
                return ""

        class MockPage:
            title = "Test"
            seo_title = ""
            owner = MockOwner()

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert schema["author"]["name"] == "testuser"

    def test_skips_author_without_owner(self, rf):
        """Test skips author when no owner."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockPage:
            title = "Test"
            seo_title = ""
            owner = None

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert "author" not in schema

    def test_skips_author_when_name_empty(self, rf):
        """Test skips author when owner has no name."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockOwner:
            username = ""

            def get_full_name(self):
                return ""

        class MockPage:
            title = "Test"
            seo_title = ""
            owner = MockOwner()

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert "author" not in schema

    def test_adds_date_published(self, rf):
        """Test adds datePublished from first_published_at."""
        from datetime import datetime, timezone

        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockPage:
            title = "Test"
            seo_title = ""
            first_published_at = datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc)

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert "datePublished" in schema
        assert "2024-01-15" in schema["datePublished"]

    def test_adds_date_modified(self, rf):
        """Test adds dateModified from last_published_at."""
        from datetime import datetime, timezone

        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockPage:
            title = "Test"
            seo_title = ""
            last_published_at = datetime(2024, 2, 20, 14, 0, tzinfo=timezone.utc)

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert "dateModified" in schema
        assert "2024-02-20" in schema["dateModified"]

    def test_adds_publisher_with_logo(self, rf, site, db):
        """Test adds publisher with logo when settings have org and logo."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockLogo:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/logo.jpg"

        class MockPage:
            title = "Test"
            seo_title = ""
            og_image = None

        settings = SEOSettings(
            site=site,
            organization_name="Test Publisher",
        )
        settings._organization_logo = MockLogo()
        type(settings).organization_logo = property(
            lambda self: getattr(self, "_organization_logo", None)
        )

        _add_article_auto_fields(schema, request, MockPage(), settings)

        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Test Publisher"
        assert "logo" in schema["publisher"]

    def test_adds_publisher_without_logo(self, rf, site, db):
        """Test adds publisher without logo when org has no logo."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockPage:
            title = "Test"
            seo_title = ""
            og_image = None

        settings = SEOSettings(
            site=site,
            organization_name="Test Publisher",
        )

        _add_article_auto_fields(schema, request, MockPage(), settings)

        assert schema["publisher"]["@type"] == "Organization"
        assert schema["publisher"]["name"] == "Test Publisher"
        assert "logo" not in schema["publisher"]

    def test_adds_publisher_with_logo_empty_url(self, rf, site, db):
        """Test adds publisher without logo when logo URL is empty."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockLogo:
            file = None

            def get_rendition(self, spec):
                raise Exception("Rendition error")

        class MockPage:
            title = "Test"
            seo_title = ""
            og_image = None

        settings = SEOSettings(
            site=site,
            organization_name="Test Publisher",
        )
        settings._organization_logo = MockLogo()
        type(settings).organization_logo = property(
            lambda self: getattr(self, "_organization_logo", None)
        )

        _add_article_auto_fields(schema, request, MockPage(), settings)

        assert schema["publisher"]["@type"] == "Organization"
        assert "logo" not in schema["publisher"]

    def test_adds_image_from_og_image(self, rf):
        """Test adds image URL from page og_image."""
        request = rf.get("/")
        schema = {"@type": "Article"}

        class MockImage:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/article-image.jpg"
            width = 1200
            height = 630

        class MockPage:
            title = "Test"
            seo_title = ""
            og_image = MockImage()

            def get_og_image_alt(self):
                return "Alt text"

        _add_article_auto_fields(schema, request, MockPage(), None)

        assert "image" in schema
        assert "article-image.jpg" in schema["image"]


class TestProductAutoFields:
    """Tests for _add_product_auto_fields function."""

    def test_adds_image_from_og_image(self, rf):
        """Test adds image URL from page og_image."""
        request = rf.get("/")
        schema = {"@type": "Product"}

        class MockImage:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/product-image.jpg"
            width = 1200
            height = 630

        class MockPage:
            og_image = MockImage()

            def get_og_image_alt(self):
                return "Product alt"

        _add_product_auto_fields(schema, request, MockPage(), None)

        assert "image" in schema
        assert "product-image.jpg" in schema["image"]


class TestContentAutoFields:
    """Tests for _add_content_auto_fields function."""

    def test_adds_image_from_og_image(self, rf):
        """Test adds image URL for content types."""
        request = rf.get("/")
        schema = {"@type": "Event"}

        class MockImage:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/event-image.jpg"
            width = 1200
            height = 630

        class MockPage:
            og_image = MockImage()

            def get_og_image_alt(self):
                return "Event alt"

        _add_content_auto_fields(schema, request, MockPage(), None)

        assert "image" in schema
        assert "event-image.jpg" in schema["image"]

    def test_adds_provider_for_course(self, rf, site, db):
        """Test adds provider for Course schema."""
        request = rf.get("/")
        schema = {"@type": "Course"}

        class MockPage:
            og_image = None

        settings = SEOSettings(site=site, organization_name="Test Academy")

        _add_content_auto_fields(schema, request, MockPage(), settings)

        assert schema["provider"]["@type"] == "Organization"
        assert schema["provider"]["name"] == "Test Academy"

    def test_adds_organizer_for_event(self, rf, site, db):
        """Test adds organizer for Event schema."""
        request = rf.get("/")
        schema = {"@type": "Event"}

        class MockPage:
            og_image = None

        settings = SEOSettings(site=site, organization_name="Event Organizer")

        _add_content_auto_fields(schema, request, MockPage(), settings)

        assert schema["organizer"]["@type"] == "Organization"
        assert schema["organizer"]["name"] == "Event Organizer"

    def test_adds_hiring_organization_for_job(self, rf, site, db):
        """Test adds hiringOrganization for JobPosting schema."""
        request = rf.get("/")
        schema = {"@type": "JobPosting"}

        class MockPage:
            og_image = None

        settings = SEOSettings(site=site, organization_name="Hiring Company")

        _add_content_auto_fields(schema, request, MockPage(), settings)

        assert schema["hiringOrganization"]["@type"] == "Organization"
        assert schema["hiringOrganization"]["name"] == "Hiring Company"

    def test_does_not_override_existing_provider(self, rf, site, db):
        """Test does not override existing provider."""
        request = rf.get("/")
        schema = {"@type": "Course", "provider": {"name": "Existing"}}

        class MockPage:
            og_image = None

        settings = SEOSettings(site=site, organization_name="New Provider")

        _add_content_auto_fields(schema, request, MockPage(), settings)

        # Should keep existing provider
        assert schema["provider"]["name"] == "Existing"

    def test_no_provider_without_organization(self, rf):
        """Test no provider/organizer when no organization name."""
        request = rf.get("/")
        schema = {"@type": "Course"}

        class MockPage:
            og_image = None

        _add_content_auto_fields(schema, request, MockPage(), None)

        assert "provider" not in schema

    def test_no_organizer_without_organization(self, rf):
        """Test no organizer when no organization name."""
        request = rf.get("/")
        schema = {"@type": "Event"}

        class MockPage:
            og_image = None

        _add_content_auto_fields(schema, request, MockPage(), None)

        assert "organizer" not in schema


class TestGetLogoUrl:
    """Tests for _get_logo_url function."""

    def test_returns_empty_for_none_logo(self, rf):
        """Test returns empty string for None logo."""
        request = rf.get("/")
        result = _get_logo_url(request, None)
        assert result == ""

    def test_returns_rendition_url(self, rf):
        """Test returns rendition URL when successful."""
        request = rf.get("/")

        class MockLogo:
            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/logo-112.jpg"

        result = _get_logo_url(request, MockLogo())
        assert "logo-112.jpg" in result

    def test_falls_back_on_rendition_error(self, rf):
        """Test falls back to original URL on rendition error."""
        request = rf.get("/")

        class MockFile:
            url = "/media/original-logo.jpg"

        class MockLogo:
            file = MockFile()

            def get_rendition(self, spec):
                raise Exception("Rendition error")

        result = _get_logo_url(request, MockLogo())
        assert "original-logo.jpg" in result


class TestGetImageUrl:
    """Tests for _get_image_url function."""

    def test_returns_empty_for_none(self, rf):
        """Test returns empty string for None image."""
        request = rf.get("/")
        result = _get_image_url(request, None)
        assert result == ""

    def test_uses_file_url_when_available(self, rf):
        """Test uses image.file.url when available."""
        request = rf.get("/")

        class MockFile:
            url = "/media/images/test.jpg"

        class MockImage:
            url = "/media/wrong.jpg"
            file = MockFile()

        result = _get_image_url(request, MockImage())
        assert "test.jpg" in result

    def test_uses_url_attribute_when_no_file(self, rf):
        """Test uses url attribute when file not available."""
        request = rf.get("/")

        class MockImage:
            url = "/media/direct.jpg"

        result = _get_image_url(request, MockImage())
        assert "direct.jpg" in result


class TestOgImageDataEdgeCases:
    """Tests for _get_og_image_data edge cases."""

    def test_uses_og_image_alt_attribute_when_no_method(self, rf):
        """Test uses og_image_alt attribute when get_og_image_alt not available."""
        request = rf.get("/")

        class MockImage:
            width = 1200
            height = 630

            def get_rendition(self, spec):
                return MockRendition()

        class MockRendition:
            url = "/media/og.jpg"
            width = 1200
            height = 630

        class MockPage:
            og_image = MockImage()
            og_image_alt = "Alt from attribute"
            # No get_og_image_alt method

        result = _get_og_image_data(request, MockPage(), None)

        assert result["alt"] == "Alt from attribute"

    def test_falls_back_on_rendition_error(self, rf):
        """Test falls back to original image on rendition error."""
        request = rf.get("/")

        class MockFile:
            url = "/media/original.jpg"

        class MockImage:
            file = MockFile()
            width = 800
            height = 600

            def get_rendition(self, spec):
                raise Exception("Rendition error")

        class MockPage:
            og_image = MockImage()
            og_image_alt = "Alt text"

            def get_og_image_alt(self):
                return "Alt text"

        result = _get_og_image_data(request, MockPage(), None)

        assert "original.jpg" in result["url"]
        assert result["width"] == 800
        assert result["height"] == 600


class TestMakeAbsoluteUrlEdgeCases:
    """Tests for _make_absolute_url edge cases."""

    def test_returns_relative_url_without_request(self):
        """Test returns relative URL when no request available."""
        result = _make_absolute_url(None, "/media/image.jpg")
        assert result == "/media/image.jpg"


class TestBuildSchemaForTypeContentTypes:
    """Tests for _build_schema_for_type with content types."""

    def test_event_type(self, rf, site, db):
        """Test Event schema generation."""
        request = rf.get("/")

        class MockPage:
            title = "Test Event"
            full_url = "https://example.com/event/"

        settings = SEOSettings(site=site, organization_name="Event Org")

        result = _build_schema_for_type(request, MockPage(), settings, "Event", {})

        assert result["@type"] == "Event"
        assert "organizer" in result

    def test_course_type(self, rf, site, db):
        """Test Course schema generation."""
        request = rf.get("/")

        class MockPage:
            title = "Test Course"
            full_url = "https://example.com/course/"

        settings = SEOSettings(site=site, organization_name="Course Provider")

        result = _build_schema_for_type(request, MockPage(), settings, "Course", {})

        assert result["@type"] == "Course"
        assert "provider" in result

    def test_job_posting_type(self, rf, site, db):
        """Test JobPosting schema generation."""
        request = rf.get("/")

        class MockPage:
            title = "Software Engineer"
            full_url = "https://example.com/jobs/engineer/"

        settings = SEOSettings(site=site, organization_name="Tech Company")

        result = _build_schema_for_type(request, MockPage(), settings, "JobPosting", {})

        assert result["@type"] == "JobPosting"
        assert "hiringOrganization" in result

    def test_recipe_type(self, rf):
        """Test Recipe schema generation."""
        request = rf.get("/")

        class MockPage:
            title = "Chocolate Cake"
            full_url = "https://example.com/recipes/chocolate-cake/"

        result = _build_schema_for_type(request, MockPage(), None, "Recipe", {})

        assert result["@type"] == "Recipe"
        assert result["name"] == "Chocolate Cake"

    def test_howto_type(self, rf):
        """Test HowTo schema generation."""
        request = rf.get("/")

        class MockPage:
            title = "How to Build a Birdhouse"
            full_url = "https://example.com/howto/birdhouse/"

        result = _build_schema_for_type(request, MockPage(), None, "HowTo", {})

        assert result["@type"] == "HowTo"
        assert result["name"] == "How to Build a Birdhouse"


class TestFilterEmptyValues:
    """Tests for _filter_empty_values helper function."""

    def test_none_returns_none(self):
        """None should return None."""
        assert _filter_empty_values(None) is None

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        assert _filter_empty_values("") is None

    def test_non_empty_string_returns_string(self):
        """Non-empty string should return the string."""
        assert _filter_empty_values("hello") == "hello"

    def test_bool_returns_bool(self):
        """Boolean values should be preserved."""
        assert _filter_empty_values(True) is True
        assert _filter_empty_values(False) is False

    def test_int_returns_int(self):
        """Integer values should be preserved."""
        assert _filter_empty_values(0) == 0
        assert _filter_empty_values(42) == 42

    def test_float_returns_float(self):
        """Float values should be preserved."""
        assert _filter_empty_values(0.0) == 0.0
        assert _filter_empty_values(3.14) == 3.14

    def test_empty_list_returns_none(self):
        """Empty list should return None."""
        assert _filter_empty_values([]) is None

    def test_list_with_none_items_returns_none(self):
        """List with only None items should return None."""
        assert _filter_empty_values([None, None]) is None

    def test_list_with_valid_items(self):
        """List with valid items should filter out None."""
        assert _filter_empty_values(["a", None, "b"]) == ["a", "b"]

    def test_nested_list_filtering(self):
        """Nested lists should be filtered recursively."""
        result = _filter_empty_values([{"name": "test"}, {"name": ""}])
        assert result == [{"name": "test"}]

    def test_empty_dict_returns_none(self):
        """Empty dict should return None."""
        assert _filter_empty_values({}) is None

    def test_dict_with_only_type_returns_none(self):
        """Dict with only @type should return None."""
        assert _filter_empty_values({"@type": "Thing"}) is None

    def test_dict_preserves_type_and_context(self):
        """Dict should preserve @type and @context with other data."""
        result = _filter_empty_values(
            {"@type": "Thing", "@context": "https://schema.org", "name": "Test"}
        )
        assert result == {
            "@type": "Thing",
            "@context": "https://schema.org",
            "name": "Test",
        }

    def test_dict_filters_empty_values(self):
        """Dict should filter out empty values."""
        result = _filter_empty_values(
            {"name": "Test", "description": "", "value": None}
        )
        assert result == {"name": "Test"}

    def test_dict_filters_recursively(self):
        """Dict should filter nested objects recursively."""
        result = _filter_empty_values(
            {
                "name": "Test",
                "address": {"street": "123 Main", "city": ""},
            }
        )
        assert result == {"name": "Test", "address": {"street": "123 Main"}}

    def test_other_types_returned_as_is(self):
        """Other types should be returned as-is."""
        # Test with a tuple (not dict, list, str, bool, int, float, or None)
        result = _filter_empty_values((1, 2, 3))
        assert result == (1, 2, 3)


class TestPageLangTemplateTag:
    """Tests for page_lang template tag."""

    def test_page_lang_with_seo_mixin(self, rf, db):
        """Test page_lang returns language from page with seo_locale field."""

        class MockPage:
            seo_locale = "ja_JP"

        request = rf.get("/")
        context = {"request": request, "page": MockPage()}

        from wagtail_herald.templatetags.wagtail_herald import page_lang

        result = page_lang(context)
        assert result == "ja"

    def test_page_lang_fallback_to_settings(self, rf, db, site):
        """Test page_lang falls back to settings default_locale."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import page_lang

        SEOSettings.objects.create(site=site, default_locale="de_DE")

        request = rf.get("/")
        request.site = site
        context = {"request": request, "page": None}

        result = page_lang(context)
        assert result == "de"

    def test_page_lang_default(self, rf, db):
        """Test page_lang returns 'en' when no locale available."""
        from wagtail_herald.templatetags.wagtail_herald import page_lang

        context = {"request": None, "page": None}

        result = page_lang(context)
        assert result == "en"


class TestPageLocaleTemplateTag:
    """Tests for page_locale template tag."""

    def test_page_locale_with_seo_mixin(self, rf, db):
        """Test page_locale returns full locale from page with seo_locale field."""

        class MockPage:
            seo_locale = "ja_JP"

        request = rf.get("/")
        context = {"request": request, "page": MockPage()}

        from wagtail_herald.templatetags.wagtail_herald import page_locale

        result = page_locale(context)
        assert result == "ja_JP"

    def test_page_locale_fallback_to_settings(self, rf, db, site):
        """Test page_locale falls back to settings default_locale."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import page_locale

        SEOSettings.objects.create(site=site, default_locale="fr_FR")

        request = rf.get("/")
        request.site = site
        context = {"request": request, "page": None}

        result = page_locale(context)
        assert result == "fr_FR"

    def test_page_locale_default(self, rf, db):
        """Test page_locale returns 'en_US' when no locale available."""
        from wagtail_herald.templatetags.wagtail_herald import page_locale

        context = {"request": None, "page": None}

        result = page_locale(context)
        assert result == "en_US"


class TestBuildSeoContextLocale:
    """Tests for build_seo_context locale handling."""

    def test_og_locale_from_page(self, rf, db):
        """Test og_locale uses page seo_locale field when available."""
        from wagtail_herald.templatetags.wagtail_herald import build_seo_context

        class MockPage:
            title = "Test Page"
            search_description = ""
            full_url = "https://example.com/test/"
            seo_locale = "ko_KR"

            def get_canonical_url(self, request=None):
                return self.full_url

        request = rf.get("/")
        result = build_seo_context(request, MockPage(), None)

        assert result["og_locale"] == "ko_KR"

    def test_og_locale_fallback_to_settings(self, rf, db, site):
        """Test og_locale falls back to settings when page has no locale."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import build_seo_context

        settings = SEOSettings.objects.create(site=site, default_locale="es_ES")

        class MockPage:
            title = "Test Page"
            search_description = ""
            full_url = "https://example.com/test/"

            def get_canonical_url(self, request=None):
                return self.full_url

        request = rf.get("/")
        request.site = site
        result = build_seo_context(request, MockPage(), settings)

        assert result["og_locale"] == "es_ES"

    def test_og_locale_default(self, rf, db):
        """Test og_locale defaults to en_US."""
        from wagtail_herald.templatetags.wagtail_herald import build_seo_context

        class MockPage:
            title = "Test Page"
            search_description = ""
            full_url = "https://example.com/test/"

            def get_canonical_url(self, request=None):
                return self.full_url

        request = rf.get("/")
        result = build_seo_context(request, MockPage(), None)

        assert result["og_locale"] == "en_US"


class TestSchemaInLanguage:
    """Tests for inLanguage property in Schema.org output."""

    def test_inlanguage_with_page_locale(self, rf):
        """Test inLanguage uses page's seo_locale field."""

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            seo_locale = "ja_JP"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Article", {})

        assert result["inLanguage"] == "ja"

    def test_inlanguage_simplified_chinese(self, rf):
        """Test inLanguage returns zh-Hans for Simplified Chinese."""

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            seo_locale = "zh_CN"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Article", {})

        assert result["inLanguage"] == "zh-Hans"

    def test_inlanguage_traditional_chinese(self, rf):
        """Test inLanguage returns zh-Hant for Traditional Chinese."""

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"
            seo_locale = "zh_TW"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Article", {})

        assert result["inLanguage"] == "zh-Hant"

    def test_inlanguage_fallback_to_settings(self, rf, site, db):
        """Test inLanguage falls back to settings when page has no method."""
        from wagtail_herald.models import SEOSettings

        settings = SEOSettings.objects.create(site=site, default_locale="fr_FR")

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"

        result = _build_schema_for_type(
            rf.get("/"), MockPage(), settings, "Article", {}
        )

        assert result["inLanguage"] == "fr"

    def test_inlanguage_fallback_to_english(self, rf):
        """Test inLanguage defaults to 'en' when no locale available."""

        class MockPage:
            title = "Test Article"
            full_url = "https://example.com/article/"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Article", {})

        assert result["inLanguage"] == "en"

    def test_inlanguage_not_added_to_person(self, rf):
        """Test inLanguage is NOT added to Person schema type."""

        class MockPage:
            title = "John Doe"
            full_url = "https://example.com/person/"
            seo_locale = "ja_JP"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Person", {})

        assert "inLanguage" not in result

    def test_inlanguage_in_blogposting(self, rf):
        """Test inLanguage is added to BlogPosting."""

        class MockPage:
            title = "My Blog Post"
            full_url = "https://example.com/blog/post/"
            seo_locale = "de_DE"

        result = _build_schema_for_type(
            rf.get("/"), MockPage(), None, "BlogPosting", {}
        )

        assert result["inLanguage"] == "de"

    def test_inlanguage_in_newsarticle(self, rf):
        """Test inLanguage is added to NewsArticle."""

        class MockPage:
            title = "News Article"
            full_url = "https://example.com/news/article/"
            seo_locale = "ko_KR"

        result = _build_schema_for_type(
            rf.get("/"), MockPage(), None, "NewsArticle", {}
        )

        assert result["inLanguage"] == "ko"

    def test_inlanguage_in_event(self, rf):
        """Test inLanguage is added to Event."""

        class MockPage:
            title = "Conference 2024"
            full_url = "https://example.com/events/conference/"
            seo_locale = "es_ES"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Event", {})

        assert result["inLanguage"] == "es"

    def test_inlanguage_in_product(self, rf):
        """Test inLanguage is added to Product."""

        class MockPage:
            title = "Super Widget"
            full_url = "https://example.com/products/widget/"
            seo_locale = "pt_BR"

        result = _build_schema_for_type(rf.get("/"), MockPage(), None, "Product", {})

        assert result["inLanguage"] == "pt"

    def test_inlanguage_settings_chinese_simplified(self, rf, site, db):
        """Test settings-based Chinese Simplified returns zh-Hans."""
        from wagtail_herald.models import SEOSettings

        settings = SEOSettings.objects.create(site=site, default_locale="zh_CN")

        class MockPage:
            title = "Test"
            full_url = "https://example.com/"

        result = _build_schema_for_type(
            rf.get("/"), MockPage(), settings, "Article", {}
        )

        assert result["inLanguage"] == "zh-Hans"

    def test_inlanguage_settings_chinese_traditional(self, rf, site, db):
        """Test settings-based Chinese Traditional returns zh-Hant."""
        from wagtail_herald.models import SEOSettings

        settings = SEOSettings.objects.create(site=site, default_locale="zh_TW")

        class MockPage:
            title = "Test"
            full_url = "https://example.com/"

        result = _build_schema_for_type(
            rf.get("/"), MockPage(), settings, "Article", {}
        )

        assert result["inLanguage"] == "zh-Hant"


class TestSeoBodyTemplateTag:
    """Tests for the seo_body template tag."""

    def test_tag_is_registered(self):
        """Test that seo_body tag can be loaded."""
        template = Template("{% load wagtail_herald %}{% seo_body %}")
        assert template is not None

    def test_tag_renders_without_request(self, db):
        """Test seo_body renders without request in context."""
        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({})  # No request
        html = template.render(context)

        # Should render empty (no GTM without settings)
        assert "googletagmanager" not in html

    def test_tag_renders_gtm_noscript(self, rf, site, db):
        """Test seo_body renders GTM noscript when configured."""
        SEOSettings.objects.create(site=site, gtm_container_id="GTM-TEST123")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "<noscript>" in html
        assert "googletagmanager.com/ns.html?id=GTM-TEST123" in html
        assert 'style="display:none;visibility:hidden"' in html

    def test_tag_empty_when_no_gtm(self, rf, site, db):
        """Test seo_body returns empty when GTM not configured."""
        SEOSettings.objects.create(site=site, gtm_container_id="")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "googletagmanager" not in html

    def test_tag_renders_custom_body_end_html(self, rf, site, db):
        """Test seo_body renders custom body end HTML when configured."""
        SEOSettings.objects.create(
            site=site,
            custom_body_end_html='<script src="https://widget.example.com/chat.js"></script>',
        )

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})
        html = template.render(context)

        assert '<script src="https://widget.example.com/chat.js"></script>' in html

    def test_tag_empty_when_no_custom_body_end(self, rf, site, db):
        """Test seo_body doesn't render custom HTML when not configured."""
        SEOSettings.objects.create(site=site, custom_body_end_html="")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})
        html = template.render(context)

        assert html.strip() == ""

    def test_tag_renders_both_gtm_and_custom_body(self, rf, site, db):
        """Test seo_body renders both GTM noscript and custom body HTML."""
        SEOSettings.objects.create(
            site=site,
            gtm_container_id="GTM-TEST123",
            custom_body_end_html='<div id="chat-widget"></div>',
        )

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "googletagmanager.com/ns.html?id=GTM-TEST123" in html
        assert '<div id="chat-widget"></div>' in html


class TestGtmInSeoHead:
    """Tests for GTM script in seo_head template tag."""

    def test_seo_head_renders_gtm_script(self, rf, site, db):
        """Test seo_head renders GTM script when configured."""
        SEOSettings.objects.create(site=site, gtm_container_id="GTM-ABC123")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "googletagmanager.com/gtm.js?id=" in html
        assert "GTM-ABC123" in html
        assert "dataLayer" in html

    def test_seo_head_no_gtm_when_empty(self, rf, site, db):
        """Test seo_head doesn't render GTM when not configured."""
        SEOSettings.objects.create(site=site, gtm_container_id="")

        request = rf.get("/")
        request.site = site

        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request})
        html = template.render(context)

        assert "googletagmanager.com/gtm.js" not in html

    def test_build_seo_context_includes_gtm(self, rf, site, db):
        """Test build_seo_context includes gtm_container_id."""
        settings = SEOSettings.objects.create(site=site, gtm_container_id="GTM-XYZ789")

        request = rf.get("/")
        request.site = site

        result = build_seo_context(request, None, settings)

        assert result["gtm_container_id"] == "GTM-XYZ789"

    def test_build_seo_context_empty_gtm(self, rf, site, db):
        """Test build_seo_context handles empty gtm_container_id."""
        settings = SEOSettings.objects.create(site=site, gtm_container_id="")

        request = rf.get("/")
        request.site = site

        result = build_seo_context(request, None, settings)

        assert result["gtm_container_id"] == ""


class TestGetSchemaLanguageHelper:
    """Tests for _get_schema_language helper function."""

    def test_uses_page_seo_locale(self, rf):
        """Test helper uses page's seo_locale field."""
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        class MockPage:
            seo_locale = "ja_JP"

        result = _get_schema_language(MockPage(), None)
        assert result == "ja"

    def test_fallback_to_settings_japanese(self, rf, site, db):
        """Test helper falls back to settings for Japanese."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        settings = SEOSettings.objects.create(site=site, default_locale="ja_JP")

        class MockPage:
            pass

        result = _get_schema_language(MockPage(), settings)
        assert result == "ja"

    def test_fallback_to_settings_simplified_chinese(self, rf, site, db):
        """Test helper falls back to settings for Simplified Chinese."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        settings = SEOSettings.objects.create(site=site, default_locale="zh_CN")

        class MockPage:
            pass

        result = _get_schema_language(MockPage(), settings)
        assert result == "zh-Hans"

    def test_fallback_to_settings_traditional_chinese(self, rf, site, db):
        """Test helper falls back to settings for Traditional Chinese."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        settings = SEOSettings.objects.create(site=site, default_locale="zh_TW")

        class MockPage:
            pass

        result = _get_schema_language(MockPage(), settings)
        assert result == "zh-Hant"

    def test_fallback_to_english(self, rf):
        """Test helper falls back to 'en' when nothing available."""
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        class MockPage:
            pass

        result = _get_schema_language(MockPage(), None)
        assert result == "en"

    def test_no_page(self, rf):
        """Test helper handles None page."""
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        result = _get_schema_language(None, None)
        assert result == "en"

    def test_settings_with_empty_locale(self, rf, site, db):
        """Test helper handles settings with empty default_locale."""
        from wagtail_herald.models import SEOSettings
        from wagtail_herald.templatetags.wagtail_herald import _get_schema_language

        settings = SEOSettings.objects.create(site=site, default_locale="")

        class MockPage:
            pass

        result = _get_schema_language(MockPage(), settings)
        assert result == "en"


class TestGetSeoSettingsCaching:
    """Tests for SEOSettings request-level caching."""

    def test_returns_none_for_none_request(self):
        """Test that None request returns None."""
        from wagtail_herald.templatetags.wagtail_herald import get_seo_settings

        result = get_seo_settings(None)
        assert result is None

    def test_caches_on_request(self, rf, site, db):
        """Test that settings are cached on request object."""
        from wagtail_herald.templatetags.wagtail_herald import (
            _SEO_SETTINGS_CACHE_ATTR,
            get_seo_settings,
        )

        SEOSettings.objects.create(site=site, organization_name="Test Org")

        request = rf.get("/")
        request.site = site

        # First call should set cache
        result1 = get_seo_settings(request)
        assert result1 is not None
        assert result1.organization_name == "Test Org"
        assert hasattr(request, _SEO_SETTINGS_CACHE_ATTR)

        # Second call should return cached value
        result2 = get_seo_settings(request)
        assert result2 is result1  # Same object

    def test_multiple_tags_use_same_settings(self, rf, site, db):
        """Test that multiple template tags use the same cached settings."""
        SEOSettings.objects.create(site=site, gtm_container_id="GTM-TEST123")

        request = rf.get("/")
        request.site = site

        # Render template with multiple tags
        template = Template(
            "{% load wagtail_herald %}{% seo_head %}{% seo_body %}{% seo_schema %}"
        )
        context = Context({"request": request})
        template.render(context)

        # Verify cache was set
        from wagtail_herald.templatetags.wagtail_herald import _SEO_SETTINGS_CACHE_ATTR

        assert hasattr(request, _SEO_SETTINGS_CACHE_ATTR)
