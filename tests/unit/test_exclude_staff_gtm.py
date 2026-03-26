"""管理者ユーザーのGTM除外テスト (#117)

管理者(is_staff=True)のページビューがGTMで計測されると、アクセス解析データが
汚染される。staffユーザーに対してGTMコンテナIDを空にすることで除外する。

## デシジョンテーブル: DT-SHOULD-EXCLUDE-GTM

| ID  | request | user   | is_staff | 期待結果 |
|-----|---------|--------|----------|----------|
| DT1 | None    | -      | -        | False    |
| DT2 | あり    | None   | -        | False    |
| DT3 | あり    | あり   | False    | False    |
| DT4 | あり    | あり   | True     | True     |
| DT5 | あり    | あり   | 属性なし | False    |

## デシジョンテーブル: DT-BUILD-SEO-CONTEXT-GTM

| ID  | is_staff | settings.gtm_container_id | 期待 gtm_container_id |
|-----|----------|---------------------------|----------------------|
| BC1 | True     | "GTM-XXXXX"              | ""                   |
| BC2 | False    | "GTM-XXXXX"              | "GTM-XXXXX"          |
| BC3 | (なし)   | "GTM-XXXXX"              | "GTM-XXXXX"          |

## デシジョンテーブル: DT-SEO-BODY-GTM

| ID  | is_staff | settings.gtm_container_id | 期待 gtm_container_id |
|-----|----------|---------------------------|----------------------|
| SB1 | True     | "GTM-XXXXX"              | ""                   |
| SB2 | False    | "GTM-XXXXX"              | "GTM-XXXXX"          |
"""

from __future__ import annotations

from unittest import mock

import pytest

from wagtail_herald.templatetags.wagtail_herald import (
    _should_exclude_gtm,
    build_seo_context,
    seo_body,
)


class TestShouldExcludeGtm:
    """_should_exclude_gtm() のユニットテスト。"""

    def test_should_exclude_gtm_with_none_request_returns_false(self):
        """requestがNoneの場合Falseを返すことを確認する。

        【目的】_should_exclude_gtm()にNoneを与え、Falseが返却されることを
               もって、テンプレートタグがrequest無しで呼ばれた場合の安全性を保証する
        【種別】エッジケース
        【対象】_should_exclude_gtm(request)
        【技法】同値分割（DT1参照）
        【テストデータ】request=None
        """
        result = _should_exclude_gtm(None)

        assert result is False

    def test_should_exclude_gtm_with_no_user_returns_false(self):
        """requestにuserが無い場合Falseを返すことを確認する。

        【目的】_should_exclude_gtm()にuser属性を持たないrequestを与え、
               Falseが返却されることをもって、ミドルウェア未適用時の安全性を保証する
        【種別】エッジケース
        【対象】_should_exclude_gtm(request)
        【技法】同値分割（DT2参照）
        【テストデータ】user属性を持たないrequestオブジェクト
        """
        request = mock.Mock(spec=[])

        result = _should_exclude_gtm(request)

        assert result is False

    def test_should_exclude_gtm_with_none_user_returns_false(self):
        """request.userがNoneの場合Falseを返すことを確認する。

        【目的】_should_exclude_gtm()にuser=Noneのrequestを与え、Falseが
               返却されることをもって、未認証状態の安全性を保証する
        【種別】エッジケース
        【対象】_should_exclude_gtm(request)
        【技法】同値分割（DT2参照）
        【テストデータ】request.user=None
        """
        request = mock.Mock()
        request.user = None

        result = _should_exclude_gtm(request)

        assert result is False

    def test_should_exclude_gtm_with_non_staff_user_returns_false(self):
        """非staffユーザーの場合Falseを返すことを確認する。

        【目的】_should_exclude_gtm()にis_staff=Falseのユーザーを与え、
               Falseが返却されることをもって、一般ユーザーのGTM計測が有効であることを保証する
        【種別】正常系テスト
        【対象】_should_exclude_gtm(request)
        【技法】同値分割（DT3参照）
        【テストデータ】is_staff=Falseのユーザー
        """
        request = mock.Mock()
        request.user = mock.Mock(is_staff=False)

        result = _should_exclude_gtm(request)

        assert result is False

    def test_should_exclude_gtm_with_staff_user_returns_true(self):
        """staffユーザーの場合Trueを返すことを確認する。

        【目的】_should_exclude_gtm()にis_staff=Trueのユーザーを与え、
               Trueが返却されることをもって、管理者のGTM除外要件を保証する
        【種別】正常系テスト
        【対象】_should_exclude_gtm(request)
        【技法】同値分割（DT4参照）
        【テストデータ】is_staff=Trueのユーザー
        """
        request = mock.Mock()
        request.user = mock.Mock(is_staff=True)

        result = _should_exclude_gtm(request)

        assert result is True

    def test_should_exclude_gtm_with_user_without_is_staff_attr_returns_false(self):
        """userにis_staff属性がない場合Falseを返すことを確認する。

        【目的】_should_exclude_gtm()にis_staff属性を持たないuserオブジェクトを与え、
               Falseが返却されることをもって、カスタムユーザーモデルの互換性を保証する
        【種別】エッジケース
        【対象】_should_exclude_gtm(request)
        【技法】エラー推測（DT5参照）
        【テストデータ】is_staff属性を持たないuserオブジェクト
        """
        request = mock.Mock()
        request.user = mock.Mock(spec=[])

        result = _should_exclude_gtm(request)

        assert result is False


