"""Integration tests for SEO context overrides in the seo_head template tag.

Tests the full template rendering pipeline: Django Template engine loads the
wagtail_herald template tags, the seo_head tag reads well-known context keys
(seo_title, seo_description, seo_canonical_url, seo_og_image), passes them
as overrides to build_seo_context(), and the resulting HTML contains the
overridden values in the correct meta/link/title elements.
"""

import pytest
from django.template import Context, Template
from wagtail.models import Site

from wagtail_herald.models import SEOSettings


@pytest.fixture
def _site(db):
    """Get or create the default site for template rendering tests."""
    from wagtail.models import Page

    try:
        root = Page.objects.get(depth=1)
    except Page.DoesNotExist:
        root = Page.add_root(title="Root", slug="root")

    site, _ = Site.objects.get_or_create(
        hostname="localhost",
        defaults={
            "root_page": root,
            "is_default_site": True,
            "site_name": "Test Site",
        },
    )
    if site.site_name != "Test Site":
        site.site_name = "Test Site"
        site.save()
    return site


@pytest.fixture
def request_with_site(rf, _site):
    """Build a minimal request bound to the default site."""
    request = rf.get("/")
    request.site = _site
    return request


@pytest.fixture
def mock_page():
    """A lightweight page-like object with default SEO attributes."""

    class _MockPage:
        title = "Original Page Title"
        seo_title = ""
        search_description = "Original page description"
        full_url = "https://example.com/original/"

    return _MockPage()


TEMPLATE_STRING = "{% load wagtail_herald %}{% seo_head %}"


class TestSeoHeadContextOverrideTitle:
    """Tests that seo_title context key overrides the title in rendered HTML."""

    @pytest.mark.django_db
    def test_title_element_contains_override_title(self, request_with_site, mock_page):
        """seo_head renders the overridden title in the <title> element.

        Purpose: Verify that placing seo_title in the template context causes
                 the rendered <title> tag to contain the override value instead
                 of the page's own title, confirming the full pipeline from
                 context key extraction to HTML output.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=...) -> seo_head tag -> _SEO_CONTEXT_KEYS
                     -> build_seo_context(overrides={"title": ...}) -> seo_head.html
        Test data:
        - Mock page with title "Original Page Title"
        - Context with seo_title="Events Archive"
        - Site with site_name "Test Site"
        Verification:
        1. Render {% seo_head %} with seo_title in context
        2. Confirm <title> contains "Events Archive | Test Site"
        3. Confirm <title> does NOT contain "Original Page Title"
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": "Events Archive",
            }
        )

        html = template.render(context)

        assert "<title>Events Archive | Test Site</title>" in html
        assert (
            "Original Page Title" not in html.split("<title>")[1].split("</title>")[0]
        )

    @pytest.mark.django_db
    def test_og_title_contains_override_title(self, request_with_site, mock_page):
        """seo_head renders the overridden title in og:title meta tag.

        Purpose: Verify that seo_title override propagates to og:title and
                 twitter:title, ensuring social sharing previews show the
                 sub-route title rather than the parent page title.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=...) -> build_seo_context(overrides)
                     -> og_title / twitter_title in seo_head.html
        Test data:
        - Mock page with title "Original Page Title"
        - Context with seo_title="Events Archive"
        Verification:
        1. Render {% seo_head %} with seo_title in context
        2. Confirm og:title contains "Events Archive"
        3. Confirm twitter:title contains "Events Archive"
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": "Events Archive",
            }
        )

        html = template.render(context)

        assert 'property="og:title" content="Events Archive"' in html
        assert 'name="twitter:title" content="Events Archive"' in html


