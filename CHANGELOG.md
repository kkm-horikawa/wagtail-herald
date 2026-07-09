# Changelog

## Unreleased

- **Breaking**: GTM headスニペットのテキスト構造が変わりました。Content-Security-Policy で `script-src 'sha256-...'` のようなハッシュ許可リストを使用している場合は、このインラインスクリプトのハッシュ値を再計算してください。
