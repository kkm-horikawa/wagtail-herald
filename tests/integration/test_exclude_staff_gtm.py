"""Integration tests for staff user GTM exclusion (#117).

Tests the full template rendering pipeline: Django Template engine loads the
wagtail_herald template tags, the seo_head / seo_body tags check the current
user's is_staff flag via the request object, and exclude GTM snippets from
the rendered HTML for staff users while keeping all other SEO tags intact.
"""

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template
from wagtail.models import Page, Site

from wagtail_herald.models import SEOSettings

GTM_CONTAINER_ID = "GTM-TEST117"
GTM_JS_MARKER = "googletagmanager.com/gtm.js"
GTM_NS_MARKER = "googletagmanager.com/ns.html"


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
            "site_name": "Test Site",
        },
    )
    if site.site_name != "Test Site":
        site.site_name = "Test Site"
        site.save()
    return site


@pytest.fixture
def seo_settings(_site):
    """Create SEOSettings with GTM container ID configured."""
    return SEOSettings.objects.create(
        site=_site,
        gtm_container_id=GTM_CONTAINER_ID,
    )


@pytest.fixture
def staff_user(db):
    """Create a staff user."""
    return User.objects.create_user(
        username="staff", password="testpass", is_staff=True
    )


@pytest.fixture
def normal_user(db):
    """Create a non-staff user."""
    return User.objects.create_user(
        username="normal", password="testpass", is_staff=False
    )


@pytest.fixture
def mock_page():
    """A lightweight page-like object with default SEO attributes."""

    class _MockPage:
        title = "Test Page"
        seo_title = ""
        search_description = "Test page description"
        full_url = "https://example.com/test/"

    return _MockPage()


def _build_request(rf, _site, user):
    """Build a request bound to the site with the given user."""
    request = rf.get("/")
    request.site = _site
    request.user = user
    return request


class TestSeoHeadGtmExclusionForStaff:
    """seo_head template tag excludes GTM script for staff users."""

    @pytest.mark.django_db
    def test_staff_user_page_does_not_contain_gtm_script(
        self, rf, _site, seo_settings, staff_user, mock_page
    ):
        """staffユーザーのページアクセスでGTMスクリプトがHTMLに含まれない。

        【目的】staffユーザーのリクエストでseo_headをレンダリングし、
               GTM JavaScriptスニペットが出力されないことをもって、
               管理者のページビューがアクセス解析を汚染しない要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=True) -> seo_head tag -> _should_exclude_gtm
                    -> build_seo_context(gtm_container_id="") -> seo_head.html
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - テスト用ページオブジェクト
        【検証シナリオ】
        1. staffユーザーのリクエストでseo_headテンプレートタグをレンダリング
        2. 出力HTMLにGTM JavaScriptが含まれないことを確認
        3. GTMコンテナIDが含まれないことを確認
        """
        request = _build_request(rf, _site, staff_user)
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        assert GTM_JS_MARKER not in html
        assert GTM_CONTAINER_ID not in html

    @pytest.mark.django_db
    def test_non_staff_user_page_contains_gtm_script(
        self, rf, _site, seo_settings, normal_user, mock_page
    ):
        """非staffユーザーのページアクセスでGTMスクリプトがHTMLに含まれる。

        【目的】非staffユーザーのリクエストでseo_headをレンダリングし、
               GTM JavaScriptスニペットが正常に出力されることをもって、
               一般ユーザーのアクセス解析計測が有効であることを保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=False) -> seo_head tag -> _should_exclude_gtm
                    -> build_seo_context(gtm_container_id="GTM-TEST117") -> seo_head.html
        【テストデータ】
        - is_staff=Falseのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - テスト用ページオブジェクト
        【検証シナリオ】
        1. 非staffユーザーのリクエストでseo_headテンプレートタグをレンダリング
        2. 出力HTMLにGTM JavaScriptが含まれることを確認
        3. GTMコンテナIDが含まれることを確認
        """
        request = _build_request(rf, _site, normal_user)
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        assert GTM_JS_MARKER in html
        assert GTM_CONTAINER_ID in html

    @pytest.mark.django_db
    def test_anonymous_user_page_contains_gtm_script(
        self, rf, _site, seo_settings, mock_page
    ):
        """未ログインユーザーのページアクセスでGTMスクリプトがHTMLに含まれる。

        【目的】未ログイン（AnonymousUser）のリクエストでseo_headをレンダリングし、
               GTM JavaScriptスニペットが正常に出力されることをもって、
               匿名ユーザーのアクセス解析計測が有効であることを保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(AnonymousUser) -> seo_head tag -> _should_exclude_gtm
                    -> build_seo_context(gtm_container_id="GTM-TEST117") -> seo_head.html
        【テストデータ】
        - AnonymousUser（未認証）
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - テスト用ページオブジェクト
        【検証シナリオ】
        1. AnonymousUserのリクエストでseo_headテンプレートタグをレンダリング
        2. 出力HTMLにGTM JavaScriptが含まれることを確認
        3. GTMコンテナIDが含まれることを確認
        """
        request = _build_request(rf, _site, AnonymousUser())
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        assert GTM_JS_MARKER in html
        assert GTM_CONTAINER_ID in html


