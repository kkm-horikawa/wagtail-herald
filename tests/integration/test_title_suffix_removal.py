"""Integration tests for title suffix removal (#121).

Tests the full template rendering pipeline to verify that the <title> tag
contains only the page title without site name suffix, and that og:site_name
continues to be output independently.
"""

import pytest
from django.template import Context, Template
from wagtail.models import Page, Site

from wagtail_herald.models import SEOSettings

TEMPLATE_STRING = "{% load wagtail_herald %}{% seo_head %}"


@pytest.fixture
def _site(db):
    """Get or create the default site for template rendering tests."""
    try:
        root = Page.objects.get(depth=1)
    except Page.DoesNotExist:
        root = Page.add_root(title="Root", slug="root")

    site, _ = Site.objects.get_or_create(
        hostname="localhost",
        defaults={
            "root_page": root,
            "is_default_site": True,
            "site_name": "My Awesome Site",
        },
    )
    if site.site_name != "My Awesome Site":
        site.site_name = "My Awesome Site"
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
        title = "About Us"
        seo_title = ""
        search_description = "Learn about our company"
        full_url = "https://example.com/about/"

    return _MockPage()


@pytest.fixture
def mock_page_with_seo_title():
    """A page-like object with seo_title set (Wagtail promote tab override)."""

    class _MockPage:
        title = "About Us"
        seo_title = "About Our Company"
        search_description = "Learn about our company"
        full_url = "https://example.com/about/"

    return _MockPage()


