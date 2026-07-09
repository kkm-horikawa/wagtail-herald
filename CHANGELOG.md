# Changelog

## Unreleased

- **Breaking**: GTM headスニペットのテキスト構造が変わりました。Content-Security-Policy で `script-src 'sha256-...'` のようなハッシュ許可リストを使用している場合は、このインラインスクリプトのハッシュ値を再計算してください。
- **BREAKING CHANGE**: `gtm_server_container_url` の意味を変更しました。v0.12.0 では「ホスト名」を指定していましたが、v0.13.0 では「完全な配信パスのURL」を指定してください。例: 旧形式 `https://your-domain.com` -> 新形式 `https://your-domain.com/aBcDeFgHiJ/`。また、`noscript` iframe は常に `https://www.googletagmanager.com/ns.html` を指すようになりました。v0.12.0 で `gtm_server_container_url` を設定していた場合も、server URL が使われるのは head の script のみです。
