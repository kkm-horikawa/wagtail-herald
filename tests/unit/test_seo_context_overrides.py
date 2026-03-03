"""Tests for SEO context overrides in build_seo_context and _get_og_image_data.

Verifies that per-route override values (title, description, canonical_url,
og_image) take priority over page-level values when passed to
build_seo_context(), and that _get_og_image_data() respects og_image_override.

## Decision Table: DT-OVERRIDE-FILTERING

| ID  | override key | override value | expected behavior        |
|-----|-------------|----------------|--------------------------|
| DT1 | title       | "Custom"       | uses override value      |
| DT2 | title       | ""             | uses empty string        |
| DT3 | title       | None           | falls back to page value |
| DT4 | description | "Custom desc"  | uses override value      |
| DT5 | description | ""             | uses empty string        |
| DT6 | description | None           | falls back to page value |
| DT7 | canonical   | "https://..."  | uses override value      |
| DT8 | canonical   | None           | falls back to page value |
"""

from __future__ import annotations

from unittest import mock

import pytest

from wagtail_herald.templatetags.wagtail_herald import (
    _get_og_image_data,
    build_seo_context,
)


class _MockPage:
    """Minimal mock page with SEO-relevant attributes."""

    title = "Page Title"
    seo_title = ""
    search_description = "Page description"
    full_url = "https://example.com/page/"


class _MockPageWithSeoTitle(_MockPage):
    seo_title = "SEO Title"


class _MockRendition:
    url = "/media/images/og.jpg"
    width = 1200
    height = 630


class _MockImage:
    title = "Override Image"
    width = 1200
    height = 630

    def get_rendition(self, spec: str) -> _MockRendition:
        return _MockRendition()


class _MockPageImage:
    title = "Page OG Image"
    width = 1200
    height = 630

    def get_rendition(self, spec: str) -> _MockRendition:
        return _MockRendition()


class _MockPageWithOgImage(_MockPage):
    og_image = _MockPageImage()
    og_image_alt = "Page OG alt"

    def get_og_image_alt(self) -> str:
        return "Page OG alt"


