
# 注意事項
- flask_loginをimportする際はmodelsでload_userを定義しないとtemplatesが読み込まれない
- postgresqlを使う際は、create databaseとdb.create_all()はコマンドで実行する必要がある
- herokuでPostgreSQLを使う場合はアドオンをインストールしてURIを変更する必要がある


# 機能要件
- ログイン機能
- ユーザ情報編集機能
- ユーザ検索機能
- 友達申請、削除機能
- メッセージ送信機能
- 非同期通信機能

以下は後日実装予定
- OAuthによるSSO機能
- クレジット支払機能
- 単体テスト機能