class TestSeoBodyGtmExclusionForStaff:
    """seo_body template tag excludes GTM noscript for staff users."""

    @pytest.mark.django_db
    def test_staff_user_page_does_not_contain_gtm_noscript(
        self, rf, _site, seo_settings, staff_user
    ):
        """staffユーザーのページアクセスでGTM noscriptがHTMLに含まれない。

        【目的】staffユーザーのリクエストでseo_bodyをレンダリングし、
               GTM noscriptフォールバックが出力されないことをもって、
               body側のGTM除外も正しく動作する要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=True) -> seo_body tag -> _should_exclude_gtm
                    -> render_to_string(gtm_container_id="") -> seo_body.html
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        【検証シナリオ】
        1. staffユーザーのリクエストでseo_bodyテンプレートタグをレンダリング
        2. 出力HTMLにGTM noscript iframeが含まれないことを確認
        """
        request = _build_request(rf, _site, staff_user)
        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})

        html = template.render(context)

        assert GTM_NS_MARKER not in html
        assert GTM_CONTAINER_ID not in html

    @pytest.mark.django_db
    def test_non_staff_user_page_contains_gtm_noscript(
        self, rf, _site, seo_settings, normal_user
    ):
        """非staffユーザーのページアクセスでGTM noscriptがHTMLに含まれる。

        【目的】非staffユーザーのリクエストでseo_bodyをレンダリングし、
               GTM noscriptフォールバックが正常に出力されることをもって、
               一般ユーザーのbody側GTM計測が有効であることを保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=False) -> seo_body tag -> _should_exclude_gtm
                    -> render_to_string(gtm_container_id="GTM-TEST117") -> seo_body.html
        【テストデータ】
        - is_staff=Falseのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        【検証シナリオ】
        1. 非staffユーザーのリクエストでseo_bodyテンプレートタグをレンダリング
        2. 出力HTMLにGTM noscript iframeが含まれることを確認
        """
        request = _build_request(rf, _site, normal_user)
        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})

        html = template.render(context)

        assert GTM_NS_MARKER in html
        assert GTM_CONTAINER_ID in html

    @pytest.mark.django_db
    def test_anonymous_user_page_contains_gtm_noscript(self, rf, _site, seo_settings):
        """未ログインユーザーのページアクセスでGTM noscriptがHTMLに含まれる。

        【目的】未ログイン（AnonymousUser）のリクエストでseo_bodyをレンダリングし、
               GTM noscriptフォールバックが正常に出力されることをもって、
               匿名ユーザーのbody側GTM計測が有効であることを保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(AnonymousUser) -> seo_body tag -> _should_exclude_gtm
                    -> render_to_string(gtm_container_id="GTM-TEST117") -> seo_body.html
        【テストデータ】
        - AnonymousUser（未認証）
        - gtm_container_id="GTM-TEST117"のSEOSettings
        【検証シナリオ】
        1. AnonymousUserのリクエストでseo_bodyテンプレートタグをレンダリング
        2. 出力HTMLにGTM noscript iframeが含まれることを確認
        """
        request = _build_request(rf, _site, AnonymousUser())
        template = Template("{% load wagtail_herald %}{% seo_body %}")
        context = Context({"request": request})

        html = template.render(context)

        assert GTM_NS_MARKER in html
        assert GTM_CONTAINER_ID in html