class TestBuildSeoContextOverrides:
    """Tests for the overrides parameter of build_seo_context."""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_title_override_sets_title_og_and_twitter(self, _mock_site):
        """Verify title override propagates to title, og_title, and twitter_title.

        Purpose: Confirm that when a RoutablePageMixin sub-route passes a custom
        title via overrides, all title-related context keys reflect the override
        rather than the page's own title.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"title": "Custom Route Title"} with a page
            that has its own title "Page Title"
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={"title": "Custom Route Title"}
        )

        assert result["og_title"] == "Custom Route Title"
        assert result["twitter_title"] == "Custom Route Title"
        assert "Custom Route Title" in result["title"]

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_title_override_takes_priority_over_seo_title(self, _mock_site):
        """Verify title override beats page.seo_title.

        Purpose: Confirm that even when a page has seo_title set, the
        override value takes priority. This validates that sub-route titles
        can differ from the page-level SEO title.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: page.seo_title="SEO Title", overrides={"title": "Override"}
        """
        page = _MockPageWithSeoTitle()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={"title": "Override Title"}
        )

        assert result["og_title"] == "Override Title"
        assert result["twitter_title"] == "Override Title"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_description_override_sets_all_description_fields(self, _mock_site):
        """Verify description override propagates to description, og, and twitter.

        Purpose: Confirm that a sub-route description override replaces the
        page's search_description across all SEO contexts (meta, OG, Twitter).
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"description": "Custom desc"} with a page
            that has search_description="Page description"
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={"description": "Custom desc"}
        )

        assert result["description"] == "Custom desc"
        assert result["og_description"] == "Custom desc"
        assert result["twitter_description"] == "Custom desc"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_canonical_url_override_sets_canonical_and_og_url(self, _mock_site):
        """Verify canonical_url override propagates to canonical_url and og_url.

        Purpose: Confirm that a sub-route can specify its own canonical URL,
        which is critical for RoutablePageMixin routes that have different URLs
        from the parent page.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"canonical_url": "https://example.com/sub/"}
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request,
            page,
            None,
            overrides={"canonical_url": "https://example.com/sub/"},
        )

        assert result["canonical_url"] == "https://example.com/sub/"
        assert result["og_url"] == "https://example.com/sub/"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_all_overrides_combined(self, _mock_site):
        """Verify all override keys work together.

        Purpose: Confirm that title, description, and canonical_url overrides
        can be applied simultaneously without interfering with each other.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: decision table (all conditions true)
        Test data: all three text overrides provided simultaneously
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request,
            page,
            None,
            overrides={
                "title": "Route Title",
                "description": "Route Desc",
                "canonical_url": "https://example.com/route/",
            },
        )

        assert result["og_title"] == "Route Title"
        assert result["description"] == "Route Desc"
        assert result["og_description"] == "Route Desc"
        assert result["canonical_url"] == "https://example.com/route/"
        assert result["og_url"] == "https://example.com/route/"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_empty_string_override_uses_empty_string(self, _mock_site):
        """Verify empty string override is kept, not treated as missing.

        Purpose: Confirm that an intentional empty string override (e.g., to
        suppress a page title) is preserved. The implementation filters None
        but keeps empty strings. Ref DT2.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: boundary value analysis (empty string as boundary of
            valid string domain)
        Test data: overrides={"title": ""} with page.title="Page Title"
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None, overrides={"title": ""})

        assert result["og_title"] == ""
        assert result["twitter_title"] == ""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_empty_string_description_override_uses_empty_string(self, _mock_site):
        """Verify empty string description override is kept.

        Purpose: Confirm that an intentional empty description override is
        preserved rather than falling back to page.search_description. Ref DT5.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: boundary value analysis
        Test data: overrides={"description": ""} with
            page.search_description="Page description"
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None, overrides={"description": ""})

        assert result["description"] == ""
        assert result["og_description"] == ""
        assert result["twitter_description"] == ""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_none_value_in_overrides_falls_back_to_page(self, _mock_site):
        """Verify None override value is filtered and page value is used.

        Purpose: Confirm that passing None for an override key does not
        suppress the page value. The implementation filters None via
        dict comprehension. Ref DT3.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning (None as invalid override)
        Test data: overrides={"title": None} with page.title="Page Title"
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None, overrides={"title": None})

        assert result["og_title"] == "Page Title"
        assert result["twitter_title"] == "Page Title"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_none_description_override_falls_back_to_page(self, _mock_site):
        """Verify None description override falls back to page.search_description.

        Purpose: Confirm None filtering for the description key. Ref DT6.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"description": None}
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None, overrides={"description": None})

        assert result["description"] == "Page description"
        assert result["og_description"] == "Page description"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_none_canonical_url_override_falls_back_to_page(self, _mock_site):
        """Verify None canonical_url override falls back to page URL.

        Purpose: Confirm None filtering for the canonical_url key. Ref DT8.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"canonical_url": None}
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={"canonical_url": None}
        )

        assert result["canonical_url"] == "https://example.com/page/"
        assert result["og_url"] == "https://example.com/page/"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_empty_overrides_dict_behaves_as_no_overrides(self, _mock_site):
        """Verify empty overrides dict has same result as no overrides.

        Purpose: Confirm that an empty overrides dict does not change any
        values compared to passing no overrides at all.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: boundary value analysis (empty collection)
        Test data: overrides={} vs overrides=None
        """
        page = _MockPage()
        request = mock.Mock()

        result_empty = build_seo_context(request, page, None, overrides={})
        result_none = build_seo_context(request, page, None, overrides=None)

        assert result_empty["og_title"] == result_none["og_title"]
        assert result_empty["description"] == result_none["description"]
        assert result_empty["canonical_url"] == result_none["canonical_url"]
        assert result_empty["og_url"] == result_none["og_url"]

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_partial_overrides_only_affect_specified_keys(self, _mock_site):
        """Verify only specified override keys are changed; others use page values.

        Purpose: Confirm that providing a title override does not affect
        description or canonical_url, which should still come from the page.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: decision table (partial conditions)
        Test data: only title override provided
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={"title": "Only Title Override"}
        )

        assert result["og_title"] == "Only Title Override"
        assert result["description"] == "Page description"
        assert result["canonical_url"] == "https://example.com/page/"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_all_none_overrides_behaves_as_no_overrides(self, _mock_site):
        """Verify all-None overrides dict produces same result as no overrides.

        Purpose: Confirm that when every override value is None, all values
        are filtered and the page defaults are used.
        Category: edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: boundary value analysis
        Test data: overrides with all keys set to None
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request,
            page,
            None,
            overrides={
                "title": None,
                "description": None,
                "canonical_url": None,
                "og_image": None,
            },
        )

        assert result["og_title"] == "Page Title"
        assert result["description"] == "Page description"
        assert result["canonical_url"] == "https://example.com/page/"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_og_image_override_passed_to_get_og_image_data(self, _mock_site):
        """Verify og_image override is forwarded to _get_og_image_data.

        Purpose: Confirm that when og_image is included in overrides, the
        override image appears in all image-related context keys.
        Category: normal case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: equivalence partitioning
        Test data: overrides={"og_image": MockImage()} with page that has
            no og_image
        """
        page = _MockPage()
        request = mock.Mock()
        override_image = _MockImage()

        result = build_seo_context(
            request, page, None, overrides={"og_image": override_image}
        )

        assert result["og_image"] is not None
        assert result["og_image"] != ""
        assert result["twitter_image"] == result["og_image"]

    @pytest.mark.parametrize(
        "override_key,override_value,expected_key,expected_value",
        [
            pytest.param(
                "title",
                "Custom Title",
                "og_title",
                "Custom Title",
                id="DT1-title-override",
            ),
            pytest.param(
                "title",
                "",
                "og_title",
                "",
                id="DT2-title-empty-string",
            ),
            pytest.param(
                "description",
                "Custom desc",
                "og_description",
                "Custom desc",
                id="DT4-description-override",
            ),
            pytest.param(
                "description",
                "",
                "og_description",
                "",
                id="DT5-description-empty-string",
            ),
        ],
    )
    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_override_value_propagation(
        self,
        _mock_site,
        override_key,
        override_value,
        expected_key,
        expected_value,
    ):
        """Verify individual override values propagate correctly.

        Purpose: Parametric validation of each override key/value combination
        from the DT-OVERRIDE-FILTERING decision table.
        Category: normal case / edge case
        Target: build_seo_context(request, page, settings, overrides)
        Technique: decision table (DT-OVERRIDE-FILTERING)
        Test data: see parametrize entries DT1, DT2, DT4, DT5
        """
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(
            request, page, None, overrides={override_key: override_value}
        )

        assert result[expected_key] == expected_value


class TestOgImageDataOverride:
    """Tests for og_image_override parameter in _get_og_image_data."""

    def test_override_image_used_instead_of_page_image(self):
        """Verify og_image_override takes priority over page.og_image.

        Purpose: Confirm that when a sub-route provides an og_image override,
        it is used instead of the page's own og_image, supporting per-route
        social sharing images.
        Category: normal case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: equivalence partitioning
        Test data: page with og_image set, og_image_override with different image
        """
        request = mock.Mock()
        page = _MockPageWithOgImage()
        override_image = _MockImage()

        result = _get_og_image_data(
            request, page, None, og_image_override=override_image
        )

        assert result["alt"] == "Override Image"
        assert result["url"] != ""
        assert result["width"] == 1200
        assert result["height"] == 630

    def test_override_image_none_falls_back_to_page(self):
        """Verify og_image_override=None falls back to page.og_image.

        Purpose: Confirm that when no override is provided (None), the normal
        fallback chain (page.og_image -> settings.default_og_image) is used.
        Category: edge case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: equivalence partitioning
        Test data: og_image_override=None with page that has og_image
        """
        request = mock.Mock()
        page = _MockPageWithOgImage()

        result = _get_og_image_data(request, page, None, og_image_override=None)

        assert result["alt"] == "Page OG alt"

    def test_override_image_skips_settings_default(self):
        """Verify og_image_override skips settings.default_og_image entirely.

        Purpose: Confirm that when an override image is provided, the settings
        default_og_image is never consulted, even if the page has no og_image.
        Category: normal case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: equivalence partitioning
        Test data: page without og_image, settings with default_og_image,
            og_image_override provided
        """
        request = mock.Mock()
        page = _MockPage()
        settings = mock.Mock()
        settings.default_og_image = _MockPageImage()
        settings.default_og_image_alt = "Default alt"
        override_image = _MockImage()

        result = _get_og_image_data(
            request, page, settings, og_image_override=override_image
        )

        assert result["alt"] == "Override Image"

    def test_override_image_without_title_attribute(self):
        """Verify og_image_override without title uses empty alt.

        Purpose: Confirm that when the override image object lacks a title
        attribute, alt text falls back to empty string gracefully.
        Category: edge case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: error guessing (missing attribute)
        Test data: override image mock without title attribute
        """
        request = mock.Mock()
        page = _MockPage()
        override_image = mock.Mock(spec=[])
        override_image.get_rendition = mock.Mock(return_value=_MockRendition())

        result = _get_og_image_data(
            request, page, None, og_image_override=override_image
        )

        assert result["alt"] == ""

    def test_override_image_rendition_failure_falls_back(self):
        """Verify graceful fallback when override image rendition fails.

        Purpose: Confirm that if get_rendition raises an exception for the
        override image, the function falls back to the original image URL.
        Category: error case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: error guessing (rendition failure)
        Test data: override image whose get_rendition raises Exception
        """
        request = mock.Mock()
        page = _MockPage()
        override_image = mock.Mock(
            spec=["title", "get_rendition", "width", "height", "url"]
        )
        override_image.title = "Broken Image"
        override_image.get_rendition.side_effect = Exception("rendition error")
        override_image.width = 800
        override_image.height = 400
        override_image.url = "/media/broken.jpg"

        result = _get_og_image_data(
            request, page, None, og_image_override=override_image
        )

        assert result["alt"] == "Broken Image"
        assert result["width"] == 800
        assert result["height"] == 400

    def test_no_override_no_page_image_no_settings_returns_empty(self):
        """Verify empty result when no image is available anywhere.

        Purpose: Confirm that when no override, no page og_image, and no
        settings default are available, all image fields are empty.
        Category: edge case
        Target: _get_og_image_data(request, page, settings, og_image_override)
        Technique: boundary value analysis (all sources empty)
        Test data: no override, page without og_image, None settings
        """
        request = mock.Mock()
        page = _MockPage()

        result = _get_og_image_data(request, page, None, og_image_override=None)

        assert result["url"] == ""
        assert result["alt"] == ""
        assert result["width"] == ""
        assert result["height"] == ""