class TestSeoHeadContextOverrideDescription:
    """Tests that seo_description context key overrides description in rendered HTML."""

    @pytest.mark.django_db
    def test_meta_description_contains_override(self, request_with_site, mock_page):
        """seo_head renders the overridden description in meta description.

        Purpose: Verify that placing seo_description in the template context
                 causes the rendered meta description to contain the override
                 value, ensuring search engine snippets for sub-routes show
                 route-specific descriptions.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_description=...) -> seo_head tag
                     -> build_seo_context(overrides={"description": ...})
                     -> seo_head.html meta[name=description]
        Test data:
        - Mock page with search_description "Original page description"
        - Context with seo_description="Browse our upcoming events"
        Verification:
        1. Render {% seo_head %} with seo_description in context
        2. Confirm meta[name=description] contains override text
        3. Confirm og:description and twitter:description also contain override
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_description": "Browse our upcoming events",
            }
        )

        html = template.render(context)

        assert 'name="description" content="Browse our upcoming events"' in html
        assert 'property="og:description" content="Browse our upcoming events"' in html
        assert 'name="twitter:description" content="Browse our upcoming events"' in html

    @pytest.mark.django_db
    def test_original_description_not_present(self, request_with_site, mock_page):
        """seo_head does not render the original description when override is set.

        Purpose: Verify that the original page description is fully replaced
                 by the override, preventing stale or incorrect descriptions
                 from appearing in sub-route meta tags.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_description=...) -> build_seo_context(overrides)
        Test data:
        - Mock page with search_description "Original page description"
        - Context with seo_description="Override description"
        Verification:
        1. Render {% seo_head %} with seo_description in context
        2. Confirm "Original page description" does not appear in meta description
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_description": "Override description",
            }
        )

        html = template.render(context)

        assert "Original page description" not in html


class TestSeoHeadContextOverrideCanonicalUrl:
    """Tests that seo_canonical_url context key overrides canonical URL in rendered HTML."""

    @pytest.mark.django_db
    def test_canonical_link_contains_override_url(self, request_with_site, mock_page):
        """seo_head renders the overridden canonical URL in link[rel=canonical].

        Purpose: Verify that placing seo_canonical_url in the template context
                 causes the rendered canonical link and og:url to contain the
                 override URL, preventing duplicate content issues for sub-routes.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_canonical_url=...) -> seo_head tag
                     -> build_seo_context(overrides={"canonical_url": ...})
                     -> seo_head.html link[rel=canonical] + og:url
        Test data:
        - Mock page with full_url "https://example.com/original/"
        - Context with seo_canonical_url="https://example.com/events/2026/march/"
        Verification:
        1. Render {% seo_head %} with seo_canonical_url in context
        2. Confirm link[rel=canonical] href contains override URL
        3. Confirm og:url contains override URL
        """
        override_url = "https://example.com/events/2026/march/"
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_canonical_url": override_url,
            }
        )

        html = template.render(context)

        assert f'rel="canonical" href="{override_url}"' in html
        assert f'property="og:url" content="{override_url}"' in html

    @pytest.mark.django_db
    def test_original_canonical_url_not_present(self, request_with_site, mock_page):
        """seo_head does not render the original canonical URL when override is set.

        Purpose: Verify that the original page URL is fully replaced by the
                 override in both canonical link and og:url, preventing crawlers
                 from seeing conflicting canonical signals.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_canonical_url=...) -> build_seo_context(overrides)
        Test data:
        - Mock page with full_url "https://example.com/original/"
        - Context with seo_canonical_url="https://example.com/events/"
        Verification:
        1. Render {% seo_head %} with seo_canonical_url in context
        2. Confirm "https://example.com/original/" does not appear in canonical or og:url
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_canonical_url": "https://example.com/events/",
            }
        )

        html = template.render(context)

        assert "https://example.com/original/" not in html


class TestSeoHeadContextOverrideAllKeys:
    """Tests that all override keys work together in a single rendering."""

    @pytest.mark.django_db
    def test_all_overrides_applied_simultaneously(self, request_with_site, mock_page):
        """seo_head applies all context overrides when provided together.

        Purpose: Verify that seo_title, seo_description, and seo_canonical_url
                 can be combined in a single template context, and all three
                 overrides are reflected in the rendered HTML. This simulates
                 the typical RoutablePageMixin sub-route pattern where all SEO
                 fields are overridden at once.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title, seo_description, seo_canonical_url)
                     -> seo_head tag -> _SEO_CONTEXT_KEYS extraction
                     -> build_seo_context(overrides={title, description, canonical_url})
                     -> seo_head.html (all elements)
        Test data:
        - Mock page with default title/description/URL
        - Context with all three overrides set
        Verification:
        1. Render {% seo_head %} with all overrides in context
        2. Confirm <title> uses override title
        3. Confirm meta description uses override description
        4. Confirm canonical URL uses override URL
        5. Confirm OG and Twitter tags use override values
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": "March 2026 Events",
                "seo_description": "All events happening in March 2026",
                "seo_canonical_url": "https://example.com/events/2026/march/",
            }
        )

        html = template.render(context)

        assert "<title>March 2026 Events | Test Site</title>" in html
        assert 'name="description" content="All events happening in March 2026"' in html
        assert 'rel="canonical" href="https://example.com/events/2026/march/"' in html
        assert 'property="og:title" content="March 2026 Events"' in html
        assert (
            'property="og:description" content="All events happening in March 2026"'
            in html
        )
        assert (
            'property="og:url" content="https://example.com/events/2026/march/"' in html
        )
        assert 'name="twitter:title" content="March 2026 Events"' in html
        assert (
            'name="twitter:description" content="All events happening in March 2026"'
            in html
        )


