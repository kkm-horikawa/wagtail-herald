"""Integration tests for the root favicon endpoints.

Google のファビコン取得は ``/favicon.ico`` などのルートを必ず探し、取得失敗が
一度でもあると検索結果のファビコンが地球儀に戻る。herald が設定済みのファビコン
画像を恒久ルートパスで・長期キャッシュ付きで返すことを保証する。

| ID  | パス                  | 設定         | 期待結果                              |
|-----|-----------------------|--------------|---------------------------------------|
| FV1 | /favicon.ico          | favicon_png  | 200 / image/png / 1年 immutable cache |
| FV2 | /favicon.ico          | なし         | 404                                   |
| FV3 | /favicon.svg          | favicon_svg  | 200 / 1年 immutable cache             |
| FV4 | /apple-touch-icon.png | apple_touch  | 200 / 1年 immutable cache             |
"""

from unittest.mock import patch

import pytest
from django.http import Http404
from django.test import Client, RequestFactory
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site

from wagtail_herald.models import SEOSettings
from wagtail_herald.views import favicon

ONE_YEAR_IMMUTABLE = "public, max-age=31536000, immutable"


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def root_page(db):
    try:
        return Page.objects.get(depth=1)
    except Page.DoesNotExist:
        return Page.add_root(title="Root", slug="root")


@pytest.fixture
def default_site(db, root_page):
    site, _created = Site.objects.get_or_create(
        hostname="localhost",
        defaults={
            "root_page": root_page,
            "is_default_site": True,
            "site_name": "Test Site",
        },
    )
    return site


def _make_image(filename: str):
    return get_image_model().objects.create(
        title=filename,
        file=get_test_image_file(filename=filename),
    )


class TestFaviconEndpoint:
    @pytest.mark.django_db
    def test_serves_configured_png_with_long_cache(self, client, default_site):
        """FV1: GET /favicon.ico returns the configured PNG with a 1-year cache."""
        SEOSettings.objects.create(
            site=default_site, favicon_png=_make_image("favicon.png")
        )

        response = client.get("/favicon.ico")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert response["Cache-Control"] == ONE_YEAR_IMMUTABLE

    @pytest.mark.django_db
    def test_returns_404_when_not_configured(self, client, default_site):
        """FV2: GET /favicon.ico returns 404 when no favicon is configured."""
        SEOSettings.objects.create(site=default_site)

        response = client.get("/favicon.ico")

        assert response.status_code == 404

    @pytest.mark.django_db
    def test_falls_back_to_default_content_type_for_unknown_extension(
        self, client, default_site
    ):
        """FV5: 拡張子から MIME を判定できない場合はビューの既定 Content-Type を使う。"""
        SEOSettings.objects.create(
            site=default_site, favicon_png=_make_image("favicon")
        )

        response = client.get("/favicon.ico")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"

    @patch("wagtail_herald.views.Site.find_for_request", return_value=None)
    def test_raises_404_when_no_site_resolved(self, _mock_find):
        """FV6: リクエストに対応する Site が解決できない場合は 404。"""
        request = RequestFactory().get("/favicon.ico")

        with pytest.raises(Http404):
            favicon(request)


class TestFaviconSvgEndpoint:
    @pytest.mark.django_db
    def test_serves_configured_svg_with_long_cache(self, client, default_site):
        """FV3: GET /favicon.svg serves the configured SVG favicon."""
        SEOSettings.objects.create(
            site=default_site, favicon_svg=_make_image("favicon.png")
        )

        response = client.get("/favicon.svg")

        assert response.status_code == 200
        assert response["Cache-Control"] == ONE_YEAR_IMMUTABLE

    @pytest.mark.django_db
    def test_returns_404_when_not_configured(self, client, default_site):
        SEOSettings.objects.create(site=default_site)

        assert client.get("/favicon.svg").status_code == 404


class TestAppleTouchIconEndpoint:
    @pytest.mark.django_db
    def test_serves_configured_icon_with_long_cache(self, client, default_site):
        """FV4: GET /apple-touch-icon.png serves the configured Apple touch icon."""
        SEOSettings.objects.create(
            site=default_site, apple_touch_icon=_make_image("apple.png")
        )

        response = client.get("/apple-touch-icon.png")

        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert response["Cache-Control"] == ONE_YEAR_IMMUTABLE

    @pytest.mark.django_db
    def test_returns_404_when_not_configured(self, client, default_site):
        SEOSettings.objects.create(site=default_site)

        assert client.get("/apple-touch-icon.png").status_code == 404