class TestBuildSeoContextGtmExclusion:
    """build_seo_context() でのGTM除外テスト。"""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_build_seo_context_staff_user_excludes_gtm(self, _mock_site):
        """staffユーザーの場合gtm_container_idが空になることを確認する。

        【目的】build_seo_context()にis_staff=Trueのrequestを与え、
               gtm_container_idが空文字になることをもって、
               staffユーザーのGTMタグ出力抑制要件を保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings, overrides)
        【技法】デシジョンテーブル（BC1参照）
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-XXXXX"のSEOSettings
        """
        request = mock.Mock()
        request.user = mock.Mock(is_staff=True)
        settings = mock.Mock()
        settings.gtm_container_id = "GTM-XXXXX"

        settings.twitter_handle = ""
        settings.custom_head_html = ""
        settings.default_og_image = None
        settings.default_locale = "en_US"
        settings.favicon_svg = None
        settings.favicon_png = None
        settings.apple_touch_icon = None

        result = build_seo_context(request, None, settings)

        assert result["gtm_container_id"] == ""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_build_seo_context_non_staff_user_keeps_gtm(self, _mock_site):
        """非staffユーザーの場合gtm_container_idが設定値のままであることを確認する。

        【目的】build_seo_context()にis_staff=Falseのrequestを与え、
               gtm_container_idが設定値のままであることをもって、
               一般ユーザーのGTM計測が正常に動作することを保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings, overrides)
        【技法】デシジョンテーブル（BC2参照）
        【テストデータ】
        - is_staff=Falseのユーザー
        - gtm_container_id="GTM-XXXXX"のSEOSettings
        """
        request = mock.Mock()
        request.user = mock.Mock(is_staff=False)
        settings = mock.Mock()
        settings.gtm_container_id = "GTM-XXXXX"

        settings.twitter_handle = ""
        settings.custom_head_html = ""
        settings.default_og_image = None
        settings.default_locale = "en_US"
        settings.favicon_svg = None
        settings.favicon_png = None
        settings.apple_touch_icon = None

        result = build_seo_context(request, None, settings)

        assert result["gtm_container_id"] == "GTM-XXXXX"

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.Site.find_for_request",
        return_value=None,
    )
    def test_build_seo_context_anonymous_user_keeps_gtm(self, _mock_site):
        """未ログインユーザー(AnonymousUser相当)の場合gtm_container_idが設定値のままであることを確認する。

        【目的】build_seo_context()にis_staff=Falseの匿名ユーザーを与え、
               gtm_container_idが設定値のままであることをもって、
               匿名ユーザーのGTM計測が正常に動作することを保証する
        【種別】正常系テスト
        【対象】build_seo_context(request, page, settings, overrides)
        【技法】デシジョンテーブル（BC3参照）
        【テストデータ】
        - is_staff=Falseの匿名ユーザー（AnonymousUser相当）
        - gtm_container_id="GTM-XXXXX"のSEOSettings
        """
        anonymous_user = mock.Mock(is_staff=False, is_authenticated=False)
        request = mock.Mock()
        request.user = anonymous_user
        settings = mock.Mock()
        settings.gtm_container_id = "GTM-XXXXX"

        settings.twitter_handle = ""
        settings.custom_head_html = ""
        settings.default_og_image = None
        settings.default_locale = "en_US"
        settings.favicon_svg = None
        settings.favicon_png = None
        settings.apple_touch_icon = None

        result = build_seo_context(request, None, settings)

        assert result["gtm_container_id"] == "GTM-XXXXX"