class TestSeoHeadContextOverrideBackwardCompatibility:
    """Tests that existing behavior is unchanged when no overrides are present."""

    @pytest.mark.django_db
    def test_no_overrides_uses_page_values(self, request_with_site, mock_page):
        """seo_head renders page's own SEO values when no context overrides exist.

        Purpose: Verify backward compatibility: when no seo_title,
                 seo_description, or seo_canonical_url keys are in the template
                 context, the rendered HTML uses the page object's attributes
                 as before the override feature was introduced.
        Category: Normal (regression)
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(page=...) without overrides -> seo_head tag
                     -> build_seo_context(overrides={}) -> seo_head.html
        Test data:
        - Mock page with title "Original Page Title", search_description
          "Original page description", full_url "https://example.com/original/"
        - Context WITHOUT any seo_* override keys
        Verification:
        1. Render {% seo_head %} without any override keys in context
        2. Confirm <title> uses page title
        3. Confirm meta description uses page search_description
        4. Confirm canonical URL uses page full_url
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
            }
        )

        html = template.render(context)

        assert "<title>Original Page Title | Test Site</title>" in html
        assert 'name="description" content="Original page description"' in html
        assert 'rel="canonical" href="https://example.com/original/"' in html
        assert 'property="og:title" content="Original Page Title"' in html

    @pytest.mark.django_db
    def test_none_values_are_not_treated_as_overrides(
        self, request_with_site, mock_page
    ):
        """seo_head ignores context keys with None values (not treated as overrides).

        Purpose: Verify that if seo_title or seo_description is explicitly set
                 to None in the template context, it is not treated as an
                 override and the page's original values are used instead.
                 This is important because Context.get() returns None for
                 missing keys, so None must mean "no override".
        Category: Boundary
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=None) -> seo_head tag
                     -> _SEO_CONTEXT_KEYS check (value is not None)
                     -> build_seo_context(overrides={})
        Test data:
        - Mock page with title "Original Page Title"
        - Context with seo_title=None and seo_description=None
        Verification:
        1. Render {% seo_head %} with seo_title=None in context
        2. Confirm <title> uses the page's original title
        3. Confirm meta description uses the page's original description
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": None,
                "seo_description": None,
                "seo_canonical_url": None,
            }
        )

        html = template.render(context)

        assert "<title>Original Page Title | Test Site</title>" in html
        assert 'name="description" content="Original page description"' in html
        assert 'rel="canonical" href="https://example.com/original/"' in html


