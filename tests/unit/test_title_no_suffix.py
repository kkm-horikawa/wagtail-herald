"""titleタグからサイト名サフィックスを除去するテスト (#121)

build_seo_contextが返すtitleがpage_titleのみ（サイト名サフィックスなし）であることを
検証する。og:site_nameは引き続きsite_nameを返し、title_separatorフィールドは
SEOSettingsから削除されている。

## デシジョンテーブル: DT-TITLE-NO-SUFFIX

| ID  | page_title   | site_name    | 期待 title    | 期待 og_site_name |
|-----|-------------|-------------|--------------|------------------|
| DT1 | "Test Page" | "My Site"   | "Test Page"  | "My Site"        |
| DT2 | "Test Page" | ""          | "Test Page"  | ""               |
| DT3 | ""          | "My Site"   | ""           | "My Site"        |
| DT4 | seo_title有 | "My Site"   | "SEO Title"  | "My Site"        |
"""

from __future__ import annotations

from unittest import mock

import pytest

from wagtail_herald.templatetags.wagtail_herald import build_seo_context


class _MockPage:
    title = "Test Page"
    seo_title = ""
    search_description = ""
    full_url = "https://example.com/test/"


class _MockPageWithSeoTitle(_MockPage):
    seo_title = "SEO Title"


def _make_mock_site(site_name: str) -> mock.Mock:
    site = mock.Mock()
    site.site_name = site_name
    return site


class TestBuildSeoContextTitleNoSuffix:
    """build_seo_context()のtitleがpage_titleのみであることの検証。"""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_title_equals_page_title_without_site_name_suffix(self, mock_find):
        """site_nameが設定されていてもtitleにサフィックスが付かないことを確認する。

        【目的】build_seo_context()にsite_name付きのサイトとページを与え、
               titleがpage_titleのみであることをもって、サイト名サフィックス
               除去要件を保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings)
        【技法】デシジョンテーブル（DT1参照）
        【テストデータ】
        - page.title="Test Page"
        - site.site_name="My Site"
        """
        mock_find.return_value = _make_mock_site("My Site")
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None)

        assert result["title"] == "Test Page"
        assert "My Site" not in result["title"]

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_title_without_site_name_configured(self, mock_find):
        """site_nameが空の場合もtitleがpage_titleのみであることを確認する。

        【目的】build_seo_context()にsite_name空のサイトとページを与え、
               titleがpage_titleのみであることをもって、空site_nameケースの
               安全性を保証する
        【種別】エッジケース
        【対象】build_seo_context(request, page, settings)
        【技法】デシジョンテーブル（DT2参照）
        【テストデータ】
        - page.title="Test Page"
        - site.site_name=""
        """
        mock_find.return_value = _make_mock_site("")
        page = _MockPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None)

        assert result["title"] == "Test Page"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_empty_page_title_with_site_name(self, mock_find):
        """page_titleが空でsite_nameがあってもtitleが空のままであることを確認する。

        【目的】build_seo_context()に空titleのページとsite_name付きサイトを与え、
               titleが空のままであることをもって、サイト名だけが出力される
               リグレッションを防止する
        【種別】エッジケース
        【対象】build_seo_context(request, page, settings)
        【技法】デシジョンテーブル（DT3参照）
        【テストデータ】
        - page.title=""
        - site.site_name="My Site"
        """
        mock_find.return_value = _make_mock_site("My Site")

        class EmptyTitlePage(_MockPage):
            title = ""

        page = EmptyTitlePage()
        request = mock.Mock()

        result = build_seo_context(request, page, None)

        assert result["title"] == ""
        assert "My Site" not in result["title"]

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_seo_title_used_without_site_name_suffix(self, mock_find):
        """seo_titleが設定されている場合もサフィックスなしで使用されることを確認する。

        【目的】build_seo_context()にseo_title付きページとsite_name付きサイトを与え、
               titleがseo_titleのみであることをもって、seo_title使用時の
               サフィックス除去要件を保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings)
        【技法】デシジョンテーブル（DT4参照）
        【テストデータ】
        - page.seo_title="SEO Title"
        - site.site_name="My Site"
        """
        mock_find.return_value = _make_mock_site("My Site")
        page = _MockPageWithSeoTitle()
        request = mock.Mock()

        result = build_seo_context(request, page, None)

        assert result["title"] == "SEO Title"
        assert "My Site" not in result["title"]