class TestStaffUserSeoTagsIntact:
    """Staff user GTM exclusion does not affect other SEO tags."""

    @pytest.mark.django_db
    def test_staff_user_meta_tags_and_og_tags_still_rendered(
        self, rf, _site, seo_settings, staff_user, mock_page
    ):
        """staffユーザーでもメタタグ・OGタグは正常に出力される。

        【目的】staffユーザーのリクエストでseo_headをレンダリングし、
               GTMのみが除外され、title・description・OGタグ等の
               SEOメタデータは正常に出力されることをもって、
               GTM除外がSEO出力全体に影響しない要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=True) -> seo_head tag -> build_seo_context
                    -> seo_head.html (GTM excluded, meta tags intact)
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - title="Test Page", description="Test page description"のページ
        【検証シナリオ】
        1. staffユーザーのリクエストでseo_headテンプレートタグをレンダリング
        2. GTMスクリプトが含まれないことを確認
        3. <title>タグにページタイトルが含まれることを確認
        4. descriptionメタタグが含まれることを確認
        5. OGタグ（og:type, og:title）が含まれることを確認
        """
        request = _build_request(rf, _site, staff_user)
        template = Template("{% load wagtail_herald %}{% seo_head %}")
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        assert GTM_JS_MARKER not in html
        assert GTM_CONTAINER_ID not in html

        assert "<title>" in html
        assert "Test Page" in html
        assert 'name="description"' in html
        assert "Test page description" in html
        assert 'property="og:type"' in html
        assert 'property="og:title"' in html


class TestSeoHeadAndBodyGtmConsistency:
    """seo_head and seo_body GTM exclusion behavior is consistent."""

    @pytest.mark.django_db
    def test_staff_both_head_and_body_exclude_gtm(
        self, rf, _site, seo_settings, staff_user, mock_page
    ):
        """staffユーザーではseo_headとseo_bodyの両方でGTMが除外される。

        【目的】staffユーザーのリクエストでseo_headとseo_bodyを同時にレンダリングし、
               head側のGTMスクリプトとbody側のGTM noscriptの両方が除外される
               ことをもって、GTM除外がhead/bodyの両方で一貫して動作する要件を保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=True) -> seo_head + seo_body tags
                    -> _should_exclude_gtm -> both templates exclude GTM
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - テスト用ページオブジェクト
        【検証シナリオ】
        1. staffユーザーのリクエストでseo_headとseo_bodyを同時レンダリング
        2. head側にGTM JavaScriptが含まれないことを確認
        3. body側にGTM noscriptが含まれないことを確認
        """
        request = _build_request(rf, _site, staff_user)
        template = Template(
            "{% load wagtail_herald %}{% seo_head %}<!-- sep -->{% seo_body %}"
        )
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        assert GTM_JS_MARKER not in html
        assert GTM_NS_MARKER not in html
        assert GTM_CONTAINER_ID not in html

    @pytest.mark.django_db
    def test_non_staff_both_head_and_body_contain_gtm(
        self, rf, _site, seo_settings, normal_user, mock_page
    ):
        """非staffユーザーではseo_headとseo_bodyの両方でGTMが出力される。

        【目的】非staffユーザーのリクエストでseo_headとseo_bodyを同時にレンダリングし、
               head側のGTMスクリプトとbody側のGTM noscriptの両方が出力される
               ことをもって、一般ユーザーのGTM計測が完全に有効であることを保証する
        【種別】正常系
        【技法】APIエンドポイント（Djangoテンプレートレンダリングパイプライン）
        【連携対象】request(is_staff=False) -> seo_head + seo_body tags
                    -> _should_exclude_gtm -> both templates include GTM
        【テストデータ】
        - is_staff=Falseのユーザー
        - gtm_container_id="GTM-TEST117"のSEOSettings
        - テスト用ページオブジェクト
        【検証シナリオ】
        1. 非staffユーザーのリクエストでseo_headとseo_bodyを同時レンダリング
        2. head側にGTM JavaScriptが含まれることを確認
        3. body側にGTM noscriptが含まれることを確認
        """
        request = _build_request(rf, _site, normal_user)
        template = Template(
            "{% load wagtail_herald %}{% seo_head %}<!-- sep -->{% seo_body %}"
        )
        context = Context({"request": request, "page": mock_page})

        html = template.render(context)

        head_part, body_part = html.split("<!-- sep -->")
        assert GTM_JS_MARKER in head_part
        assert GTM_CONTAINER_ID in head_part
        assert GTM_NS_MARKER in body_part
        assert GTM_CONTAINER_ID in body_part