class TestSeoHeadContextOverridePartial:
    """Tests that partial overrides work (some keys overridden, others use page defaults)."""

    @pytest.mark.django_db
    def test_only_title_overridden_others_from_page(self, request_with_site, mock_page):
        """seo_head uses override for title but page defaults for description and URL.

        Purpose: Verify that overriding only seo_title does not affect
                 description or canonical URL, which should still come from the
                 page object. This supports the common case where a sub-route
                 only needs a different title.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=...) -> build_seo_context(overrides={"title": ...})
                     -> description and canonical_url from page
        Test data:
        - Mock page with all default attributes
        - Context with only seo_title set
        Verification:
        1. Render {% seo_head %} with only seo_title in context
        2. Confirm <title> uses override
        3. Confirm meta description uses page's search_description
        4. Confirm canonical URL uses page's full_url
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": "Custom Sub-Route Title",
            }
        )

        html = template.render(context)

        assert "<title>Custom Sub-Route Title | Test Site</title>" in html
        assert 'name="description" content="Original page description"' in html
        assert 'rel="canonical" href="https://example.com/original/"' in html

    @pytest.mark.django_db
    def test_only_description_overridden_others_from_page(
        self, request_with_site, mock_page
    ):
        """seo_head uses override for description but page defaults for title and URL.

        Purpose: Verify that overriding only seo_description leaves title and
                 canonical URL unchanged from the page object.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_description=...) -> build_seo_context(overrides={"description": ...})
        Test data:
        - Mock page with all default attributes
        - Context with only seo_description set
        Verification:
        1. Render {% seo_head %} with only seo_description in context
        2. Confirm <title> uses page title
        3. Confirm meta description uses override
        4. Confirm canonical URL uses page full_url
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_description": "Custom sub-route description",
            }
        )

        html = template.render(context)

        assert "<title>Original Page Title | Test Site</title>" in html
        assert 'name="description" content="Custom sub-route description"' in html
        assert 'rel="canonical" href="https://example.com/original/"' in html


class TestSeoHeadContextOverrideWithSEOSettings:
    """Tests that overrides work correctly alongside SEOSettings configuration."""

    @pytest.mark.django_db
    def test_overrides_with_custom_title_separator(self, rf, _site):
        """seo_head uses SEOSettings title_separator with overridden title.

        Purpose: Verify that the title separator configured in SEOSettings is
                 used when composing the full title from the override value,
                 confirming that overrides integrate correctly with site-wide
                 SEO configuration.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=...) + SEOSettings(title_separator="-")
                     -> build_seo_context(overrides={"title": ...})
                     -> full_title = "override - Site Name"
        Test data:
        - SEOSettings with title_separator "-"
        - Context with seo_title="Events"
        Verification:
        1. Create SEOSettings with custom title separator
        2. Render {% seo_head %} with seo_title in context
        3. Confirm <title> uses "Events - Test Site" format
        """
        SEOSettings.objects.create(site=_site, title_separator="-")

        request = rf.get("/")
        request.site = _site

        class MockPage:
            title = "Original"
            seo_title = ""
            search_description = ""
            full_url = "https://example.com/"

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request,
                "page": MockPage(),
                "seo_title": "Events",
            }
        )

        html = template.render(context)

        assert "<title>Events - Test Site</title>" in html

    @pytest.mark.django_db
    def test_overrides_with_twitter_handle(self, rf, _site):
        """seo_head renders twitter:site from SEOSettings alongside overridden title.

        Purpose: Verify that SEOSettings fields like twitter_handle are still
                 rendered when context overrides are active, ensuring that
                 per-route overrides and site-wide settings coexist.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title=...) + SEOSettings(twitter_handle=...)
                     -> build_seo_context -> seo_head.html
        Test data:
        - SEOSettings with twitter_handle "mysite"
        - Context with seo_title="Events"
        Verification:
        1. Create SEOSettings with twitter_handle
        2. Render {% seo_head %} with seo_title override
        3. Confirm twitter:site contains @mysite
        4. Confirm twitter:title contains override title
        """
        SEOSettings.objects.create(site=_site, twitter_handle="mysite")

        request = rf.get("/")
        request.site = _site

        class MockPage:
            title = "Original"
            seo_title = ""
            search_description = ""
            full_url = "https://example.com/"

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request,
                "page": MockPage(),
                "seo_title": "Events",
            }
        )

        html = template.render(context)

        assert 'name="twitter:site" content="@mysite"' in html
        assert 'name="twitter:title" content="Events"' in html


