"""IndexNow通知・シグナル・キーファイルビューのユニットテスト。

notify_indexnow()、handle_page_published()、indexnow_key_file()の
ビジネスロジックを全てモックベースで検証する。
"""

import json
from unittest import mock
from urllib.error import URLError

import pytest
from django.http import Http404

from wagtail_herald.indexnow import (
    INDEXNOW_ENDPOINT,
    INDEXNOW_TIMEOUT_SECONDS,
    _send_indexnow,
    notify_indexnow,
)
from wagtail_herald.signals import handle_page_published, register_signals
from wagtail_herald.views import indexnow_key_file


class TestNotifyIndexnow:
    """notify_indexnow()のテスト（スレッド起動とガード条件）。"""

    def test_starts_daemon_thread_with_correct_args(self):
        """有効なページとapi_keyで、バックグラウンドスレッドが起動される。

        【目的】notify_indexnowがdaemonスレッドを起動して_send_indexnowに
               正しい引数を渡すことをもって、非ブロッキング通知要件を保証する
        【種別】正常系テスト
        【対象】notify_indexnow(page, api_key)
        【技法】同値分割
        【テストデータ】有効なfull_urlを持つページと有効なapi_key
        """
        page = mock.Mock()
        page.full_url = "https://example.com/blog/my-post/"

        with mock.patch("wagtail_herald.indexnow.threading.Thread") as mock_thread:
            notify_indexnow(page, "abc123def456")

            mock_thread.assert_called_once_with(
                target=_send_indexnow,
                args=("https://example.com/blog/my-post/", "abc123def456"),
                daemon=True,
            )
            mock_thread.return_value.start.assert_called_once()

    def test_empty_api_key_does_nothing(self):
        """api_keyが空文字の場合はスレッドを起動せず早期リターンする。

        【目的】api_keyが空文字のときスレッドが起動しないことをもって、
               未設定時の不要な処理防止要件を保証する
        【種別】エッジケーステスト
        【対象】notify_indexnow(page, api_key)
        【技法】境界値分析（空文字境界）
        【テストデータ】空文字のapi_key
        """
        page = mock.Mock()

        with mock.patch("wagtail_herald.indexnow.threading.Thread") as mock_thread:
            notify_indexnow(page, "")

            mock_thread.assert_not_called()

    def test_none_api_key_does_nothing(self):
        """api_keyがNoneの場合はスレッドを起動せず早期リターンする。

        【目的】api_keyがNoneのときスレッドが起動しないことをもって、
               未設定時の不要な処理防止要件を保証する
        【種別】エッジケーステスト
        【対象】notify_indexnow(page, api_key)
        【技法】境界値分析（None境界）
        【テストデータ】Noneのapi_key
        """
        page = mock.Mock()

        with mock.patch("wagtail_herald.indexnow.threading.Thread") as mock_thread:
            notify_indexnow(page, None)

            mock_thread.assert_not_called()

    def test_none_full_url_does_nothing(self):
        """page.full_urlがNoneの場合はスレッドを起動せず早期リターンする。

        【目的】full_urlがNoneのときスレッドが起動しないことをもって、
               URLなしページの安全なスキップ要件を保証する
        【種別】エッジケーステスト
        【対象】notify_indexnow(page, api_key)
        【技法】境界値分析（None境界）
        【テストデータ】full_url=Noneのページ
        """
        page = mock.Mock()
        page.full_url = None

        with mock.patch("wagtail_herald.indexnow.threading.Thread") as mock_thread:
            notify_indexnow(page, "validkey")

            mock_thread.assert_not_called()