class TestSeoBodyGtmExclusion:
    """seo_body() でのGTM除外テスト。"""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.render_to_string",
        return_value="",
    )
    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.get_seo_settings",
    )
    def test_seo_body_staff_user_excludes_gtm(self, mock_get_settings, mock_render):
        """staffユーザーの場合seo_bodyのgtm_container_idが空になることを確認する。

        【目的】seo_body()にis_staff=Trueのrequestを持つcontextを与え、
               render_to_stringに渡されるgtm_container_idが空文字であることをもって、
               body内GTMノーscriptタグの出力抑制要件を保証する
        【種別】正常系テスト
        【対象】seo_body(context)
        【技法】デシジョンテーブル（SB1参照）
        【テストデータ】
        - is_staff=Trueのユーザー
        - gtm_container_id="GTM-XXXXX"のSEOSettings
        """
        staff_user = mock.Mock(is_staff=True)
        request = mock.Mock()
        request.user = staff_user
        settings = mock.Mock()
        settings.gtm_container_id = "GTM-XXXXX"
        settings.custom_body_end_html = ""
        mock_get_settings.return_value = settings
        context = {"request": request}

        seo_body(context)

        rendered_context = mock_render.call_args[0][1]
        assert rendered_context["gtm_container_id"] == ""

    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.render_to_string",
        return_value="",
    )
    @mock.patch(
        "wagtail_herald.templatetags.wagtail_herald.get_seo_settings",
    )
    def test_seo_body_non_staff_user_keeps_gtm(self, mock_get_settings, mock_render):
        """非staffユーザーの場合seo_bodyのgtm_container_idが設定値のままであることを確認する。

        【目的】seo_body()にis_staff=Falseのrequestを持つcontextを与え、
               render_to_stringに渡されるgtm_container_idが設定値のままであることをもって、
               一般ユーザーのbody内GTMノーscriptタグが正常出力されることを保証する
        【種別】正常系テスト
        【対象】seo_body(context)
        【技法】デシジョンテーブル（SB2参照）
        【テストデータ】
        - is_staff=Falseのユーザー
        - gtm_container_id="GTM-XXXXX"のSEOSettings
        """
        non_staff_user = mock.Mock(is_staff=False)
        request = mock.Mock()
        request.user = non_staff_user
        settings = mock.Mock()
        settings.gtm_container_id = "GTM-XXXXX"
        settings.custom_body_end_html = ""
        mock_get_settings.return_value = settings
        context = {"request": request}

        seo_body(context)

        rendered_context = mock_render.call_args[0][1]
        assert rendered_context["gtm_container_id"] == "GTM-XXXXX"


class TestShouldExcludeGtmParametrized:
    """_should_exclude_gtm() のパラメタライズドテスト。"""

    @pytest.mark.parametrize(
        "request_obj,expected",
        [
            pytest.param(None, False, id="DT1-request-none"),
            pytest.param(
                mock.Mock(**{"user": None}),
                False,
                id="DT2-user-none",
            ),
            pytest.param(
                mock.Mock(**{"user": mock.Mock(is_staff=False)}),
                False,
                id="DT3-non-staff",
            ),
            pytest.param(
                mock.Mock(**{"user": mock.Mock(is_staff=True)}),
                True,
                id="DT4-staff",
            ),
            pytest.param(
                mock.Mock(**{"user": mock.Mock(spec=[])}),
                False,
                id="DT5-no-is-staff-attr",
            ),
        ],
    )
    def test_should_exclude_gtm_decision_table(self, request_obj, expected):
        """DT-SHOULD-EXCLUDE-GTM参照。

        【目的】_should_exclude_gtm()の全条件パターンを一括検証し、
               GTM除外判定ロジックの網羅性を保証する
        【種別】正常系テスト
        【対象】_should_exclude_gtm(request)
        【技法】デシジョンテーブル
        【テストデータ】DT-SHOULD-EXCLUDE-GTMの全パターン
        """
        result = _should_exclude_gtm(request_obj)

        assert result is expected