class TestSeoHeadContextOverrideRoutablePagePattern:
    """Tests simulating the actual RoutablePageMixin usage pattern."""

    @pytest.mark.django_db
    def test_routable_page_subroute_context_pattern(self, request_with_site):
        """seo_head handles the typical RoutablePageMixin sub-route context.

        Purpose: Verify the end-to-end pattern where a RoutablePageMixin
                 sub-route view sets seo_title, seo_description, and
                 seo_canonical_url in the template context alongside the parent
                 page object. This simulates the documented usage pattern.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: RoutablePageMixin.render() context with page + seo_* keys
                     -> {% seo_head %} -> _SEO_CONTEXT_KEYS extraction
                     -> build_seo_context(overrides) -> seo_head.html
        Test data:
        - Parent page "My Blog" (the RoutablePageMixin page)
        - Sub-route context: seo_title="Posts tagged Python",
          seo_description="All blog posts tagged with Python",
          seo_canonical_url="https://example.com/blog/tags/python/"
        Verification:
        1. Render with the exact context shape a RoutablePageMixin view produces
        2. Confirm all rendered HTML elements use the sub-route overrides
        3. Confirm site_name from the Wagtail site is still appended to title
        """

        class RoutableParentPage:
            title = "My Blog"
            seo_title = ""
            search_description = "Welcome to my blog"
            full_url = "https://example.com/blog/"

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": RoutableParentPage(),
                "seo_title": "Posts tagged Python",
                "seo_description": "All blog posts tagged with Python",
                "seo_canonical_url": "https://example.com/blog/tags/python/",
            }
        )

        html = template.render(context)

        assert "<title>Posts tagged Python | Test Site</title>" in html
        assert 'name="description" content="All blog posts tagged with Python"' in html
        assert 'rel="canonical" href="https://example.com/blog/tags/python/"' in html
        assert 'property="og:title" content="Posts tagged Python"' in html
        assert (
            'property="og:url" content="https://example.com/blog/tags/python/"' in html
        )
        assert "My Blog" not in html.split("<title>")[1].split("</title>")[0]
        assert "Welcome to my blog" not in html

    @pytest.mark.django_db
    def test_self_key_also_resolves_page(self, request_with_site):
        """seo_head resolves page from 'self' context key (Wagtail convention).

        Purpose: Verify that when the template context uses 'self' instead of
                 'page' (as Wagtail templates do by default), the seo_head tag
                 still finds the page and applies overrides correctly.
        Category: Normal (regression)
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(self=page, seo_title=...) -> seo_head tag
                     -> page = context.get("page") or context.get("self")
                     -> build_seo_context(overrides)
        Test data:
        - Page object stored under 'self' key (not 'page')
        - Context with seo_title override
        Verification:
        1. Render with 'self' key containing the page
        2. Confirm override title appears in <title>
        3. Confirm page's search_description is used (no description override)
        """

        class WagtailPage:
            title = "Blog Home"
            seo_title = ""
            search_description = "Blog homepage description"
            full_url = "https://example.com/blog/"

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "self": WagtailPage(),
                "seo_title": "Category: Tech",
            }
        )

        html = template.render(context)

        assert "<title>Category: Tech | Test Site</title>" in html
        assert 'name="description" content="Blog homepage description"' in html