class TestTitleWithoutSiteSuffix:
    """<title> contains only page_title without site name suffix."""

    @pytest.mark.django_db
    def test_title_is_page_title_only(self, request_with_site, mock_page):
        """titleタグがページタイトルのみでサイト名サフィックスを含まない。

        【目的】seo_headテンプレートタグをレンダリングし、<title>タグに
               ページタイトルのみが含まれサイト名が付加されていないことをもって、
               Issue #121のtitleサフィックス除去要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> build_seo_context
                    -> seo_head.html <title>
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - title="About Us"のページ
        【検証シナリオ】
        1. seo_headテンプレートタグをレンダリング
        2. <title>が"About Us"のみであることを確認
        3. <title>内にサイト名が含まれないことを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context({"request": request_with_site, "page": mock_page})

        html = template.render(context)

        title_content = html.split("<title>")[1].split("</title>")[0]
        assert title_content == "About Us"
        assert "My Awesome Site" not in title_content

    @pytest.mark.django_db
    def test_seo_title_override_without_site_suffix(
        self, request_with_site, mock_page_with_seo_title
    ):
        """seo_titleが設定されたページでもtitleにサイト名サフィックスが付かない。

        【目的】Wagtailのpromoteタブでseo_titleを設定したページをレンダリングし、
               <title>がseo_titleのみでサイト名が付加されないことをもって、
               seo_titleオーバーライド時もサフィックス除去が適用される要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> _get_page_title(seo_title)
                    -> build_seo_context -> seo_head.html <title>
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - seo_title="About Our Company"のページ
        【検証シナリオ】
        1. seo_titleが設定されたページでseo_headをレンダリング
        2. <title>が"About Our Company"のみであることを確認
        3. <title>内にサイト名が含まれないことを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {"request": request_with_site, "page": mock_page_with_seo_title}
        )

        html = template.render(context)

        title_content = html.split("<title>")[1].split("</title>")[0]
        assert title_content == "About Our Company"
        assert "My Awesome Site" not in title_content

    @pytest.mark.django_db
    def test_context_override_title_without_site_suffix(
        self, request_with_site, mock_page
    ):
        """コンテキストのseo_titleオーバーライドでもtitleにサイト名が付かない。

        【目的】RoutablePageMixinパターンでseo_titleコンテキストキーを設定し、
               <title>がオーバーライド値のみでサイト名が付加されないことをもって、
               サブルートでもサフィックス除去が適用される要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】Context(seo_title=...) -> seo_head tag
                    -> _collect_overrides_from_context
                    -> build_seo_context(overrides) -> seo_head.html <title>
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - コンテキストのseo_title="Events Archive"
        【検証シナリオ】
        1. seo_titleコンテキストキーを設定してseo_headをレンダリング
        2. <title>が"Events Archive"のみであることを確認
        3. <title>内にサイト名が含まれないことを確認
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

        title_content = html.split("<title>")[1].split("</title>")[0]
        assert title_content == "Events Archive"
        assert "My Awesome Site" not in title_content


class TestOgSiteNameStillOutput:
    """og:site_name meta tag continues to be output after title suffix removal."""

    @pytest.mark.django_db
    def test_og_site_name_rendered_with_site_name(self, request_with_site, mock_page):
        """og:site_nameメタタグにサイト名が出力される。

        【目的】titleからサイト名サフィックスを除去した後も、
               og:site_nameメタタグにはサイト名が正常に出力されることをもって、
               SNSシェア時のサイト名表示が維持される要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> build_seo_context(og_site_name)
                    -> seo_head.html og:site_name
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - 通常のテストページ
        【検証シナリオ】
        1. seo_headテンプレートタグをレンダリング
        2. og:site_nameメタタグにサイト名が含まれることを確認
        3. <title>にはサイト名が含まれないことを確認（分離を検証）
        """
        template = Template(TEMPLATE_STRING)
        context = Context({"request": request_with_site, "page": mock_page})

        html = template.render(context)

        assert 'property="og:site_name" content="My Awesome Site"' in html
        title_content = html.split("<title>")[1].split("</title>")[0]
        assert "My Awesome Site" not in title_content

    @pytest.mark.django_db
    def test_og_site_name_with_seo_title_override(
        self, request_with_site, mock_page_with_seo_title
    ):
        """seo_title使用時もog:site_nameが正常に出力される。

        【目的】seo_titleオーバーライドが設定されたページでも
               og:site_nameメタタグが正しく出力されることをもって、
               titleとog:site_nameの独立性を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> build_seo_context
                    -> seo_head.html (title, og:site_name独立)
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - seo_title="About Our Company"のページ
        【検証シナリオ】
        1. seo_titleが設定されたページでseo_headをレンダリング
        2. og:site_nameにサイト名が出力されることを確認
        3. <title>はseo_titleのみであることを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {"request": request_with_site, "page": mock_page_with_seo_title}
        )

        html = template.render(context)

        assert 'property="og:site_name" content="My Awesome Site"' in html
        assert "<title>About Our Company</title>" in html

    @pytest.mark.django_db
    def test_og_site_name_with_context_override(self, request_with_site, mock_page):
        """コンテキストオーバーライド時もog:site_nameが正常に出力される。

        【目的】seo_titleコンテキストキーでタイトルをオーバーライドした場合でも
               og:site_nameが正しく出力されることをもって、
               RoutablePageMixinパターンでのSNSシェア表示を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】Context(seo_title=...) -> seo_head tag
                    -> build_seo_context -> seo_head.html (title, og:site_name)
        【テストデータ】
        - site_name="My Awesome Site"のWagtailサイト
        - コンテキストのseo_title="Events Archive"
        【検証シナリオ】
        1. seo_titleコンテキストキーを設定してseo_headをレンダリング
        2. og:site_nameにサイト名が出力されることを確認
        3. <title>はオーバーライド値のみであることを確認
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

        assert 'property="og:site_name" content="My Awesome Site"' in html
        assert "<title>Events Archive</title>" in html


class TestTitleSeparatorFieldRemoved:
    """title_separator field no longer exists on SEOSettings model."""

    @pytest.mark.django_db
    def test_seo_settings_has_no_title_separator_field(self, _site):
        """SEOSettingsモデルにtitle_separatorフィールドが存在しない。

        【目的】SEOSettingsを作成し、title_separatorフィールドが
               モデルから削除されていることをもって、
               Issue #121のtitle_separator整理要件を保証する
        【種別】正常系
        【技法】モデルライフサイクル
        【連携対象】SEOSettings model -> DB schema (0007 migration)
        【テストデータ】
        - デフォルト設定のSEOSettings
        【検証シナリオ】
        1. SEOSettingsインスタンスを作成
        2. title_separator属性が存在しないことを確認
        """
        settings = SEOSettings.objects.create(site=_site)

        assert not hasattr(settings, "title_separator")

    @pytest.mark.django_db
    def test_seo_settings_creation_without_title_separator(self, _site):
        """title_separatorなしでSEOSettingsが正常に作成・保存できる。

        【目的】title_separatorフィールド削除後もSEOSettingsの
               CRUD操作が正常に動作することをもって、
               マイグレーション後のデータ整合性を保証する
        【種別】正常系
        【技法】モデルライフサイクル
        【連携対象】SEOSettings.objects.create -> DB -> SEOSettings.objects.get
        【テストデータ】
        - gtm_container_idを持つSEOSettings
        【検証シナリオ】
        1. title_separatorなしでSEOSettingsを作成
        2. DBから再取得して値が正しいことを確認
        """
        settings = SEOSettings.objects.create(
            site=_site, gtm_container_id="GTM-TEST121"
        )

        reloaded = SEOSettings.objects.get(pk=settings.pk)
        assert reloaded.gtm_container_id == "GTM-TEST121"


class TestTitleAndOgTitleConsistency:
    """<title> and og:title contain the same value (page_title only)."""

    @pytest.mark.django_db
    def test_title_and_og_title_match(self, request_with_site, mock_page):
        """titleとog:titleが同じ値（ページタイトルのみ）を持つ。

        【目的】<title>とog:titleが一致することをもって、
               検索結果とSNSプレビューで同じタイトルが表示される
               一貫性を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> build_seo_context
                    -> seo_head.html (title, og:title)
        【テストデータ】
        - title="About Us"のページ
        【検証シナリオ】
        1. seo_headテンプレートタグをレンダリング
        2. <title>とog:titleが同じ値であることを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context({"request": request_with_site, "page": mock_page})

        html = template.render(context)

        assert "<title>About Us</title>" in html
        assert 'property="og:title" content="About Us"' in html

    @pytest.mark.django_db
    def test_title_and_og_title_match_with_seo_title(
        self, request_with_site, mock_page_with_seo_title
    ):
        """seo_title設定時もtitleとog:titleが一致する。

        【目的】seo_titleが設定されたページで<title>とog:titleが
               同じ値を持つことをもって、タイトルの一貫性を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> _get_page_title(seo_title)
                    -> build_seo_context -> seo_head.html (title, og:title)
        【テストデータ】
        - seo_title="About Our Company"のページ
        【検証シナリオ】
        1. seo_titleが設定されたページでseo_headをレンダリング
        2. <title>とog:titleが同じseo_titleの値であることを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context(
            {"request": request_with_site, "page": mock_page_with_seo_title}
        )

        html = template.render(context)

        assert "<title>About Our Company</title>" in html
        assert 'property="og:title" content="About Our Company"' in html


class TestNoPageContext:
    """Rendering with no page in context still works after title_separator removal."""

    @pytest.mark.django_db
    def test_no_page_renders_empty_title_without_error(self, request_with_site):
        """ページがない場合でもエラーなくレンダリングされる。

        【目的】pageコンテキストキーがない場合でもseo_headが
               エラーなくレンダリングされることをもって、
               title_separator削除後のエッジケースでの安全性を保証する
        【種別】境界値
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request -> seo_head tag -> build_seo_context(page=None)
                    -> seo_head.html
        【テストデータ】
        - requestのみでpageなし
        【検証シナリオ】
        1. pageなしでseo_headテンプレートタグをレンダリング
        2. エラーなく出力されることを確認
        3. <title>タグが存在し空であることを確認
        """
        template = Template(TEMPLATE_STRING)
        context = Context({"request": request_with_site})

        html = template.render(context)

        assert "<title></title>" in html