class TestSendIndexnow:
    """_send_indexnow()のテスト（HTTP送信ロジック）。"""

    def test_sends_post_with_correct_payload(self):
        """正しいペイロードでIndexNow APIにPOSTリクエストを送信する。

        【目的】_send_indexnowが正しいhost・key・keyLocation・urlListを含む
               JSONペイロードでPOSTすることをもって、IndexNow API連携要件を保証する
        【種別】正常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】同値分割
        【テストデータ】有効なpage_urlと有効なapi_key
        """
        with mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock.Mock(status=200)

            _send_indexnow("https://example.com/blog/my-post/", "abc123def456")

            mock_urlopen.assert_called_once()
            req = mock_urlopen.call_args[0][0]
            assert req.full_url == INDEXNOW_ENDPOINT
            assert req.method == "POST"
            assert req.get_header("Content-type") == "application/json"

            payload = json.loads(req.data.decode())
            assert payload["host"] == "example.com"
            assert payload["key"] == "abc123def456"
            assert payload["keyLocation"] == "https://example.com/abc123def456.txt"
            assert payload["urlList"] == ["https://example.com/blog/my-post/"]

    def test_uses_configured_timeout(self):
        """urlopen呼び出しに設定済みのタイムアウト値が使われる。

        【目的】_send_indexnowがINDEXNOW_TIMEOUT_SECONDSのタイムアウトで
               urlopen を呼ぶことをもって、タイムアウト設定要件を保証する
        【種別】正常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】同値分割
        【テストデータ】有効なpage_urlとapi_key
        """
        with mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock.Mock(status=200)

            _send_indexnow("https://example.com/page/", "testkey")

            _, kwargs = mock_urlopen.call_args
            assert kwargs["timeout"] == INDEXNOW_TIMEOUT_SECONDS

    def test_url_error_logs_warning_without_crash(self):
        """URLError発生時にwarningログを出力しクラッシュしない。

        【目的】URLError時に_send_indexnowがクラッシュしないことをもって、
               ネットワークエラーへの耐障害性要件を保証する
        【種別】異常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】エラー推測
        【テストデータ】URLErrorを発生させるモック
        """
        with (
            mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen,
            mock.patch("wagtail_herald.indexnow.logger") as mock_logger,
        ):
            mock_urlopen.side_effect = URLError("Connection refused")

            _send_indexnow("https://example.com/page/", "testkey")

            mock_logger.warning.assert_called_once()
            assert "example.com/page/" in mock_logger.warning.call_args[0][1]

    def test_os_error_logs_warning_without_crash(self):
        """OSError（タイムアウト等）発生時にwarningログを出力しクラッシュしない。

        【目的】OSError時に_send_indexnowがクラッシュしないことをもって、
               タイムアウト等の予期せぬエラーへの耐障害性要件を保証する
        【種別】異常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】エラー推測
        【テストデータ】OSErrorを発生させるモック
        """
        with (
            mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen,
            mock.patch("wagtail_herald.indexnow.logger") as mock_logger,
        ):
            mock_urlopen.side_effect = OSError("Connection timed out")

            _send_indexnow("https://example.com/page/", "testkey")

            mock_logger.warning.assert_called_once()

    def test_successful_response_logs_info(self):
        """正常レスポンス時にinfoログを出力する。

        【目的】正常時に_send_indexnowがinfoログを出力することをもって、
               通知成功の監視・追跡要件を保証する
        【種別】正常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】同値分割
        【テストデータ】status=200のレスポンス
        """
        with (
            mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen,
            mock.patch("wagtail_herald.indexnow.logger") as mock_logger,
        ):
            mock_urlopen.return_value = mock.Mock(status=200)

            _send_indexnow("https://example.com/page/", "testkey")

            mock_logger.info.assert_called_once()
            assert "example.com/page/" in mock_logger.info.call_args[0][1]

    def test_host_extracted_from_full_url(self):
        """page_urlからホスト名が正しく抽出される。

        【目的】サブドメイン付きURLからhostが正しく抽出されることをもって、
               多様なURL形式への対応要件を保証する
        【種別】正常系テスト
        【対象】_send_indexnow(page_url, api_key)
        【技法】同値分割
        【テストデータ】サブドメイン付きURL
        """
        with mock.patch("wagtail_herald.indexnow.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock.Mock(status=200)

            _send_indexnow("https://blog.example.com/post/", "mykey")

            req = mock_urlopen.call_args[0][0]
            payload = json.loads(req.data.decode())
            assert payload["host"] == "blog.example.com"
            assert payload["keyLocation"] == "https://blog.example.com/mykey.txt"


class TestHandlePagePublished:
    """handle_page_published()のテスト。"""

    def test_calls_notify_when_api_key_configured(self):
        """api_key設定済みの場合にnotify_indexnowを呼び出す。

        【目的】api_keyが設定されたサイトでページ公開時にnotify_indexnowが
               呼ばれることをもって、IndexNow自動通知要件を保証する
        【種別】正常系テスト
        【対象】handle_page_published(sender, instance, **kwargs)
        【技法】同値分割
        【テストデータ】indexnow_api_key設定済みのSEOSettings
        """
        mock_site = mock.Mock()
        mock_settings = mock.Mock()
        mock_settings.indexnow_api_key = "test-api-key"

        page = mock.Mock()
        page.get_site.return_value = mock_site

        with (
            mock.patch("wagtail_herald.models.settings.SEOSettings") as mock_seo_cls,
            mock.patch("wagtail_herald.signals.notify_indexnow") as mock_notify,
        ):
            mock_seo_cls.for_site.return_value = mock_settings

            handle_page_published(sender=mock.Mock(), instance=page)

            mock_notify.assert_called_once_with(page, "test-api-key")

    def test_does_not_call_notify_when_api_key_empty(self):
        """api_keyが空の場合はnotify_indexnowを呼ばない。

        【目的】api_keyが空のときnotify_indexnowが呼ばれないことをもって、
               未設定サイトの不要な通知防止要件を保証する
        【種別】エッジケーステスト
        【対象】handle_page_published(sender, instance, **kwargs)
        【技法】境界値分析（空文字境界）
        【テストデータ】indexnow_api_key=""のSEOSettings
        """
        mock_site = mock.Mock()
        mock_settings = mock.Mock()
        mock_settings.indexnow_api_key = ""

        page = mock.Mock()
        page.get_site.return_value = mock_site

        with (
            mock.patch("wagtail_herald.models.settings.SEOSettings") as mock_seo_cls,
            mock.patch("wagtail_herald.signals.notify_indexnow") as mock_notify,
        ):
            mock_seo_cls.for_site.return_value = mock_settings

            handle_page_published(sender=mock.Mock(), instance=page)

            mock_notify.assert_not_called()

    def test_raises_attribute_error_when_api_key_attribute_missing(self):
        """SEOSettingsにindexnow_api_key属性がない場合はAttributeErrorが発生する。

        【目的】直接属性アクセスを使用しているため、属性がなければ
               AttributeErrorとなることを明示的に文書化する
        【種別】異常系テスト
        【対象】handle_page_published(sender, instance, **kwargs)
        【技法】エラー推測
        【テストデータ】indexnow_api_key属性を持たないSEOSettings
        """
        mock_site = mock.Mock()
        mock_settings = mock.Mock(spec=[])

        page = mock.Mock()
        page.get_site.return_value = mock_site

        with mock.patch("wagtail_herald.models.settings.SEOSettings") as mock_seo_cls:
            mock_seo_cls.for_site.return_value = mock_settings

            with pytest.raises(AttributeError):
                handle_page_published(sender=mock.Mock(), instance=page)

    def test_handles_get_site_exception_gracefully(self):
        """get_site()が例外を投げた場合にクラッシュしない。

        【目的】get_site()の例外時にハンドラがクラッシュしないことをもって、
               孤立ページ等の異常状態への耐障害性要件を保証する
        【種別】異常系テスト
        【対象】handle_page_published(sender, instance, **kwargs)
        【技法】エラー推測
        【テストデータ】get_site()がExceptionを発生させるページ
        """
        page = mock.Mock()
        page.get_site.side_effect = Exception("No site found")

        with mock.patch("wagtail_herald.signals.notify_indexnow") as mock_notify:
            handle_page_published(sender=mock.Mock(), instance=page)

            mock_notify.assert_not_called()

    def test_handles_get_site_returns_none(self):
        """get_site()がNoneを返す場合にクラッシュしない。

        【目的】get_site()がNoneを返す場合にハンドラがクラッシュしないことをもって、
               サイト未関連付けページの安全なスキップ要件を保証する
        【種別】エッジケーステスト
        【対象】handle_page_published(sender, instance, **kwargs)
        【技法】境界値分析（None境界）
        【テストデータ】get_site()がNoneを返すページ
        """
        page = mock.Mock()
        page.get_site.return_value = None

        with mock.patch("wagtail_herald.signals.notify_indexnow") as mock_notify:
            handle_page_published(sender=mock.Mock(), instance=page)

            mock_notify.assert_not_called()


class TestRegisterSignals:
    """register_signals()のテスト。"""

    def test_connects_handler_to_page_published(self):
        """page_publishedシグナルにハンドラを接続する。

        【目的】register_signals()がpage_published.connectを呼ぶことをもって、
               シグナル登録要件を保証する
        【種別】正常系テスト
        【対象】register_signals()
        【技法】同値分割
        【テストデータ】なし
        """
        with mock.patch("wagtail_herald.signals.page_published") as mock_signal:
            register_signals()

            mock_signal.connect.assert_called_once_with(handle_page_published)


class TestIndexnowKeyFileView:
    """indexnow_key_file()ビューのテスト。"""

    def test_returns_key_with_text_plain_when_key_matches(self, rf):
        """api_keyが一致する場合、text/plainでキー文字列を返す。

        【目的】URLパスのkeyとSEOSettings.indexnow_api_keyが一致するとき
               キー文字列をtext/plainで返すことをもって、IndexNowドメイン所有権
               検証要件を保証する
        【種別】正常系テスト
        【対象】indexnow_key_file(request, key)
        【技法】同値分割
        【テストデータ】一致するapi_key
        """
        mock_settings = mock.Mock()
        mock_settings.indexnow_api_key = "abc123def456"
        mock_site = mock.Mock()

        request = rf.get("/abc123def456.txt")
        request.site = mock_site

        with (
            mock.patch("wagtail_herald.views.Site.find_for_request") as mock_find,
            mock.patch(
                "wagtail_herald.views.SEOSettings.for_request"
            ) as mock_for_request,
        ):
            mock_find.return_value = mock_site
            mock_for_request.return_value = mock_settings

            response = indexnow_key_file(request, "abc123def456")

            assert response.status_code == 200
            assert response["Content-Type"] == "text/plain"
            assert response.content.decode() == "abc123def456"

    def test_returns_404_when_api_key_not_configured(self, rf):
        """api_keyが未設定の場合に404を返す。

        【目的】indexnow_api_keyが空のときHttp404を返すことをもって、
               未設定サイトでキーファイルが公開されない要件を保証する
        【種別】異常系テスト
        【対象】indexnow_key_file(request, key)
        【技法】境界値分析（空文字境界）
        【テストデータ】indexnow_api_key=""のSEOSettings
        """
        mock_settings = mock.Mock()
        mock_settings.indexnow_api_key = ""
        mock_site = mock.Mock()

        request = rf.get("/somekey.txt")
        request.site = mock_site

        with (
            mock.patch("wagtail_herald.views.Site.find_for_request") as mock_find,
            mock.patch(
                "wagtail_herald.views.SEOSettings.for_request"
            ) as mock_for_request,
        ):
            mock_find.return_value = mock_site
            mock_for_request.return_value = mock_settings

            with pytest.raises(Http404):
                indexnow_key_file(request, "somekey")

    def test_returns_404_when_key_does_not_match(self, rf):
        """URLパスのkeyとsettingsのkeyが一致しない場合に404を返す。

        【目的】不一致のキーでHttp404を返すことをもって、他サイトの
               キーファイル偽装防止要件を保証する
        【種別】異常系テスト
        【対象】indexnow_key_file(request, key)
        【技法】同値分割
        【テストデータ】異なるkeyの組み合わせ
        """
        mock_settings = mock.Mock()
        mock_settings.indexnow_api_key = "correct-key"
        mock_site = mock.Mock()

        request = rf.get("/wrong-key.txt")
        request.site = mock_site

        with (
            mock.patch("wagtail_herald.views.Site.find_for_request") as mock_find,
            mock.patch(
                "wagtail_herald.views.SEOSettings.for_request"
            ) as mock_for_request,
        ):
            mock_find.return_value = mock_site
            mock_for_request.return_value = mock_settings

            with pytest.raises(Http404):
                indexnow_key_file(request, "wrong-key")

    def test_returns_404_when_no_site(self, rf):
        """サイトが見つからない場合に404を返す。

        【目的】Site.find_for_requestがNoneを返すときHttp404となることをもって、
               未管理ドメインでのキーファイル非公開要件を保証する
        【種別】異常系テスト
        【対象】indexnow_key_file(request, key)
        【技法】エラー推測
        【テストデータ】Site.find_for_requestがNoneを返すリクエスト
        """
        request = rf.get("/somekey.txt")

        with mock.patch("wagtail_herald.views.Site.find_for_request") as mock_find:
            mock_find.return_value = None

            with pytest.raises(Http404):
                indexnow_key_file(request, "somekey")

    def test_returns_404_when_seo_settings_is_none(self, rf):
        """SEOSettings.for_requestがNoneを返す場合に404を返す。

        【目的】SEOSettingsが存在しないサイトでHttp404となることをもって、
               設定未作成サイトの安全なハンドリング要件を保証する
        【種別】エッジケーステスト
        【対象】indexnow_key_file(request, key)
        【技法】エラー推測
        【テストデータ】SEOSettings.for_requestがNoneを返すサイト
        """
        mock_site = mock.Mock()
        request = rf.get("/somekey.txt")
        request.site = mock_site

        with (
            mock.patch("wagtail_herald.views.Site.find_for_request") as mock_find,
            mock.patch(
                "wagtail_herald.views.SEOSettings.for_request"
            ) as mock_for_request,
        ):
            mock_find.return_value = mock_site
            mock_for_request.return_value = None

            with pytest.raises(Http404):
                indexnow_key_file(request, "somekey")