class TestSeoHeadContextOverrideOgImage:
    """Tests that seo_og_image context key overrides OG image in rendered HTML."""

    @pytest.mark.django_db
    def test_og_image_tag_contains_override_image_url(
        self, request_with_site, mock_page
    ):
        """seo_head renders the overridden OG image URL in og:image meta tag.

        Purpose: Verify that placing a Wagtail Image object as seo_og_image in
                 the template context causes the rendered og:image, og:image:width,
                 og:image:height, and twitter:image meta tags to use the override
                 image's rendition URL, bypassing the page's own og_image and the
                 site-wide default_og_image fallback.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_og_image=Image) -> seo_head tag
                     -> _SEO_CONTEXT_KEYS extraction
                     -> build_seo_context(overrides={"og_image": Image})
                     -> _get_og_image_data(og_image_override=Image)
                     -> seo_head.html og:image / twitter:image
        Test data:
        - Mock page with default attributes (no og_image)
        - Mock Wagtail Image with get_rendition returning a mock rendition
          (url="/media/override-og.jpg", width=1200, height=630)
        Verification:
        1. Render {% seo_head %} with seo_og_image in context
        2. Confirm og:image contains the override rendition URL
        3. Confirm og:image:width and og:image:height are present
        4. Confirm twitter:image contains the override rendition URL
        """

        class MockRendition:
            url = "/media/override-og.jpg"
            width = 1200
            height = 630

        class MockImage:
            title = "Override OG Image"
            width = 2400
            height = 1260

            def get_rendition(self, spec):
                return MockRendition()

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_og_image": MockImage(),
            }
        )

        html = template.render(context)

        assert (
            'property="og:image" content="http://testserver/media/override-og.jpg"'
            in html
        )
        assert 'property="og:image:width" content="1200"' in html
        assert 'property="og:image:height" content="630"' in html
        assert (
            'name="twitter:image" content="http://testserver/media/override-og.jpg"'
            in html
        )

    @pytest.mark.django_db
    def test_og_image_alt_uses_override_image_title(self, request_with_site, mock_page):
        """seo_head uses the override image's title as og:image:alt.

        Purpose: Verify that when seo_og_image is provided, the og:image:alt
                 and twitter:image:alt meta tags are populated from the override
                 image's title attribute, not from the page's og_image_alt.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_og_image=Image) -> _get_og_image_data
                     -> alt_text = og_image_override.title
                     -> seo_head.html og:image:alt / twitter:image:alt
        Test data:
        - Mock Image with title "Event Banner 2026"
        Verification:
        1. Render {% seo_head %} with seo_og_image in context
        2. Confirm og:image:alt contains the override image title
        """

        class MockRendition:
            url = "/media/event-banner.jpg"
            width = 1200
            height = 630

        class MockImage:
            title = "Event Banner 2026"
            width = 2400
            height = 1260

            def get_rendition(self, spec):
                return MockRendition()

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_og_image": MockImage(),
            }
        )

        html = template.render(context)

        assert 'property="og:image:alt" content="Event Banner 2026"' in html
        assert 'name="twitter:image:alt" content="Event Banner 2026"' in html

    @pytest.mark.django_db
    def test_none_seo_og_image_not_treated_as_override(
        self, request_with_site, mock_page
    ):
        """seo_head ignores seo_og_image=None and falls back to page/default.

        Purpose: Verify that if seo_og_image is explicitly set to None in the
                 template context, it is not treated as an override and the
                 normal fallback chain (page.og_image -> settings.default_og_image)
                 is used. Since mock_page has no og_image and no SEOSettings
                 default is configured, no og:image tag should appear.
        Category: Boundary
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_og_image=None) -> seo_head tag
                     -> _SEO_CONTEXT_KEYS check (value is not None)
                     -> overrides dict does NOT include og_image
                     -> _get_og_image_data(og_image_override=None) -> fallback chain
        Test data:
        - Mock page with no og_image attribute
        - Context with seo_og_image=None
        Verification:
        1. Render {% seo_head %} with seo_og_image=None in context
        2. Confirm og:image meta tag is NOT present (no image source available)
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_og_image": None,
            }
        )

        html = template.render(context)

        assert 'property="og:image"' not in html
        assert 'name="twitter:image"' not in html

    @pytest.mark.django_db
    def test_og_image_override_takes_priority_over_page_og_image(
        self, request_with_site
    ):
        """seo_head uses seo_og_image override even when page has its own og_image.

        Purpose: Verify that when both the page object has an og_image and
                 seo_og_image is provided in context, the context override wins.
                 This ensures sub-route specific images can replace the parent
                 page's default OG image.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_og_image=OverrideImage) + page.og_image=PageImage
                     -> _get_og_image_data(og_image_override=OverrideImage)
                     -> override takes priority -> seo_head.html
        Test data:
        - Page with og_image returning "/media/page-og.jpg"
        - Context seo_og_image returning "/media/override-og.jpg"
        Verification:
        1. Render {% seo_head %} with both page og_image and context override
        2. Confirm og:image contains the override URL, not the page URL
        """

        class PageRendition:
            url = "/media/page-og.jpg"
            width = 1200
            height = 630

        class PageImage:
            title = "Page Image"
            width = 1200
            height = 630

            def get_rendition(self, spec):
                return PageRendition()

        class OverrideRendition:
            url = "/media/override-og.jpg"
            width = 1200
            height = 630

        class OverrideImage:
            title = "Override Image"
            width = 2400
            height = 1260

            def get_rendition(self, spec):
                return OverrideRendition()

        class PageWithOgImage:
            title = "Page With Image"
            seo_title = ""
            search_description = "A page with its own OG image"
            full_url = "https://example.com/page-with-image/"
            og_image = PageImage()
            og_image_alt = "Page alt text"

            def get_og_image_alt(self):
                return "Page alt text"

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": PageWithOgImage(),
                "seo_og_image": OverrideImage(),
            }
        )

        html = template.render(context)

        assert "override-og.jpg" in html
        assert "page-og.jpg" not in html

    @pytest.mark.django_db
    def test_og_image_override_combined_with_other_overrides(
        self, request_with_site, mock_page
    ):
        """seo_head applies og_image override together with title and description overrides.

        Purpose: Verify that seo_og_image works correctly alongside seo_title,
                 seo_description, and seo_canonical_url, simulating a full
                 RoutablePageMixin sub-route scenario where all SEO fields
                 including the OG image are overridden.
        Category: Normal
        Technique: API endpoint (Django template rendering pipeline)
        Integration: Context(seo_title, seo_description, seo_canonical_url, seo_og_image)
                     -> seo_head tag -> _SEO_CONTEXT_KEYS extraction
                     -> build_seo_context(overrides={title, description, canonical_url, og_image})
                     -> seo_head.html (all elements)
        Test data:
        - Mock page with default attributes
        - All four context override keys provided
        Verification:
        1. Render {% seo_head %} with all overrides in context
        2. Confirm title, description, canonical URL, and og:image all use overrides
        """

        class MockRendition:
            url = "/media/march-events-banner.jpg"
            width = 1200
            height = 630

        class MockImage:
            title = "March Events Banner"
            width = 2400
            height = 1260

            def get_rendition(self, spec):
                return MockRendition()

        template = Template(TEMPLATE_STRING)
        context = Context(
            {
                "request": request_with_site,
                "page": mock_page,
                "seo_title": "March 2026 Events",
                "seo_description": "All events in March 2026",
                "seo_canonical_url": "https://example.com/events/2026/march/",
                "seo_og_image": MockImage(),
            }
        )

        html = template.render(context)

        assert "<title>March 2026 Events | Test Site</title>" in html
        assert 'name="description" content="All events in March 2026"' in html
        assert 'rel="canonical" href="https://example.com/events/2026/march/"' in html
        assert "march-events-banner.jpg" in html
        assert 'property="og:image:alt" content="March Events Banner"' in html