class TestOgSiteNameStillOutput:
    """og_site_nameがsite_nameを引き続き返すことの検証。"""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_og_site_name_returns_site_name(self, mock_find):
        """og_site_nameがsite_nameを返すことを確認する。

        【目的】build_seo_context()のog_site_nameがsite.site_nameを返すことをもって、
               OGPメタタグでサイト名が引き続き出力される要件を保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings)
        【技法】同値分割
        【テストデータ】
        - site.site_name="My Site"
        """
        mock_find.return_value = _make_mock_site("My Site")
        request = mock.Mock()

        result = build_seo_context(request, _MockPage(), None)

        assert result["og_site_name"] == "My Site"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_og_site_name_empty_when_no_site_name(self, mock_find):
        """site_nameが空の場合og_site_nameも空であることを確認する。

        【目的】build_seo_context()にsite_name空のサイトを与え、
               og_site_nameが空文字であることをもって、空サイト名のケースを保証する
        【種別】エッジケース
        【対象】build_seo_context(request, page, settings)
        【技法】境界値分析
        【テストデータ】
        - site.site_name=""
        """
        mock_find.return_value = _make_mock_site("")
        request = mock.Mock()

        result = build_seo_context(request, _MockPage(), None)

        assert result["og_site_name"] == ""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_og_site_name_empty_when_no_site(self, _mock_find):
        """サイトが見つからない場合og_site_nameが空であることを確認する。

        【目的】build_seo_context()にサイトなしのrequestを与え、
               og_site_nameが空文字であることをもって、サイト未設定ケースの安全性を保証する
        【種別】エッジケース
        【対象】build_seo_context(request, page, settings)
        【技法】同値分割
        【テストデータ】
        - Site.find_for_request()がNoneを返す
        """
        request = mock.Mock()

        result = build_seo_context(request, _MockPage(), None)

        assert result["og_site_name"] == ""


class TestTitleSeparatorRemoved:
    """SEOSettingsからtitle_separatorフィールドが削除されていることの検証。"""

    def test_seo_settings_has_no_title_separator_field(self):
        """SEOSettingsにtitle_separatorフィールドが存在しないことを確認する。

        【目的】SEOSettingsクラスにtitle_separator属性が存在しないことをもって、
               フィールド削除要件を保証する
        【種別】リグレッション
        【対象】SEOSettings
        【技法】エラー推測
        【テストデータ】SEOSettingsクラスのフィールド一覧
        """
        from wagtail_herald.models import SEOSettings

        field_names = [f.name for f in SEOSettings._meta.get_fields()]

        assert "title_separator" not in field_names


class TestTitleAndOgSiteNameIndependence:
    """titleとog_site_nameが独立していることの検証。"""

    @pytest.mark.parametrize(
        "page_title,seo_title,site_name,expected_title,expected_og_site_name",
        [
            pytest.param("Test Page", "", "My Site", "Test Page", "My Site", id="DT1"),
            pytest.param("Test Page", "", "", "Test Page", "", id="DT2"),
            pytest.param("", "", "My Site", "", "My Site", id="DT3"),
            pytest.param(
                "Regular", "SEO Title", "My Site", "SEO Title", "My Site", id="DT4"
            ),
        ],
    )
    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
    )
    def test_title_and_og_site_name_decision_table(
        self,
        mock_find,
        page_title,
        seo_title,
        site_name,
        expected_title,
        expected_og_site_name,
    ):
        """DT-TITLE-NO-SUFFIX参照。

        【目的】page_title/seo_title/site_nameの組み合わせに応じた
               title・og_site_nameの値を検証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings)
        【技法】デシジョンテーブル
        【テストデータ】DT-TITLE-NO-SUFFIXの全パターン
        """
        mock_find.return_value = _make_mock_site(site_name)

        class DynamicPage(_MockPage):
            pass

        DynamicPage.title = page_title
        DynamicPage.seo_title = seo_title

        page = DynamicPage()
        request = mock.Mock()

        result = build_seo_context(request, page, None)

        assert result["title"] == expected_title
        assert result["og_site_name"] == expected_og_site_name
